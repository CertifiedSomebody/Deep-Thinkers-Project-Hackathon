import os
import json  # make sure this is at the top of app.py
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import TakeQuizForm  


from models import db, User, Module, Quiz, Challenge, Submission, ForumPost, Comment
from forms import (
    LoginForm,
    RegisterForm,
    QuizForm,
    ChallengeForm,
    ChallengeSubmissionForm, 
    ForumForm,
    CommentForm,
    ModuleForm,
    GameForm,
)
from config import Config
from flask_migrate import Migrate
from models import db
# -----------------------------
# FLASK APP SETUP
# -----------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB
db.init_app(app)
migrate = Migrate(app, db)

# Login manager setup
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Upload folder setup
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# -----------------------------
# LOGIN MANAGER
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inject current datetime into templates
@app.context_processor
def inject_now():
    return {"now": datetime.now}

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    modules = Module.query.all()
    challenges = Challenge.query.all()
    top_users = User.query.order_by(User.eco_points.desc()).limit(5).all()
    return render_template(
        "index.html", modules=modules, challenges=challenges, top_users=top_users
    )

# ---------- AUTH ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_pw,
            role=form.role.data or "student",
            eco_points=0,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))

# ---------- DASHBOARD ----------
@app.route("/dashboard")
@login_required
def dashboard():
    modules = Module.query.all()
    challenges = Challenge.query.all()

    if current_user.role == "teacher":
        submissions = Submission.query.order_by(Submission.id.desc()).all()
        return render_template(
            "dashboard_teacher.html",
            modules=modules,
            challenges=challenges,
            submissions=submissions,
        )

    leaderboard = User.query.filter_by(role="student").order_by(
        User.eco_points.desc()
    ).limit(5).all()

    return render_template(
        "dashboard_student.html",
        modules=modules,
        challenges=challenges,
        leaderboard=leaderboard,
    )

# ---------- MODULE DETAIL ----------
@app.route("/module/<int:module_id>")
@login_required
def module_detail(module_id):
    module_obj = Module.query.get_or_404(module_id)
    return render_template("module.html", module=module_obj)

# ---------- MODULE MANAGEMENT ----------
@app.route("/module/create", methods=["GET", "POST"])
@login_required
def create_module():
    if current_user.role != "teacher":
        flash("Only teachers can add modules.", "danger")
        return redirect(url_for("dashboard"))

    form = ModuleForm()
    if form.validate_on_submit():
        module = Module(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data
        )
        db.session.add(module)
        db.session.commit()
        flash("Module added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_module.html", form=form)

@app.route("/module/edit/<int:module_id>", methods=["GET", "POST"])
@login_required
def edit_module(module_id):
    if current_user.role != "teacher":
        flash("Only teachers can edit modules.", "danger")
        return redirect(url_for("dashboard"))

    module = Module.query.get_or_404(module_id)
    form = ModuleForm(obj=module)
    if form.validate_on_submit():
        module.title = form.title.data
        module.description = form.description.data
        module.content = form.content.data
        db.session.commit()
        flash("Module updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_module.html", form=form, edit=True)

@app.route("/module/delete/<int:module_id>")
@login_required
def delete_module(module_id):
    if current_user.role != "teacher":
        flash("Only teachers can delete modules.", "danger")
        return redirect(url_for("dashboard"))

    module = Module.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()
    flash("Module deleted successfully!", "success")
    return redirect(url_for("dashboard"))

