from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app import db
from app.models import Feedback, UserProgress

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['OPTIONS', 'POST'])
@cross_origin(origins=["http://localhost:3000"], supports_credentials=True)
@jwt_required()
def submit_feedback():
    if request.method == 'OPTIONS':
        return '', 204

    user_id = get_jwt_identity()
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({'error': 'Nachricht darf nicht leer sein.'}), 400

    try:
        feedback = Feedback(user_id=user_id, message=message)
        db.session.add(feedback)

        progress = UserProgress.query.filter_by(user_id=user_id, module_id=None).first()

        if not progress:
            progress = UserProgress(
                user_id=user_id,
                module_id=None,
                xp_from_notes=0,
                xp_from_exercises=0,
                xp_from_feedback=160
            )
            db.session.add(progress)
        elif not progress.xp_from_feedback:
            progress.xp_from_feedback = 160

        db.session.commit()
        return jsonify({'message': 'Feedback erfolgreich gespeichert und XP vergeben.'}), 200
    except Exception as e:
        db.session.rollback()
        print("Feedback error:", e)
        return jsonify({'error': 'Ein Fehler ist aufgetreten.'}), 500
