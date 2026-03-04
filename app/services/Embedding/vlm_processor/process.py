import base64
from langchain_core.messages import HumanMessage


def process(human_message, image_path):
    if image_path:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        message = HumanMessage(content = [
            {"type": "text", "text": human_message},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            }
        ])