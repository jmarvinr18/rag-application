# syntax=docker/dockerfile:1

# Confluence PDF -> cleaned DOCX converter.
# PyMuPDF and python-docx ship pure pip wheels (MuPDF is bundled), so no
# apt build dependencies are required on a glibc-based slim image.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="confluence-pdf-to-docx" \
      org.opencontainers.image.description="Clean a Confluence-exported PDF into a self-contained DOCX for Amazon Q ingestion." \
      org.opencontainers.image.source="https://example.com/your-repo"

# Deterministic, log-friendly Python behaviour for CI/CD.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so this layer is cached unless requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY confluence_pdf_to_docx.py .

# Run as a non-root user (least privilege). UID 1000 plays nicely with most
# Jenkins agents; override at build time with --build-arg UID=<id> if needed.
ARG UID=1000
RUN useradd --create-home --uid "${UID}" appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data
USER appuser

# /data is the mount point for input PDFs and output DOCX files.
WORKDIR /data
VOLUME ["/data"]

# `docker run <image> input.pdf output.docx [flags]` — args pass straight through.
ENTRYPOINT ["python", "/app/confluence_pdf_to_docx.py"]
CMD ["--help"]