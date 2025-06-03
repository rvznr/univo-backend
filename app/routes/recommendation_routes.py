from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.ai.logic import get_topic_recommendations

recommendation_bp = Blueprint('recommendation_bp', __name__)

@recommendation_bp.route('/ai/recommendations', methods=['POST'])
@jwt_required()
def get_ai_recommendations():
    user_id = get_jwt_identity()
    try:
        suggestions = get_topic_recommendations(user_id)
        return jsonify({"recommendations": suggestions}), 200
    except Exception as e:
        print("❌ Recommendation Error:", str(e))
        return jsonify({"recommendations": []}), 500
