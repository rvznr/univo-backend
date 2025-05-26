from flask import Blueprint, jsonify, request
from app.models import QuizGroup, Question, QuizResult
from flask_jwt_extended import jwt_required, get_jwt_identity

quiz_bp = Blueprint('quiz_bp', __name__)

@quiz_bp.route('/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = QuizGroup.query.all()
    result = []
    for q in quizzes:
        result.append({
            'quiz_id': q.id,
            'title': q.title,
            'difficulty': q.difficulty,
            'topics': q.topic_ids.split(',') if q.topic_ids else []
        })
    return jsonify(result)

@quiz_bp.route('/<int:quiz_id>/questions', methods=['GET'])
def get_questions_for_quiz(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    response = []
    for q in questions:
        options = {
            'a': q.option_a,
            'b': q.option_b,
            'c': q.option_c,
            'd': q.option_d,
        }

        response.append({
            'id': q.id,
            'question': q.question,
            'correct_answer': q.correct_answer.lower(),  
            'topic_id': q.topic_id,
            'question_type': q.question_type,
            'options': options 
        })
    return jsonify(response)

@quiz_bp.route('/<int:quiz_id>/iscompleted', methods=['GET'])
@jwt_required()
def is_quiz_completed(quiz_id):
    user_id = get_jwt_identity()
    existing_result = QuizResult.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    return jsonify({"completed": existing_result is not None})
