from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from models import db, User, MoodEntry, ChatMessage

import os


# ==========================================
# APP CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = "mindcare-ai-secret-key-2026"


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "mindcare.db"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + DATABASE_PATH
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# SIGNUP
# ==========================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        if not username or not email or not password:

            return render_template(
                "signup.html",
                error="Please fill all fields."
            )


        if len(password) < 6:

            return render_template(
                "signup.html",
                error="Password must contain at least 6 characters."
            )


        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()


        if existing_user:

            return render_template(
                "signup.html",
                error="Username or email already exists."
            )


        new_user = User(
            username=username,
            email=email
        )

        new_user.set_password(password)


        db.session.add(new_user)

        db.session.commit()


        session.clear()

        session["user_id"] = new_user.id

        session["username"] = new_user.username


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "signup.html"
    )


# ==========================================
# LOGIN
# ==========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        user = User.query.filter_by(
            email=email
        ).first()


        if user is None:

            return render_template(
                "login.html",
                error="Invalid email or password."
            )


        if not user.check_password(password):

            return render_template(
                "login.html",
                error="Invalid email or password."
            )


        session.clear()

        session["user_id"] = user.id

        session["username"] = user.username


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "login.html"
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "dashboard.html"
    )


# ==========================================
# AI CHAT
# ==========================================

@app.route(
    "/chat",
    methods=["GET", "POST"]
)
def chat():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        user_message = request.form.get(
            "message",
            ""
        ).strip()


        if user_message:

            message = user_message.lower()


            # ==================================
            # SAFETY RESPONSE
            # ==================================

            if any(word in message for word in [
                "suicide",
                "kill myself",
                "want to die",
                "end my life",
                "hurt myself",
                "self harm"
            ]):

                response = (
                    "I'm really sorry you're going through "
                    "such a difficult moment. 💙 Please reach "
                    "out to someone you trust or a qualified "
                    "mental-health professional. If you are "
                    "in immediate danger, contact your local "
                    "emergency service."
                )


            # ==================================
            # SAD / LOW MOOD
            # ==================================

            elif any(word in message for word in [
                "not good",
                "not okay",
                "not well",
                "feeling bad",
                "feel bad",
                "sad",
                "unhappy",
                "depressed",
                "crying",
                "cry",
                "feeling low",
                "feel low",
                "down",
                "lonely",
                "alone"
            ]):

                response = (
                    "I'm sorry you're feeling this way. 💙 "
                    "I'm here to listen. You don't have to "
                    "handle everything alone. Would you like "
                    "to tell me what's troubling you?"
                )


            # ==================================
            # STRESS
            # ==================================

            elif any(word in message for word in [
                "stress",
                "stressed",
                "pressure",
                "overwhelmed",
                "tension",
                "too much work"
            ]):

                response = (
                    "It sounds like you're dealing with a lot "
                    "right now. 💙 Take a slow breath and give "
                    "yourself a small break. You can also try "
                    "the Stress Relief section for a breathing "
                    "exercise."
                )


            # ==================================
            # ANXIETY
            # ==================================

            elif any(word in message for word in [
                "anxiety",
                "anxious",
                "worried",
                "worry",
                "nervous",
                "panic",
                "scared",
                "fear"
            ]):

                response = (
                    "It's understandable to feel anxious "
                    "sometimes. 💙 Try taking a few slow, "
                    "comfortable breaths and focus on the "
                    "present moment. I'm here if you want "
                    "to talk about what's worrying you."
                )


            # ==================================
            # ANGER
            # ==================================

            elif any(word in message for word in [
                "angry",
                "anger",
                "mad",
                "furious",
                "irritated",
                "annoyed"
            ]):

                response = (
                    "It sounds like something has really "
                    "frustrated you. 💙 Take a moment to "
                    "breathe and give yourself some space. "
                    "If you'd like, tell me what happened."
                )


            # ==================================
            # HAPPY
            # ==================================

            elif any(word in message for word in [
                "happy",
                "feeling good",
                "feeling great",
                "doing good",
                "doing great",
                "wonderful",
                "excited",
                "joy",
                "joyful",
                "amazing"
            ]):

                response = (
                    "That's wonderful to hear! 😊 "
                    "I'm glad you're feeling positive. "
                    "What's making you feel happy today?"
                )


            # ==================================
            # GREETING
            # ==================================

            elif any(word in message for word in [
                "hello",
                "hi",
                "hey"
            ]):

                response = (
                    "Hello! 💙 I'm MindCare AI. "
                    "I'm here to listen. How are you "
                    "feeling today?"
                )


            # ==================================
            # THANK YOU
            # ==================================

            elif any(word in message for word in [
                "thank you",
                "thanks"
            ]):

                response = (
                    "You're welcome. 💙 I'm always here "
                    "to listen and support you."
                )


            # ==================================
            # DEFAULT RESPONSE
            # ==================================

            else:

                response = (
                    "Thank you for sharing that with me. 💙 "
                    "I'm listening. Tell me a little more "
                    "about what you're experiencing."
                )


            # ==================================
            # SAVE USER MESSAGE
            # ==================================

            user_chat = ChatMessage(
                user_id=session["user_id"],
                sender="user",
                message=user_message
            )

            db.session.add(user_chat)


            # ==================================
            # SAVE AI RESPONSE
            # ==================================

            ai_chat = ChatMessage(
                user_id=session["user_id"],
                sender="ai",
                message=response
            )

            db.session.add(ai_chat)

            db.session.commit()


            return redirect(
                url_for("chat")
            )


    # ==========================================
    # LOAD CHAT HISTORY
    # ==========================================

    chat_history = ChatMessage.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        ChatMessage.created_at.asc()
    ).all()


    return render_template(
        "chat.html",
        chat_history=chat_history
    )


# ==========================================
# MOOD TRACKING
# ==========================================

@app.route(
    "/mood",
    methods=["GET", "POST"]
)
def mood():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        selected_mood = request.form.get(
            "mood",
            ""
        ).strip()

        note = request.form.get(
            "note",
            ""
        ).strip()


        if selected_mood:

            mood_entry = MoodEntry(
                user_id=session["user_id"],
                mood=selected_mood,
                note=note
            )

            db.session.add(mood_entry)

            db.session.commit()


        return redirect(
            url_for("mood")
        )


    entries = MoodEntry.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        MoodEntry.created_at.desc()
    ).all()


    return render_template(
        "mood.html",
        entries=entries
    )


# ==========================================
# STRESS RELIEF
# ==========================================

@app.route("/stress-relief")
def stress_relief():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "stress_relief.html"
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ==========================================
# CREATE DATABASE
# ==========================================

with app.app_context():

    db.create_all()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )