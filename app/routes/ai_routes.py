from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.ai.logic import get_topic_recommendations

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/recommendations", methods=["POST"])
@jwt_required()
def get_ai_recommendations():
    print("📥 AI Recommendation Endpoint Hit")

    user_id = get_jwt_identity()
    print("🔐 JWT Identity:", user_id)
    print("🧾 Request Content-Type:", request.content_type)
    print("🧾 Request Data:", request.get_data())

    recommendations = get_topic_recommendations(user_id)
    return jsonify({ "recommendations": recommendations })
