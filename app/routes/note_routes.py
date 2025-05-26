from flask import Blueprint, jsonify
from app.models import Note, NoteImage
from flask_jwt_extended import jwt_required

note_bp = Blueprint('note', __name__)

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
@jwt_required(optional=True)
def get_note_by_id(note_id):
    try:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404

        return jsonify(note.to_dict()), 200

    except Exception as e:
        print(f"❌ get_note_by_id HATA: {e}")
        return jsonify({'error': 'Server error'}), 500


@note_bp.route('/note_images/<int:note_content_id>', methods=['GET'])
@jwt_required(optional=True)
def get_images(note_content_id):
    try:
        images = NoteImage.query.filter_by(note_content_id=note_content_id).all()
        return jsonify([image.to_dict() for image in images]), 200
    except Exception as e:
        print(f"❌ Error fetching images: {e}")
        return jsonify({'error': str(e)}), 500