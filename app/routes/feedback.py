from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app import db
from app.models import Feedback, UserProgress

feedback_bp = Blueprint('feedback_bp', __name__)

@feedback_bp.route('/feedback', methods=['OPTIONS', 'POST'])
@cross_origin(origins=["https://univo-frontend.vercel.app", "https://univoxacademia.online"], supports_credentials=True)
@jwt_required()
def submit_feedback():
    if request.method == 'OPTIONS':
        return '', 204

    user_id = get_jwt_identity()
    data = request.get_json()
    print("🔐 JWT user_id:", user_id)
    print("📨 Gelen data:", data)

    if not data:
        return jsonify({'error': 'Geçersiz JSON verisi.'}), 400

    message = data.get('message')
    if not message or not message.strip():
        return jsonify({'error': 'Mesaj boş olamaz.'}), 400

    try:
        feedback = Feedback(user_id=user_id, message=message.strip())
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
        return jsonify({'message': 'Feedback başarıyla kaydedildi ve XP verildi.'}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("❌ Feedback error:", str(e))
        traceback.print_exc()
        return jsonify({'error': 'Sunucu hatası oluştu.'}), 500
