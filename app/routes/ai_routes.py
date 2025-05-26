from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.ai.recommend import get_topic_recommendations

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/recommendations", methods=["POST"])
@jwt_required()
def get_ai_recommendations():
    user_id = get_jwt_identity()
    recommendations = get_topic_recommendations(user_id)
    return jsonify({ "recommendations": recommendations })
