#!/usr/bin/env python3
"""
clean_confluence_pdf.py
=======================

Clean a Confluence-exported PDF and emit a tidy Markdown file that is ready
for ingestion into Amazon Q (Business). Markdown is used as the output format
because it expresses document structure (headers, links, image references)
explicitly and is one of Amazon Q's natively supported ingestion formats,
which gives far cleaner retrieval than a raw, noisy PDF.

What it does (maps 1:1 to the requested cleanup steps):

  1. Identify headers / subheaders   -> font-size analysis assigns #, ##, ###
  2. Trim down whitespace            -> collapses runs of spaces, blank lines,
                                        strips NBSP / zero-width chars
  3. Remove divider lines            -> drops horizontal-rule text (---, ___,
                                        ===, em-dash runs) and ignores drawn
                                        rules (they carry no text)
  4. Hyperlinks display exact URL    -> anchor text ("click here") is replaced
                                        with the real target URL
  5. Preserve images                 -> embedded images are extracted to an
                                        images/ folder and referenced inline
                                        in reading order

Usage
-----
    pip install pymupdf
    python clean_confluence_pdf.py input.pdf
    python clean_confluence_pdf.py input.pdf -o cleaned.md --images-dir assets
    python clean_confluence_pdf.py input.pdf --min-image-size 24

Output
------
    <input>.cleaned.md          (or whatever -o specifies)
    <output_dir>/images/...     (extracted images, referenced from the md)
"""

import argparse
import os
import re
import sys
from collections import Counter

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required. Install it with:  pip install pymupdf")


# --------------------------------------------------------------------------- #
# Tunable heuristics
# --------------------------------------------------------------------------- #
HEADER_SIZE_RATIO = 1.15   # a line is a header if its font > body_size * ratio
MAX_HEADER_CHARS = 140     # headers are short; longer "big" lines are body text
MAX_HEADER_LEVELS = 4      # cap at #### (H4)

# Lines whose stripped text is only these characters are treated as dividers.
DIVIDER_RE = re.compile(r"^\s*[-_=*~–—•·.]{3,}\s*$")

# Inline whitespace + junk characters to normalise.
_WS_RE = re.compile(r"[ \t\f\v]+")
_NBSP = "\xa0"
_ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff")


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
def clean_inline(text: str) -> str:
    """Normalise whitespace and strip junk characters from a single line."""
    text = text.replace(_NBSP, " ")
    for zw in _ZERO_WIDTH:
        text = text.replace(zw, "")
    text = _WS_RE.sub(" ", text)
    return text.strip()


def is_divider(text: str) -> bool:
    return bool(DIVIDER_RE.match(text))


def finalize(markdown: str) -> str:
    """Document-level whitespace cleanup."""
    # strip trailing spaces on every line
    lines = [ln.rstrip() for ln in markdown.splitlines()]
    out = "\n".join(lines)
    # collapse 3+ blank lines down to a single blank line
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


# --------------------------------------------------------------------------- #
# Font-size analysis -> header levels
# --------------------------------------------------------------------------- #
def compute_body_size(doc) -> float:
    """The most common font size (weighted by character count) = body text."""
    sizes = Counter()
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    n = max(1, len(span["text"].strip()))
                    sizes[round(span["size"], 1)] += n
    if not sizes:
        return 0.0
    return sizes.most_common(1)[0][0]


def build_header_levels(doc, body_size: float) -> dict:
    """Map each distinct 'large' font size to a header level (1..MAX)."""
    big = set()
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    if size > body_size * HEADER_SIZE_RATIO and span["text"].strip():
                        big.add(size)
    ranked = sorted(big, reverse=True)
    return {size: min(i + 1, MAX_HEADER_LEVELS) for i, size in enumerate(ranked)}


def dominant_size(line) -> float:
    """Font size that covers the most characters in a line."""
    sizes = Counter()
    for span in line["spans"]:
        sizes[round(span["size"], 1)] += max(1, len(span["text"].strip()))
    if not sizes:
        return 0.0
    return sizes.most_common(1)[0][0]


# --------------------------------------------------------------------------- #
# Hyperlinks -> show the exact URL
# --------------------------------------------------------------------------- #
def page_link_rects(page):
    """Return [(fitz.Rect, uri), ...] for external links on the page."""
    rects = []
    for link in page.get_links():
        uri = link.get("uri")
        if uri and "from" in link:
            rects.append((fitz.Rect(link["from"]), uri))
    return rects


def uri_for_span(span_bbox, link_rects):
    """If a span overlaps a link rectangle, return that link's URI."""
    srect = fitz.Rect(span_bbox)
    for rect, uri in link_rects:
        if srect.intersects(rect):
            return uri
    return None


