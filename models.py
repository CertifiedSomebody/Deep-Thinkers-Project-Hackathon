from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="student")
    eco_points = db.Column(db.Integer, default=0)

    # Relationships
    submissions = db.relationship("Submission", backref="user", lazy=True)
    forum_posts = db.relationship("ForumPost", backref="author", lazy=True)

    def __repr__(self):
        return f"<User {self.name} ({self.email})>"


class Module(db.Model):
    __tablename__ = "module"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)

    # Relationships
    quizzes = db.relationship("Quiz", backref="module", lazy=True)

    def __repr__(self):
        return f"<Module {self.title}>"


class Quiz(db.Model):
    __tablename__ = "quiz"
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # store as JSON string
    correct_answer = db.Column(db.String(200))
    points = db.Column(db.Integer, default=10)

    def __repr__(self):
        return f"<Quiz {self.question[:20]}...>"


class Challenge(db.Model):
    __tablename__ = "challenge"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    points = db.Column(db.Integer, default=20)

    # Relationships
    submissions = db.relationship("Submission", backref="challenge", lazy=True)

    def __repr__(self):
        return f"<Challenge {self.title}>"


class Submission(db.Model):
    __tablename__ = "submission"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenge.id"), nullable=False)
    proof_link = db.Column(db.String(300))
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Submission user:{self.user_id} challenge:{self.challenge_id}>"


class ForumPost(db.Model):
    __tablename__ = "forum_post"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ForumPost {self.title[:20]}...>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"), nullable=False)

    # Relationships
    user = db.relationship("User", backref="comments", lazy=True)
    post = db.relationship("ForumPost", backref="comments", lazy=True)
