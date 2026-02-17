import os

from flask import Flask
from flask_smorest import Api


from app.routes import api
from app.database import db
from app.models import Message,Document



def create_app(db_url=None):

    app = Flask(__name__)


    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    app.config["PROPAGATE_EXCEPTIONIS"] = True
    app.config["API_TITLE"] = "RAG POC"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = ""
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        from sqlalchemy import text
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))        
        db.create_all()

    from app.services.LLM import ChatGroqModel
    app.ai_service = ChatGroqModel()  # model is loaded once

    


    api_endpoints = Api(app)
    api_endpoints.register_blueprint(api)

    return app