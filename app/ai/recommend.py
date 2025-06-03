import os
import joblib
from app.models import Topic, Note

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
print("Model klasörü:", MODEL_DIR)
print("Dosyalar:", os.listdir(MODEL_DIR))


def get_topic_recommendations(user_id):
    user_id = str(user_id)

    model_path = os.path.join(MODEL_DIR, "nb_model.joblib")
    le_user_path = os.path.join(MODEL_DIR, "le_user.joblib")
    le_topic_path = os.path.join(MODEL_DIR, "le_topic.joblib")

    missing = []
    if not os.path.exists(model_path): missing.append("nb_model.joblib")
    if not os.path.exists(le_user_path): missing.append("le_user.joblib")
    if not os.path.exists(le_topic_path): missing.append("le_topic.joblib")

    if missing:
        return [{
            "title": "Modell nicht gefunden",
            "description": f"Fehlende Dateien: {', '.join(missing)}. Bitte zuerst train_model.py ausführen.",
            "type": "error"
        }]

    model = joblib.load(model_path)
    le_user = joblib.load(le_user_path)
    le_topic = joblib.load(le_topic_path)

    if user_id not in le_user.classes_:
        return [{
            "title": "Keine Nutzerdaten",
            "description": "Für diesen Benutzer gibt es noch keine Quizdaten. Bitte zuerst ein Quiz abschließen.",
            "type": "info"
        }]

    user_encoded = le_user.transform([user_id])[0]
    predictions = {}

    for topic_id in le_topic.classes_:
        topic_encoded = le_topic.transform([topic_id])[0]
        prob_wrong = model.predict_proba([[user_encoded, topic_encoded]])[0][0]
        predictions[topic_id] = prob_wrong

    # %40 üzeri filtrele
    filtered = [(tid, prob) for tid, prob in predictions.items() if prob >= 0.4]
    sorted_topics = sorted(filtered, key=lambda x: x[1], reverse=True)

    suggestions = []
    shown_titles = set()

    def build_suggestion(note_title, module_id, topic_id, prob):
        return {
            "title": "Themenwiederholung",
            "description": (
                f"Du hast bei früheren Quizfragen zum Thema '{note_title}' häufiger Fehler gemacht. "
                f"Bitte wiederhole dieses Thema. Fehlerwahrscheinlichkeit: {int(prob * 100)}% 📘 Modul {module_id}"
            ),
            "action": "open_topic",
            "module_id": module_id,
            "topic_id": topic_id,
            "type": "review"
        }

    for topic_id, prob in sorted_topics:
        topic = Topic.query.get(int(topic_id))
        if topic:
            note = Note.query.filter_by(module_id=topic.module_id).first()
            if note and note.title not in shown_titles:
                suggestions.append(build_suggestion(note.title, note.module_id, topic.id, prob))
                shown_titles.add(note.title)

    if not suggestions:
        fallback = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
