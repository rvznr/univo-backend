from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text
import json

exercise_bp = Blueprint('exercise', __name__)

@exercise_bp.route("/module-exercises/<int:module_id>", methods=["GET"])
def get_module_with_exercises(module_id):
    try:
        exercise_query = text("""
            SELECT * FROM exercise WHERE module_id = :module_id
        """)
        exercises = db.session.execute(exercise_query, {"module_id": module_id}).fetchall()

        exercises_with_questions = []

        for ex in exercises:
            raw_questions = ex.questions
            parsed_questions = []

            if raw_questions:
                try:
                    if isinstance(raw_questions, str):
                        parsed = json.loads(raw_questions)
                    else:
                        parsed = raw_questions

                    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], list):
                        parsed = parsed[0]

                    for q in parsed:
                        if "xp_reward" not in q:
                            q["xp_reward"] = 15

                    parsed_questions = parsed

                except Exception as e:
                    print(f"❌ JSON parse hatası: {e}")
                    parsed_questions = []

            exercise_data = {
                "id": ex.id,
                "module_id": ex.module_id,
                "title": ex.title,
                "type": ex.type,
                "questions": parsed_questions
            }
            exercises_with_questions.append(exercise_data)

        return jsonify({
            "id": module_id,
            "exercises": exercises_with_questions
        }), 200

    except Exception as e:
        print(f"❌ Exercise Fetch Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
