from flask import Flask
from flask_smorest import Api
from langchain_core.output_parsers import StrOutputParser

from resources.message.message import blp as MessageBlueprint
from services.LLM import LLMModel
from services.Prompt import Prompt
app = Flask(__name__)


app.config["PROPAGATE_EXCEPTIONIS"] = True
app.config["API_TITLE"] = "RAG POC"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


llm = LLMModel().get()
prompt = Prompt().get()
output_parser = StrOutputParser()

chain = prompt|llm|output_parser

input_text = "What question you have in mind?"

print(chain.invoke({"question": input_text}))

api = Api(app)

api.register_blueprint(MessageBlueprint)