def line_text(line, link_rects) -> str:
    """
    Build a line's text. Spans that sit on top of a hyperlink are replaced
    by the link's actual URL (deduped so a multi-span anchor emits the URL
    once). The URL is padded with spaces so it never glues to neighbours.
    """
    parts = []
    prev_uri = None
    for span in line["spans"]:
        uri = uri_for_span(span["bbox"], link_rects)
        if uri:
            if uri != prev_uri:
                parts.append(f" {uri} ")
            prev_uri = uri
        else:
            parts.append(span["text"])
            prev_uri = None
    return clean_inline("".join(parts))


# --------------------------------------------------------------------------- #
# Images -> extract and reference inline
# --------------------------------------------------------------------------- #
def save_image(block, images_dir, rel_prefix, counter, min_size) -> str | None:
    """Save an image block to disk; return a Markdown image reference (or None)."""
    bbox = fitz.Rect(block["bbox"])
    if min_size and (bbox.width < min_size or bbox.height < min_size):
        return None  # skip tiny decorative icons / logos

    data = block.get("image")
    if not data:
        return None
    ext = block.get("ext", "png") or "png"

    counter[0] += 1
    name = f"img_{counter[0]:03d}.{ext}"
    path = os.path.join(images_dir, name)
    with open(path, "wb") as fh:
        fh.write(data)

    rel = os.path.join(rel_prefix, name).replace(os.sep, "/")
    return f"![image {counter[0]}]({rel})"


# --------------------------------------------------------------------------- #
# Page processing
# --------------------------------------------------------------------------- #
def process_page(page, level_map, link_rects, images_dir, rel_prefix,
                 img_counter, min_size):
    """Return an ordered list of (y, x, markdown_text) elements for the page."""
    elements = []
    blocks = page.get_text("dict")["blocks"]

    for block in blocks:
        btype = block.get("type")
        x0, y0 = block["bbox"][0], block["bbox"][1]

        if btype == 1:  # image block
            ref = save_image(block, images_dir, rel_prefix, img_counter, min_size)
            if ref:
                elements.append((y0, x0, ref))
            continue

        if btype != 0:  # not text
            continue

        paragraph = []
        for line in block["lines"]:
            text = line_text(line, link_rects)
            if not text:
                continue
            if is_divider(text):          # step 3: drop divider lines
                continue
            size = dominant_size(line)
            level = level_map.get(size)
            if level and len(text) <= MAX_HEADER_CHARS:   # step 1: header
                # flush any pending paragraph before the header
                if paragraph:
                    elements.append((y0, x0, " ".join(paragraph)))
                    paragraph = []
                ly = line["bbox"][1]
                lx = line["bbox"][0]
                elements.append((ly, lx, f"{'#' * level} {text}"))
            else:
                paragraph.append(text)

        if paragraph:
            elements.append((y0, x0, " ".join(paragraph)))

    return elements


def clean_pdf(input_path, output_path, images_dir, rel_prefix, min_size):
    doc = fitz.open(input_path)

    body_size = compute_body_size(doc)
    level_map = build_header_levels(doc, body_size)

    os.makedirs(images_dir, exist_ok=True)
    img_counter = [0]

    all_elements = []
    for page in doc:
        link_rects = page_link_rects(page)
        page_elements = process_page(
            page, level_map, link_rects, images_dir, rel_prefix,
            img_counter, min_size,
        )
        # reading order: top-to-bottom, then left-to-right
        page_elements.sort(key=lambda e: (round(e[0], 1), round(e[1], 1)))
        all_elements.extend(text for _, _, text in page_elements)

    markdown = finalize("\n\n".join(all_elements))
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    doc.close()
    return {
        "body_size": body_size,
        "header_levels": len(level_map),
        "images": img_counter[0],
        "output": output_path,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(
        description="Clean a Confluence-exported PDF into Markdown for Amazon Q ingestion."
    )
    parser.add_argument("input", help="Path to the Confluence-exported PDF")
    parser.add_argument("-o", "--output",
                        help="Output Markdown path (default: <input>.cleaned.md)")
    parser.add_argument("--images-dir", default="images",
                        help="Folder name for extracted images, relative to the "
                             "output file (default: images)")
    parser.add_argument("--min-image-size", type=float, default=0,
                        help="Skip images smaller than this many points in either "
                             "dimension (helps drop logos/icons). Default 0 = keep all.")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"Input file not found: {args.input}")

    output_path = args.output or (os.path.splitext(args.input)[0] + ".cleaned.md")
    out_dir = os.path.dirname(os.path.abspath(output_path))
    images_dir = os.path.join(out_dir, args.images_dir)

    stats = clean_pdf(
        input_path=args.input,
        output_path=output_path,
        images_dir=images_dir,
        rel_prefix=args.images_dir,
        min_size=args.min_image_size,
    )

    print("Cleanup complete.")
    print(f"  Detected body font size : {stats['body_size']}")
    print(f"  Header levels assigned  : {stats['header_levels']}")
    print(f"  Images extracted        : {stats['images']}")
    print(f"  Markdown written to     : {stats['output']}")


if __name__ == "__main__":
    main()