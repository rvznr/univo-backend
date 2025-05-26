import pandas as pd
from app import db
from app.models import UserAnswer, Question

def prepare_training_data():
    data = db.session.query(
        UserAnswer.user_id,
        Question.topic_id,
        UserAnswer.is_correct
    ).join(Question, UserAnswer.question_id == Question.id).all()

    df = pd.DataFrame(data, columns=['user_id', 'topic_id', 'is_correct'])
    return df
