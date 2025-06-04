import os
import joblib
from app.models import Topic, Note

print("📌 Aktif logic.py:", __file__)

def get_topic_recommendations(user_id):
    user_id = str(user_id)

    MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../models'))


    model_path = os.path.join(MODEL_DIR, "nb_model.joblib")
    user_path = os.path.join(MODEL_DIR, "le_user.joblib")
    topic_path = os.path.join(MODEL_DIR, "le_topic.joblib")

    print("\n🧠 MODEL YOL BİLGİLERİ")
    print("📁 MODEL_DIR:", MODEL_DIR)
    print("📄 model_path:", model_path)
    print("📄 user_path :", user_path)
    print("📄 topic_path:", topic_path)

    if not os.path.exists(MODEL_DIR):
        print("❌ MODEL_DIR bulunamadı:", MODEL_DIR)
        return [{
            "title": "Modell nicht gefunden",
            "description": "Das Modellverzeichnis fehlt auf dem Server.",
            "type": "error"
        }]

    model_files = os.listdir(MODEL_DIR)
    print("📂 MODEL_DIR içeriği:", model_files)

    if not (os.path.exists(model_path) and os.path.exists(user_path) and os.path.exists(topic_path)):
        print("❌ Model dosyalarından biri eksik!")
        return [{
            "title": "Modell nicht gefunden",
            "description": "Das Trainingsmodell wurde nicht gefunden. Bitte zuerst train_model.py ausführen.",
            "type": "error"
        }]

    try:
        model = joblib.load(model_path)
        le_user = joblib.load(user_path)
        le_topic = joblib.load(topic_path)
        print("✅ Model ve encoder'lar başarıyla yüklendi.")
    except Exception as e:
        print("❌ Model yükleme hatası:", str(e))
        return [{
            "title": "Ladefehler",
            "description": "Fehler beim Laden des Modells.",
            "type": "error"
        }]

    print("🧪 Kullanıcı ID:", user_id)
    print("🧪 Eğitimli kullanıcılar:", list(le_user.classes_))

    if user_id not in le_user.classes_:
        print(f"ℹ️ Kullanıcı ID {user_id}, eğitim verisinde yok.")
        return [{
            "title": "Keine Daten",
            "description": "Für diesen Benutzer sind nicht genügend Daten vorhanden.",
            "type": "info"
        }]

    user_encoded = le_user.transform([user_id])[0]
    predictions = {}

    for topic_id in le_topic.classes_:
        topic_encoded = le_topic.transform([topic_id])[0]
        prob_wrong = model.predict_proba([[user_encoded, topic_encoded]])[0][0]
        predictions[topic_id] = prob_wrong

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
        print("🔁 Fallback önerilere geçiliyor...")
        fallback = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        for topic_id, prob in fallback:
            topic = Topic.query.get(int(topic_id))
            if topic:
                note = Note.query.filter_by(module_id=topic.module_id).first()
                if note and note.title not in shown_titles:
                    suggestions.append(build_suggestion(note.title, note.module_id, topic.id, prob))
                    shown_titles.add(note.title)
            if len(suggestions) >= 3:
                break

    print(f"✅ Toplam öneri: {len(suggestions)}")
    return suggestions
