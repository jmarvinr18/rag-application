import os
import asyncio
import sys
# 🔥 Fix for psycopg async on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
from flask import Flask
from flask_smorest import Api
from app.config import Config
from app.extensions.redis_client import init_redis
from sqlalchemy import text
from app.routes import api
from app.database import db
from app.services.LLM import ChatGroqModel, OllamaModel
from app.services.Message import AIMessageService
from flask_migrate import Migrate

migrate = Migrate()



def create_app(db_url=None):

    app = Flask(__name__)
    app.config.from_object(Config)

    # init redis
    init_redis(app)


    app.config["PROPAGATE_EXCEPTIONIS"] = True
    app.config["API_TITLE"] = "RAG POC"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = ""
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    UPLOAD_FOLDER = "uploads"

    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


    db.init_app(app)
    migrate.init_app(app=app, db=db)

    with app.app_context():
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))        
        db.create_all()

    
    model = ChatGroqModel().get_model()  # model is loaded once
    # model = OllamaModel().get_model()  # model is loaded once
    app.ai_service = AIMessageService(model)


    api_endpoints = Api(app)
    api_endpoints.register_blueprint(api)

    return app