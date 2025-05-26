from app import db
from datetime import datetime
import json
import base64
from sqlalchemy import LargeBinary


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)
    user_answers = db.relationship('UserAnswer', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    progress = db.relationship('UserProgress', backref='user', lazy=True)

class NoteContent(db.Model):
    __tablename__ = "note_content"

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)  


    def to_dict(self):
        return {
            "id": self.id,
            "note_id": self.note_id,
            "page_number": self.page_number,
            "title": self.title,
            "content": self.content,
            "images": [image.to_dict() for image in self.images]  
        }

class NoteImage(db.Model):
    __tablename__ = 'note_images'

    id = db.Column(db.Integer, primary_key=True)
    note_content_id = db.Column(db.Integer, db.ForeignKey('note_content.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_data = db.Column(db.LargeBinary)  

    note_content = db.relationship('NoteContent', backref=db.backref('images', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'note_content_id': self.note_content_id,
            'image_url': self.image_url
        }
        
class Module(db.Model):
    __tablename__ = 'module'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    image = db.Column(db.LargeBinary)
    is_locked = db.Column(db.Boolean, default=False)
    full_width = db.Column(db.Boolean, default=False)

    notes = db.relationship('Note', backref='module', lazy=True, cascade="all, delete-orphan")
    exercises = db.relationship('Exercise', backref='module', lazy=True, cascade="all, delete-orphan")
    progress = db.relationship('UserProgress', backref='module', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image': base64.b64encode(self.image).decode('utf-8') if self.image else None,
            'isLocked': self.is_locked,
            'fullWidth': self.full_width,
            'notes': [n.to_dict() for n in self.notes],
            'exercises': [e.to_dict() for e in self.exercises]
        }

class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255))
    pages = db.Column(db.Text)  
    content_de = db.Column(db.Text)

    contents = db.relationship("NoteContent", backref="note", lazy=True, order_by="NoteContent.page_number")

    def to_dict(self):
        try:
            pages_data = json.loads(self.pages) if self.pages else []
            return {
                'id': self.id,
                'title': self.title,
                'module_id': self.module_id,
                'pages': pages_data if isinstance(pages_data, list) else [],
                'content_de': self.content_de,
                'contents': [c.to_dict() for c in self.contents]
            }
        except Exception as e:
            print(f"[Note to_dict HATASI] ID: {self.id} => {e}")
            return {
                'id': self.id,
                'title': self.title,
                'module_id': self.module_id,
                'pages': [],
                'content_de': self.content_de,
                'contents': [c.to_dict() for c in self.contents]
            }

class Exercise(db.Model):
    __tablename__ = "exercise"   

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(255))
    type = db.Column(db.String(50))
    questions = db.Column(db.Text)

    def to_dict(self):
        try:
            return {
                'id': self.id,
                'title': self.title,
                'module_id': self.module_id,
                'type': self.type,
                'questions': json.loads(self.questions) if self.questions else []
            }
        except Exception as e:
            print(f"[Exercise to_dict HATA] ID: {self.id} => {e}")
            return {
                'id': self.id,
                'title': self.title,
                'module_id': self.module_id,
                'type': self.type,
                'questions': []
            }

class QuizGroup(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(50))
    topic_ids = db.Column(db.String)

    questions = db.relationship('Question', backref='quiz_group', lazy=True)
    results = db.relationship('QuizResult', backref='quiz', lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))

    question_type = db.Column(db.String(50), default="multiple", nullable=False)

    explanation = db.Column(db.Text) 
    
    user_answers = db.relationship('UserAnswer', backref='question', lazy=True)



class QuizResult(db.Model):
    __tablename__ = 'quiz_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    xp = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserAnswer(db.Model):
    __tablename__ = 'user_answers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False) 
    selected_answer = db.Column(db.String, nullable=False)
    is_correct = db.Column(db.Boolean)


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    xp_from_notes = db.Column(db.Integer, default=0)
    xp_from_exercises = db.Column(db.Integer, default=0)
    xp_from_feedback = db.Column(db.Integer, default=0)


    def total_xp(self):
        return self.xp_from_notes + self.xp_from_exercises


class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    image = db.Column(db.String)
    progress = db.Column(db.Float, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    module_id = db.Column(db.Integer, nullable=True)

    questions = db.relationship('Question', backref='topic', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='topic', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'progress': self.progress,
            'is_locked': self.is_locked
        }
