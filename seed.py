# seed.py
from app import app, db
from models import User, Module, Quiz, Challenge
from werkzeug.security import generate_password_hash

# Use app context
with app.app_context():

    # Drop all tables and recreate them (optional)
    db.drop_all()
    db.create_all()

    # -----------------------------
    # Users
    # -----------------------------
    admin = User(
        name="Admin User",
        email="admin@ecoquest.com",
        password=generate_password_hash("admin123"),
        role="admin",
        eco_points=0
    )

    teacher = User(
        name="Jane Teacher",
        email="teacher@ecoquest.com",
        password=generate_password_hash("teacher123"),
        role="teacher",
        eco_points=0
    )

    student1 = User(
        name="Alice Student",
        email="alice@ecoquest.com",
        password=generate_password_hash("student123"),
        role="student",
        eco_points=50
    )

    student2 = User(
        name="Bob Student",
        email="bob@ecoquest.com",
        password=generate_password_hash("student123"),
        role="student",
        eco_points=120
    )

    db.session.add_all([admin, teacher, student1, student2])
    db.session.commit()

    # -----------------------------
    # Modules
    # -----------------------------
    module1 = Module(title="Recycling Basics", description="Learn the basics of recycling.", content="Content for Recycling Basics.")
    module2 = Module(title="Water Conservation", description="Tips and tricks to save water.", content="Content for Water Conservation.")
    module3 = Module(title="Energy Saving", description="Reduce energy consumption at home.", content="Content for Energy Saving.")

    db.session.add_all([module1, module2, module3])
    db.session.commit()

    # -----------------------------
    # Quizzes
    # -----------------------------
    quiz1 = Quiz(module_id=module1.id, question="Which material is recyclable?", correct_answer="Plastic", points=10)
    quiz2 = Quiz(module_id=module2.id, question="Turn off the tap while brushing. True or False?", correct_answer="True", points=10)

    db.session.add_all([quiz1, quiz2])
    db.session.commit()

    # -----------------------------
    # Challenges
    # -----------------------------
    challenge1 = Challenge(title="Recycle at Home", description="Upload a photo of your recycling efforts.", points=20)
    challenge2 = Challenge(title="Water Saving Challenge", description="Submit a screenshot of your water meter saving.", points=15)

    db.session.add_all([challenge1, challenge2])
    db.session.commit()

    print("✅ Database seeded successfully!")