# ---------- FORUM ----------
@app.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    form = ForumForm()
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    if form.validate_on_submit():
        post = ForumPost(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        flash("Post added!", "success")
        return redirect(url_for("forum"))
    return render_template("forum.html", form=form, posts=posts)

@app.route("/forum/<int:post_id>", methods=["GET", "POST"])
@login_required
def forum_post_detail(post_id):
    post = ForumPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Comment added!", "success")
        return redirect(url_for("forum_post_detail", post_id=post.id))
    return render_template("forum_post.html", post=post, form=form)

# ---------- CHALLENGES ----------

from werkzeug.utils import secure_filename
from forms import ChallengeForm

# View / Submit a challenge (students)
@app.route("/challenge/<int:challenge_id>", methods=["GET", "POST"])
@login_required
def challenge(challenge_id):
    challenge_obj = Challenge.query.get_or_404(challenge_id)

    # Only students can submit
    if current_user.role == "teacher":
        flash("Teachers cannot submit challenges.", "warning")
        return redirect(url_for("dashboard"))

    # Check if the student already submitted
    submission = Submission.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_obj.id
    ).first()

    done = bool(submission)  # True if already submitted

    # Form for new submission (only if not already submitted)
    form = ChallengeSubmissionForm() if not done else None

    if form and form.validate_on_submit():
        proof_file = form.proof_file.data
        if proof_file:
            # Save the uploaded file
            filename = secure_filename(proof_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            proof_file.save(filepath)

            # Create submission record
            submission = Submission(
                user_id=current_user.id,
                challenge_id=challenge_obj.id,
                proof_link=filepath,
                status="pending",
            )
            db.session.add(submission)
            db.session.commit()
            done = True
            flash("Submission uploaded successfully!", "success")
            # Reload the page with 'done' status
            return render_template("challenge.html", challenge=challenge_obj, done=done, submission=submission)

    return render_template(
        "challenge.html",
        challenge=challenge_obj,
        form=form,
        done=done,
        submission=submission
    )


# Create a challenge (teachers)
@app.route("/challenge/create", methods=["GET", "POST"])
@login_required
def create_challenge():
    if current_user.role != "teacher":
        flash("Only teachers can create challenges.", "danger")
        return redirect(url_for("dashboard"))

    form = ChallengeForm()
    if form.validate_on_submit():
        challenge = Challenge(
            title=form.title.data,
            description=form.description.data,
            points=form.points.data,
        )
        db.session.add(challenge)
        db.session.commit()
        flash("Challenge created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_challenge.html", form=form)


# Edit a challenge (teachers)
@app.route("/challenge/edit/<int:challenge_id>", methods=["GET", "POST"])
@login_required
def edit_challenge(challenge_id):
    if current_user.role != "teacher":
        flash("Only teachers can edit challenges.", "danger")
        return redirect(url_for("dashboard"))

    challenge = Challenge.query.get_or_404(challenge_id)
    form = ChallengeForm(obj=challenge)

    if form.validate_on_submit():
        challenge.title = form.title.data
        challenge.description = form.description.data
        challenge.points = form.points.data
        db.session.commit()
        flash("Challenge updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_challenge.html", form=form, edit=True)


# Delete a challenge (teachers)
@app.route("/challenge/delete/<int:challenge_id>", methods=["POST"])
@login_required
def delete_challenge(challenge_id):
    if current_user.role != "teacher":
        flash("Only teachers can delete challenges.", "danger")
        return redirect(url_for("dashboard"))

    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    flash("Challenge deleted successfully!", "success")
    return redirect(url_for("dashboard"))


# Review student submissions (teachers)
@app.route("/submission/<int:submission_id>/<action>")
@login_required
def review_submission(submission_id, action):
    if current_user.role != "teacher":
        flash("Only teachers can review submissions.", "danger")
        return redirect(url_for("dashboard"))

    submission = Submission.query.get_or_404(submission_id)
    if action == "approve":
        submission.status = "approved"
        submission.user.eco_points += submission.challenge.points
        flash("Submission approved! Points awarded.", "success")
    elif action == "reject":
        submission.status = "rejected"
        flash("Submission rejected.", "warning")

    db.session.commit()
    return redirect(url_for("dashboard"))

# ---------- QUIZ ----------

# ---------- TAKE QUIZ ----------
@app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)

    if current_user.role == "teacher":
        flash("Teachers cannot take quizzes.", "warning")
        return redirect(url_for("dashboard"))

    # Decode the JSON options
    try:
        options = json.loads(quiz_obj.options)
    except Exception:
        options = []

    # Use Flask-WTF form for CSRF
    form = TakeQuizForm()
    form.answer.choices = [(opt, opt) for opt in options]

    if form.validate_on_submit():
        answer = form.answer.data
        if answer.strip().lower() == quiz_obj.correct_answer.strip().lower():
            current_user.eco_points += quiz_obj.points or 10
            db.session.commit()
            flash(f"Correct! +{quiz_obj.points or 10} Eco Points", "success")
        else:
            flash("Incorrect, try again!", "danger")
        return redirect(url_for("dashboard"))

    return render_template("quiz.html", quiz=quiz_obj, form=form)


# ---------- CREATE QUIZ ----------
@app.route("/quiz/create", methods=["GET", "POST"])
@login_required
def create_quiz():
    if current_user.role != "teacher":
        flash("Only teachers can create quizzes.", "danger")
        return redirect(url_for("dashboard"))

    form = QuizForm()
    modules = Module.query.all()  # Fetch all modules for dropdown

    if form.validate_on_submit():
        module_id = request.form.get("module_id")
        if not module_id:
            flash("Please select a module for this quiz.", "danger")
            return render_template("create_quiz.html", form=form, modules=modules, edit=False)

        quiz = Quiz(
            question=form.question.data,
            options=form.options.data,  # store as JSON string
            correct_answer=form.correct_answer.data,
            points=form.points.data or 10,  # default to 10 if empty
            module_id=int(module_id)
        )
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_quiz.html", form=form, modules=modules, edit=False)


# ---------- EDIT QUIZ ----------
@app.route("/quiz/edit/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def edit_quiz(quiz_id):
    if current_user.role != "teacher":
        flash("Only teachers can edit quizzes.", "danger")
        return redirect(url_for("dashboard"))

    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    modules = Module.query.all()  # Fetch modules for dropdown

    if form.validate_on_submit():
        module_id = request.form.get("module_id")
        if not module_id:
            flash("Please select a module for this quiz.", "danger")
            return render_template("create_quiz.html", form=form, modules=modules, quiz=quiz, edit=True)

        quiz.question = form.question.data
        quiz.options = form.options.data
        quiz.correct_answer = form.correct_answer.data
        quiz.points = form.points.data or 10
        quiz.module_id = int(module_id)  # update module
        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_quiz.html", form=form, modules=modules, quiz=quiz, edit=True)


# ---------- DELETE QUIZ ----------
@app.route("/quiz/delete/<int:quiz_id>")
@login_required
def delete_quiz(quiz_id):
    if current_user.role != "teacher":
        flash("Only teachers can delete quizzes.", "danger")
        return redirect(url_for("dashboard"))

    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for("dashboard"))

# ---------- MINI GAME ----------
@app.route("/game", methods=["GET"])
@login_required
def game():
    return render_template("game.html", coins=current_user.green_coins or 0)


@app.route("/mini_game/add_points", methods=["POST"])
@login_required
def mini_game_add_points():
    if current_user.role != "student":
        flash("Only students can play the mini game.", "danger")
        return redirect(url_for("dashboard"))

    form = GameForm()
    if form.validate_on_submit():
        try:
            coins = int(form.coins.data)
        except (TypeError, ValueError):
            coins = current_user.green_coins

        current_user.green_coins = coins
        db.session.commit()
        flash(f"✅ Your progress has been saved! You now have {coins} Green Coins.", "success")
    else:
        flash("⚠️ Could not save progress (invalid form submission).", "danger")

    return redirect(url_for("game"))


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
