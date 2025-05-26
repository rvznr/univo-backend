
from flask import Blueprint

topic_bp = Blueprint('topic_bp', __name__)

@topic_bp.route('/topics')
def get_topics():
    return {"message": "List of topics"}
