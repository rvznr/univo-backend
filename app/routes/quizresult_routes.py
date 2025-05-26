from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import UserAnswer, Question, QuizResult
from flask_cors import cross_origin

quizresult_bp = Blueprint('quizresult_bp', __name__)


@quizresult_bp.route('/quiz/<int:quiz_id>/results', methods=['GET'])
@cross_origin(origins="*", supports_credentials=True)
@jwt_required()
def get_quiz_result_by_id(quiz_id):
    try:
        user_id = get_jwt_identity()
        user_answers = UserAnswer.query.join(Question).filter(
            UserAnswer.user_id == user_id,
            Question.quiz_id == quiz_id
        ).all()

        if not user_answers:
            return jsonify({"results": []}), 200

        result_data = []
        for ua in user_answers:
            question = Question.query.get(ua.question_id)
            result_data.append({
                "quizId": ua.quiz_id,
                "question": question.question,
                "selectedAnswer": ua.selected_answer,
                "correctAnswer": question.correct_answer,
                "isCorrect": ua.is_correct,
                "explanation": question.explanation or ""
            })

        return jsonify({"results": result_data}), 200
    except Exception as e:
        print("❌ get_quiz_result_by_id error:", str(e))
        return jsonify({"error": "failed to fetch results"}), 500


@quizresult_bp.route('/quizresults', methods=['GET'])
@cross_origin(origins="*", supports_credentials=True)
@jwt_required()
def get_all_quiz_results():
    try:
        user_id = get_jwt_identity()
        results = QuizResult.query.filter_by(user_id=user_id).all()

        response_data = [{
            "quiz_id": r.quiz_id,
            "topic_id": r.topic_id,
            "score": r.score,
            "xp": r.xp,
            "total_questions": r.total_questions,
            "correct_answers": r.correct_answers
        } for r in results]

        return jsonify(response_data), 200
    except Exception as e:
        print("❌ QuizResult GET error:", str(e))
        return jsonify({"error": "Sonuçlar getirilemedi"}), 500


@quizresult_bp.route('/quizresults', methods=['POST'])
@cross_origin(origins="*", supports_credentials=True)
@jwt_required()
def save_quiz_result():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        quiz_id = data.get('quiz_id')
        topic_id = data.get('topic_id')
        total_questions = data.get('total_questions')

        if quiz_id is None or topic_id is None or total_questions is None:
            print("⚠️ Eksik veya hatalı veri:", data)
            return jsonify({"message": "Eksik veri gönderildi!"}), 400

        correct_answers = UserAnswer.query.join(Question).filter(
            UserAnswer.user_id == user_id,
            Question.quiz_id == quiz_id,
            UserAnswer.is_correct == True
        ).count()

        score = correct_answers
        xp = min(score * 15, 30)

        existing_result = QuizResult.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if existing_result:
            return jsonify({"message": "Bu quiz sonucu zaten kayıtlı."}), 200

        result = QuizResult(
            user_id=user_id,
            quiz_id=quiz_id,
            topic_id=topic_id,
            score=score,
            xp=xp,
            total_questions=total_questions,
            correct_answers=correct_answers
        )

        db.session.add(result)
        db.session.commit()

        return jsonify({
            "message": "Quiz sonucu başarıyla kaydedildi.",
            "score": score,
            "xp": xp,
            "correct_answers": correct_answers
        }), 201

    except Exception as e:
        print("❌ QuizResult Save Error:", str(e))
        return jsonify({"error": "Quiz sonucu kaydedilemedi"}), 500


@quizresult_bp.route('/user_answer', methods=['POST'])
@cross_origin(origins="*", supports_credentials=True)
@jwt_required()
def save_user_answer():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')

        if not question_id or not selected_answer:
            return jsonify({"error": "Eksik veri gönderildi."}), 400

        question = Question.query.get(question_id)
        if not question:
            return jsonify({"error": "Soru bulunamadı."}), 404

        is_correct = selected_answer.strip().lower() == question.correct_answer.strip().lower()

        existing_answer = UserAnswer.query.filter_by(user_id=user_id, question_id=question_id).first()
        if existing_answer:
            return jsonify({"message": "Bu soru zaten cevaplanmış."}), 200

        user_answer = UserAnswer(
            user_id=user_id,
            question_id=question.id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            quiz_id=question.quiz_id
        )

        db.session.add(user_answer)
        db.session.commit()

        return jsonify({
            "message": "Cevap başarıyla kaydedildi.",
            "is_correct": is_correct
        }), 201

    except Exception as e:
        print("❌ UserAnswer Save Error:", str(e))
        return jsonify({"error": "Cevap kaydedilemedi"}), 500
