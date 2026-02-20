from flask_smorest import Blueprint

api = Blueprint(
    "api",
    __name__,
    url_prefix="/api/v1",
    description="RAG API"
)

from .message import blp as MessageBlueprint
from .conversation import blp as ConversationBlueprint
from .document import blp as DocumentBlueprint

api.register_blueprint(MessageBlueprint)
api.register_blueprint(ConversationBlueprint)
api.register_blueprint(DocumentBlueprint)