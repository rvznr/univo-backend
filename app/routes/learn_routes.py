from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Module, UserProgress, Note, NoteImage

learn_bp = Blueprint('learn', __name__)

@learn_bp.route('/modules', methods=['GET'])
@jwt_required(optional=True)
def get_modules():
    try:
        current_user_id = get_jwt_identity()
        modules = Module.query.all()
        result = []

        for mod in modules:
            try:
                mod_dict = mod.to_dict()
            except Exception as e:
                print(f"❌ mod.to_dict() hatası - mod id: {mod.id} -> {e}")
                continue

            if current_user_id:
                try:
                    progress = UserProgress.query.filter_by(
                        user_id=current_user_id, module_id=mod.id
                    ).first()

                    xp_notes = progress.xp_from_notes if progress else 0
                    xp_exercises = progress.xp_from_exercises if progress else 0
                    percent = 0
                    if xp_notes > 0:
                        percent += 50
                    if xp_exercises > 0:
                        percent += 50

                    mod_dict['user_progress'] = {
                        'xp_from_notes': xp_notes,
                        'xp_from_exercises': xp_exercises,
                        'percent': percent
                    }
                except Exception as e:
                    print(f"❌ progress hesaplama hatası - user: {current_user_id} - mod: {mod.id} -> {e}")

            result.append(mod_dict)

        return jsonify(result), 200

    except Exception as e:
        print("❌ Genel get_modules hatası:", e)
        return jsonify({'error': 'Module data error'}), 500


@learn_bp.route('/modules/<int:module_id>', methods=['GET'])
@jwt_required(optional=True)
def get_module_by_id(module_id):
    try:
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'error': 'Module not found'}), 404

        return jsonify(module.to_dict()), 200

    except Exception as e:
        print(f"❌ get_module_by_id hatası - id: {module_id} -> {e}")
        return jsonify({'error': 'Error retrieving module'}), 500
