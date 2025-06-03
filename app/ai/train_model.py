import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pandas as pd
import joblib
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from app import db, create_app
from app.models import UserAnswer, Question, Topic

def prepare_training_data():
    data = db.session.query(
        UserAnswer.user_id,
        Question.topic_id,
        UserAnswer.is_correct
    ).join(Question, UserAnswer.question_id == Question.id).all()

    df = pd.DataFrame(data, columns=['user_id', 'topic_id', 'is_correct'])
    df['user_id'] = df['user_id'].astype(str)
    df['topic_id'] = df['topic_id'].astype(str)
    return df

def train_and_save_model():
    df = prepare_training_data()
    if df.empty:
        print("❌ Keine Trainingsdaten gefunden.")
        return

    le_user = LabelEncoder()
    le_topic = LabelEncoder()

    df['user_encoded'] = le_user.fit_transform(df['user_id'])
    df['topic_encoded'] = le_topic.fit_transform(df['topic_id'])

    X = df[['user_encoded', 'topic_encoded']]
    y = df['is_correct']

    model = MultinomialNB()
    model.fit(X, y)

    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, "nb_model.joblib"))
    joblib.dump(le_user, os.path.join(model_dir, "le_user.joblib"))
    joblib.dump(le_topic, os.path.join(model_dir, "le_topic.joblib"))



    print("✅ Modell wurde erfolgreich trainiert und gespeichert.")
    print("Trainierte Benutzer:", df['user_id'].nunique())

    summary = df.groupby(['topic_id']).agg({'is_correct': ['count', 'sum']})
    summary.columns = ['total', 'correct']
    summary['accuracy'] = summary['correct'] / summary['total']
    summary = summary.reset_index()
    print("--- Themen-Genauigkeit ---")
    for _, row in summary.iterrows():
        topic = Topic.query.get(int(row['topic_id']))
        if topic:
            print(f"📘 Modul {topic.module_id} - {topic.title}: {row['accuracy']:.2f} Genauigkeit")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        train_and_save_model()
