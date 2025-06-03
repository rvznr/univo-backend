from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.ai.logic import get_topic_recommendations

ai_bp = Blueprint("ai_bp", __name__)

print("📥 AI Recommendation Endpoint Hit")
print("🔐 JWT Identity:", get_jwt_identity())
print("🧾 Request Content-Type:", request.content_type)
print("🧾 Request Data:", request.get_data())

@ai_bp.route("/recommendations", methods=["POST"])
@jwt_required()
def get_ai_recommendations():
    user_id = get_jwt_identity()
    recommendations = get_topic_recommendations(user_id)
    return jsonify({ "recommendations": recommendations })
