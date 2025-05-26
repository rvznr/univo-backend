from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import UserAnswer

useranswer_bp = Blueprint('useranswer_bp', __name__)

# @useranswer_bp.route('/user_answer', methods=['POST'])
# @jwt_required()
# def save_user_answer():
#     data = request.get_json()
#     user_id = get_jwt_identity()

#     quiz_id = data.get('quiz_id')
#     question_id = data.get('question_id')
#     selected_answer = data.get('selected_answer')
#     is_correct = data.get('is_correct')

#     if not all([quiz_id, question_id, selected_answer, isinstance(is_correct, bool)]):
#         return jsonify({"message": "Eksik veya hatalı veri!"}), 400

#     try:
#         answer = UserAnswer(
#             user_id=user_id,
#             quiz_id=question_id,  # dikkat: burada question_id = quiz_id FK'si!
#             selected_answer=selected_answer,
#             is_correct=is_correct
#         )
#         db.session.add(answer)
#         db.session.commit()

#         return jsonify({"message": "Cevap başarıyla kaydedildi."}), 201

#     except Exception as e:
#         print("UserAnswer Save Error:", str(e))
#         return jsonify({"error": "Cevap kaydedilemedi"}), 500
