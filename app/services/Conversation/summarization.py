from app.models import Conversation
from app.database.db import db





from flask import current_app

def summarize_conversation(convesation_id: str):

    conversation = Conversation.query.get(convesation_id)

    if not conversation:
        print("[WORKER ERROR] Conversation not found")
        return

    if conversation.title is not None:
        print("[WORKER ERROR] Conversation title is already created")
        return
    
    try:

        input_text = "Make me an 8 word summary as title about my current or previous"

        ai_text = current_app.ai_service.ask(convesation_id, input_text)

        print(f"SUMMARY TITLE: {ai_text["answer"]}")

        conversation.title = ai_text["answer"]
        db.session.commit()

        print(f"[WORKER] Completed {convesation_id}")
    except Exception as e:
        print("[WORKER ERROR]", e)
        db.session.commit()