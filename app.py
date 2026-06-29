# import json
# import os
# import datetime
# from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# app = Flask(__name__)
# app.secret_key = "memorylog_secret_key"
# DB_FILE = "database.json"

# # ==================================================
# # DATABASE HELPERS
# # ==================================================

# def load_db():
#     if not os.path.exists(DB_FILE):
#         data = {"users": {}, "history": []}
#         save_db(data)
#         return data
#     with open(DB_FILE, "r") as f:
#         return json.load(f)

# def save_db(data):
#     with open(DB_FILE, "w") as f:
#         json.dump(data, f, indent=4)

# # ==================================================
# # SCORE TREND ANALYSIS
# # ==================================================

# def analyze_score_trends(history):
#     scores = [h["score"] for h in history]

#     if len(scores) < 5:
#         return None

#     recent = scores[:4]
#     older = scores[4:8]

#     if len(older) < 4:
#         return None

#     avg_recent = sum(recent) / len(recent)
#     avg_older = sum(older) / len(older)

#     drop = avg_older - avg_recent

#     if drop > 20:
#         return "danger"
#     elif drop > 10:
#         return "warning"
#     return None

# # ==================================================
# # DEMENTIA ASSESSMENT + RECOMMENDATIONS
# # ==================================================

# def assess_dementia_stage(answers, recent_scores):
#     question_score = sum(answers)
#     avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 100

#     total_risk = question_score

#     if avg_score < 40:
#         total_risk += 6
#     elif avg_score < 60:
#         total_risk += 4
#     elif avg_score < 75:
#         total_risk += 2

#     if total_risk <= 6:
#         return "Normal"
#     elif total_risk <= 12:
#         return "Mild Cognitive Symptons"
#     elif total_risk <= 18:
#         return "Moderate Dementia"
#     else:
#         return "Severe Dementia"

# def get_recommendations(stage):
#     rec = {
#         "Normal": [
#             "Maintain regular physical and mental activities.",
#             "Continue daily memory and attention exercises.",
#             "Ensure proper sleep, nutrition, and hydration.",
#             "Stay socially active and mentally engaged."
#         ],
#         "Mild Cognitive Impairment": [
#             "Increase frequency of cognitive exercises.",
#             "Maintain a structured daily routine.",
#             "Reduce stress and improve sleep quality.",
#             "Consult a healthcare professional for baseline evaluation.",
#             "Family or caregiver monitoring is recommended."
#         ],
#         "Moderate Dementia": [
#             "Consult a neurologist or geriatric specialist.",
#             "Caregiver supervision is advised for daily tasks.",
#             "Use reminders, notes, and alarms for orientation.",
#             "Avoid independent financial decisions or driving.",
#             "Continue cognitive exercises under supervision."
#         ],
#         "Severe Dementia": [
#             "Immediate medical supervision is strongly advised.",
#             "Full-time caregiver support may be required.",
#             "Ensure a safe and controlled living environment.",
#             "Focus on comfort, routine, and emotional well-being.",
#             "Regular medical follow-ups are essential."
#         ]
#     }
#     return rec.get(stage, [])

# # ==================================================
# # AUTH ROUTES
# # ==================================================

# @app.route("/")
# def home():
#     if "user" in session:
#         return redirect(url_for("dashboard"))
#     return render_template("landing.html")

# @app.route("/login_form")
# def login_form():
#     return render_template("index.html")

# @app.route("/login", methods=["POST"])
# def login():
#     username = request.form.get("username")
#     password = request.form.get("password")

#     data = load_db()
#     user = data["users"].get(username)

#     if user and user["password"] == password:
#         session["user"] = username
#         session["role"] = user["role"]

#         if user["role"] == "caregiver":
#             return redirect(url_for("caregiver_portal"))
#         if user["role"] == "admin":
#             return redirect(url_for("admin_portal"))

#         return redirect(url_for("dashboard"))

#     return render_template("index.html", error="Invalid username or password")

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "GET":
#         return render_template("register.html")

#     username = request.form.get("username")
#     password = request.form.get("password")
#     role = request.form.get("role")
#     patient_link = request.form.get("patient_link", "").strip()

#     data = load_db()

#     if username in data["users"]:
#         return render_template("register.html", error="User already exists")

#     data["users"][username] = {
#         "password": password,
#         "role": role,
#         "linked_patient": patient_link if role == "caregiver" else None
#     }

#     save_db(data)
#     return render_template("index.html", success="Account created successfully")

# # ==================================================
# # USER DASHBOARD
# # ==================================================

# @app.route("/dashboard")
# def dashboard():
#     if "user" not in session:
#         return redirect(url_for("home"))

#     data = load_db()
#     user = session["user"]

#     history = [h for h in data["history"] if h["username"] == user]
#     history.reverse()

#     last_test_days = None
#     last_test_date = "N/A"

#     if history:
#         last_test_date = history[0]["date"]
#         try:
#             last_dt = datetime.datetime.strptime(last_test_date, "%Y-%m-%d %H:%M")
#             last_test_days = (datetime.datetime.now() - last_dt).days
#         except:
#             pass

#     alert_status = analyze_score_trends(history)

#     return render_template(
#         "dashboard.html",
#         user=user,
#         history=history,
#         last_test_days=last_test_days,
#         last_test_date=last_test_date,
#         alert_status=alert_status
#     )

# # ==================================================
# # ASSESSMENT SUBMISSION
# # ==================================================

# @app.route("/assessment", methods=["POST"])
# def assessment():
#     if "user" not in session:
#         return redirect(url_for("home"))

#     answers = [int(request.form.get(f"q{i}")) for i in range(1, 11)]

#     data = load_db()

#     scores = [h["score"] for h in data["history"]
#               if h["username"] == session["user"]]
#     recent_scores = scores[-3:]

#     stage = assess_dementia_stage(answers, recent_scores)
#     recommendations = get_recommendations(stage)

#     # SAVE assessment for caregiver access
#     data["users"][session["user"]]["assessment"] = {
#         "stage": stage,
#         "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#     }
#     save_db(data)

#     session["assessment_result"] = stage
#     session["assessment_recommendations"] = recommendations

#     return redirect(url_for("dashboard"))

# # ==================================================
# # CAREGIVER PORTAL
# # ==================================================

# @app.route("/caregiver")
# def caregiver_portal():
#     if session.get("role") != "caregiver":
#         return redirect(url_for("home"))

#     data = load_db()
#     caregiver = data["users"].get(session["user"])
#     patient = caregiver.get("linked_patient")

#     patients = {}

#     if patient and patient in data["users"]:
#         history = [h for h in data["history"] if h["username"] == patient]
#         history.reverse()

#         last_test_days = None
#         if history:
#             try:
#                 last_dt = datetime.datetime.strptime(history[0]["date"], "%Y-%m-%d %H:%M")
#                 last_test_days = (datetime.datetime.now() - last_dt).days
#             except:
#                 pass

#         alert_status = analyze_score_trends(history)

#         assessment = data["users"][patient].get("assessment")
#         stage = assessment["stage"] if assessment else None
#         recommendations = get_recommendations(stage) if stage else []

#         patients[patient] = {
#             "history": history,
#             "last_test_days": last_test_days,
#             "alert_status": alert_status,
#             "stage": stage,
#             "recommendations": recommendations
#         }

#     return render_template("caregiver.html", patients=patients)

# # ==================================================
# # ADMIN PORTAL (BASIC)
# # ==================================================

# @app.route("/admin")
# def admin_portal():
#     if session.get("role") != "admin":
#         return redirect(url_for("home"))

#     data = load_db()
#     users = [{"username": u, **info} for u, info in data["users"].items()]
#     return render_template("admin.html", users=users)

# # ==================================================
# # GAMES
# # ==================================================

# @app.route("/test/matching")
# def test_matching():
#     return render_template("test.html")

# @app.route("/test/words")
# def test_words():
#     return render_template("test_words.html")

# @app.route("/test/pattern")
# def test_pattern():
#     return render_template("test_pattern.html")

# @app.route("/submit_score", methods=["POST"])
# def submit_score():
#     if "user" not in session:
#         return jsonify({"status": "error"})

#     data = load_db()

#     data["history"].append({
#         "username": session["user"],
#         "game": request.json.get("game"),
#         "score": request.json.get("score"),
#         "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#     })

#     save_db(data)
#     return jsonify({"status": "success"})

# # ==================================================
# # LOGOUT
# # ==================================================

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("home"))

# # ==================================================
# # RUN APP
# # ==================================================

# if __name__ == "__main__":
#     app.run(debug=True)

# import json
# import os
# import datetime
# import threading
# import time

# from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# # SMS
# from twilio.rest import Client

# # Reminder scheduler
# import schedule

# app = Flask(__name__)
# app.secret_key = "memorylog_secret_key"
# DB_FILE = "database.json"

# # ==============================
# # TWILIO CONFIG (PUT YOUR KEYS)
# # ==============================
# account_sid = "YOUR_SID"
# auth_token = "YOUR_TOKEN"
# twilio_number = "+1234567890"
# client = Client(account_sid, auth_token)

# # ==============================
# # DATABASE HELPERS
# # ==============================
# def load_db():
#     if not os.path.exists(DB_FILE):
#         data = {"users": {}, "history": []}
#         save_db(data)
#         return data
#     with open(DB_FILE, "r") as f:
#         return json.load(f)

# def save_db(data):
#     with open(DB_FILE, "w") as f:
#         json.dump(data, f, indent=4)

# # ==============================
# # REMINDER SYSTEM
# # ==============================
# def send_reminder():
#     print("🔔 Reminder triggered!")

# schedule.every().day.at("09:00").do(send_reminder)

# def run_scheduler():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# threading.Thread(target=run_scheduler, daemon=True).start()

# # ==============================
# # HOME
# # ==============================
# @app.route("/")
# def home():
#     return render_template("landing.html", logged_in=("user" in session))
# # ==============================
# # LOGIN / REGISTER
# # ==============================
# @app.route("/login_form")
# def login_form():
#     return render_template("index.html")

# @app.route("/login", methods=["POST"])
# def login():
#     data = load_db()
#     username = request.form.get("username")
#     password = request.form.get("password")

#     user = data["users"].get(username)

#     if user and user["password"] == password:
#         session["user"] = username
#         session["role"] = user["role"]

#         if user["role"] == "caregiver":
#             return redirect(url_for("caregiver_portal"))
#         if user["role"] == "admin":
#             return redirect(url_for("admin_portal"))

#         return redirect(url_for("dashboard"))

#     return render_template("index.html", error="Invalid credentials")

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "GET":
#         return render_template("register.html")

#     data = load_db()
#     username = request.form.get("username")

#     if username in data["users"]:
#         return render_template("register.html", error="User exists")

#     data["users"][username] = {
#         "password": request.form.get("password"),
#         "role": request.form.get("role"),
#         "linked_patient": request.form.get("patient_link")
#     }

#     save_db(data)
#     return redirect(url_for("login_form"))

# # ==============================
# # DASHBOARD
# # ==============================
# # @app.route("/dashboard")
# # def dashboard():
# #     if "user" not in session:
# #         return redirect(url_for("home"))

# #     data = load_db()
# #     user = session["user"]

# #     history = [h for h in data["history"] if h["username"] == user]
# #     history.reverse()

# #     # ✅ ADD THIS
# #     last_test_days = None

# #     if history:
# #         try:
# #             last_date = datetime.datetime.strptime(history[0]["date"], "%Y-%m-%d %H:%M")
# #             last_test_days = (datetime.datetime.now() - last_date).days
# #         except:
# #             pass

# #     return render_template(
# #         "dashboard.html",
# #         user=user,
# #         history=history,
# #         last_test_days=last_test_days
# #     )
# @app.route("/dashboard")
# def dashboard():

#     if "user" not in session:
#         return redirect(url_for("home"))

#     data = load_db()

#     user = session["user"]

#     history = [
#         h for h in data["history"]
#         if h["username"] == user
#     ]

#     history.reverse()

#     last_test_days = None

#     if history:

#         try:

#             last_date = datetime.datetime.strptime(
#                 history[0]["date"],
#                 "%Y-%m-%d %H:%M"
#             )

#             last_test_days = (
#                 datetime.datetime.now() - last_date
#             ).days

#         except:
#             pass

#     # ADD THIS
#     alert_status = None

#     scores = [h["score"] for h in history]

#     if len(scores) >= 4:

#         recent_avg = sum(scores[:2]) / 2
#         old_avg = sum(scores[2:4]) / 2

#         drop = old_avg - recent_avg

#         if drop > 20:
#             alert_status = "danger"

#         elif drop > 10:
#             alert_status = "warning"

#     return render_template(

#         "dashboard.html",

#         user=user,

#         history=history,

#         last_test_days=last_test_days,

#         alert_status=alert_status
#     )

# # ==============================
# # GAMES ROUTES
# # ==============================

# @app.route("/test/matching")
# def test_matching():
#     return render_template("test.html")

# @app.route("/test/words")
# def test_words():
#     return render_template("test_words.html")

# @app.route("/test/pattern")
# def test_pattern():
#     return render_template("test_pattern.html")

# # ==============================
# # SUBMIT SCORE
# # ==============================
# @app.route("/submit_score", methods=["POST"])
# def submit_score():
#     if "user" not in session:
#         return jsonify({"status": "error"})

#     data = load_db()

#     data["history"].append({
#         "username": session["user"],
#         "game": request.json.get("game"),
#         "score": request.json.get("score"),
#         "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#     })

#     save_db(data)
#     return jsonify({"status": "success"})

# # ==============================
# # CAREGIVER PORTAL (UPDATED)
# # ==============================
# # @app.route("/caregiver")
# # def caregiver_portal():
# #     if session.get("role") != "caregiver":
# #         return redirect(url_for("home"))

# #     data = load_db()
# #     caregiver = data["users"][session["user"]]
# #     patient = caregiver.get("linked_patient")

# #     patient_data = data["users"].get(patient)

# #     return render_template(
# #         "caregiver.html",
# #         patient=patient,
# #         patient_data=patient_data,
# #         history=[h for h in data["history"] if h["username"] == patient]
# #     )

# @app.route("/caregiver")
# def caregiver_portal():

#     if session.get("role") != "caregiver":
#         return redirect(url_for("home"))

#     data = load_db()

#     caregiver = data["users"].get(session["user"])

#     patient = caregiver.get("linked_patient")

#     patients = {}

#     if patient and patient in data["users"]:

#         history = [

#             h for h in data["history"]

#             if h["username"] == patient
#         ]

#         history.reverse()

#         last_test_days = None

#         if history:

#             try:

#                 last_dt = datetime.datetime.strptime(

#                     history[0]["date"],
#                     "%Y-%m-%d %H:%M"
#                 )

#                 last_test_days = (

#                     datetime.datetime.now() - last_dt
#                 ).days

#             except:
#                 pass

#         alert_status = None

#         scores = [h["score"] for h in history]

#         if len(scores) >= 4:

#             recent_avg = sum(scores[:2]) / 2
#             old_avg = sum(scores[2:4]) / 2

#             drop = old_avg - recent_avg

#             if drop > 20:
#                 alert_status = "danger"

#             elif drop > 10:
#                 alert_status = "warning"

#         assessment = data["users"][patient].get("assessment")

#         stage = assessment["stage"] if assessment else None

#         recommendations = []

#         patients[patient] = {

#     "history": history,

#     "last_test_days": last_test_days,

#     "alert_status": alert_status,

#     "stage": stage,

#     "recommendations": recommendations,

#     "assessment_result": data["users"][patient].get("assessment_result", 0),

#     "location": data["users"][patient].get("location")

# }

#     return render_template(
#         "caregiver.html",
#         patients=patients
#     )

# @app.route("/save_location", methods=["POST"])
# def save_location():

#     if "user" not in session:
#         return jsonify({"status":"error"})

#     data = load_db()

#     user = session["user"]

#     location_data = request.get_json()

#     latitude = location_data.get("latitude")
#     longitude = location_data.get("longitude")

#     # SAVE LOCATION

#     data["users"][user]["location"] = {

#         "latitude": latitude,
#         "longitude": longitude

#     }

#     save_db(data)

#     return jsonify({

#         "status":"success"

#     })
# # ==============================
# # ADMIN
# # ==============================
# @app.route("/admin")
# def admin_portal():
#     data = load_db()
#     return render_template("admin.html", users=data["users"])



# # ==============================
# # LOGOUT
# # ==============================
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("home"))


# @app.route("/assessment", methods=["POST"])
# def assessment():

#     total_score = 0

#     for i in range(1, 11):

#         answer = request.form.get(f"q{i}")

#         if answer:

#             total_score += int(answer)

#     session["assessment_result"] = total_score

#     return redirect("/dashboard")

# # ==============================
# # RUN
# # ==============================
# if __name__ == "__main__":
#     app.run(debug=True)

from db import *

import datetime
import threading
import time

from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import schedule

app = Flask(__name__)

app.secret_key = "memorylog_secret_key"

# ==============================
# REMINDER SYSTEM
# ==============================

def send_reminder():
    print("🔔 Reminder triggered!")

schedule.every().day.at("09:00").do(send_reminder)

def run_scheduler():

    while True:

        schedule.run_pending()

        time.sleep(1)

threading.Thread(
    target=run_scheduler,
    daemon=True
).start()

# ==============================
# HOME
# ==============================

@app.route("/")
def home():

    return render_template(
        "landing.html",
        logged_in=("user" in session)
    )

# ==============================
# LOGIN
# ==============================

@app.route("/login_form")
def login_form():

    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")

    password = request.form.get("password")

    user = users_collection.find_one({

        "username": username

    })

    if user and user["password"] == password:

        session["user"] = username

        session["role"] = user["role"]

        if user["role"] == "caregiver":
            return redirect("/caregiver")

        if user["role"] == "admin":
            return redirect("/admin")

        return redirect("/dashboard")

    return render_template(

        "index.html",

        error="Invalid credentials"

    )

# ==============================
# REGISTER
# ==============================

# @app.route("/register", methods=["GET", "POST"])
# def register():

#     if request.method == "GET":

#         return render_template("register.html")

#     username = request.form.get("username")

#     existing = users_collection.find_one({

#         "username": username

#     })

#     if existing:

#         return render_template(

#             "register.html",

#             error="User already exists"

#         )

#     users_collection.insert_one({

#         "username": username,

#         "password": request.form.get("password"),

#         "role": request.form.get("role"),

#         "linked_patient": request.form.get("patient_link"),

#         "assessment_result": 0

#     })

#     return redirect("/login_form")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")

    username = request.form.get("username")

    password = request.form.get("password")

    role = request.form.get("role")

    existing = users_collection.find_one({

        "username": username

    })

    if existing:

        return render_template(

            "register.html",

            error="User already exists"

        )

    user_data = {

        "username": username,

        "password": password,

        "role": role,

        "assessment_result": 0

    }

    # MULTIPLE PATIENT SUPPORT

    if role == "caregiver":

        linked_patients = request.form.get(

            "linked_patient"

        )

        if linked_patients:

            patient_list = [

                p.strip()

                for p in linked_patients.split(",")

            ]

            user_data["linked_patients"] = patient_list

    users_collection.insert_one(user_data)

    return redirect("/login_form")
# ==============================
# PATIENT DASHBOARD
# ==============================

# @app.route("/dashboard")
# def dashboard():

#     if "user" not in session:
#         return redirect("/")

#     user = session["user"]

#     history = list(

#         history_collection.find({

#             "username": user

#         })

#     )

#     history.reverse()

#     # LAST TEST DAYS

#     last_test_days = None

#     if history:

#         try:

#             last_date = datetime.datetime.strptime(

#                 history[0]["date"],
#                 "%Y-%m-%d %H:%M"

#             )

#             last_test_days = (

#                 datetime.datetime.now() - last_date

#             ).days

#         except:
#             pass

#     # ALERT STATUS

#     alert_status = None

#     scores = [h["score"] for h in history]

#     if len(scores) >= 4:

#         recent_avg = sum(scores[:2]) / 2

#         old_avg = sum(scores[2:4]) / 2

#         drop = old_avg - recent_avg

#         if drop > 20:

#             alert_status = "danger"

#         elif drop > 10:

#             alert_status = "warning"

#     return render_template(

#         "dashboard.html",

#         user=user,

#         history=history,

#         last_test_days=last_test_days,

#         alert_status=alert_status

#     )
# ==============================
# PATIENT DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    # CHECK LOGIN

    if "user" not in session:

        return redirect("/")

    user = session["user"]

    # GET HISTORY

    history = list(

        history_collection.find({

            "username": user

        })

    )

    # REMOVE OBJECT IDs

    for item in history:

        item["_id"] = str(item["_id"])

    # LATEST FIRST

    history.reverse()

    # LAST TEST DAYS

    last_test_days = None

    if history:

        try:

            last_date = datetime.datetime.strptime(

                history[0]["date"],
                "%Y-%m-%d %H:%M"

            )

            last_test_days = (

                datetime.datetime.now() - last_date

            ).days

        except:
            pass

    # ALERT STATUS

    alert_status = None

    scores = [

        h.get("score",0)

        for h in history

    ]

    if len(scores) >= 4:

        recent_avg = sum(scores[:2]) / 2

        old_avg = sum(scores[2:4]) / 2

        drop = old_avg - recent_avg

        if drop > 20:

            alert_status = "danger"

        elif drop > 10:

            alert_status = "warning"

        else:

            alert_status = "good"

    # USER DATA

    user_data = users_collection.find_one({

        "username": user

    })

    assessment_result = 0

    location = None

    if user_data:

        assessment_result = user_data.get(

            "assessment_result",
            0

        )

        location = user_data.get(

            "location"
        )

    return render_template(

        "dashboard.html",

        user=user,

        history=history,

        last_test_days=last_test_days,

        alert_status=alert_status,

        assessment_result=assessment_result,

        location=location

    )
# ==============================
# GAMES
# ==============================

@app.route("/test/matching")
def test_matching():

    return render_template("test.html")

@app.route("/test/words")
def test_words():

    return render_template("test_words.html")

@app.route("/test/pattern")
def test_pattern():

    return render_template("test_pattern.html")

# ==============================
# SUBMIT SCORE
# ==============================

@app.route("/submit_score", methods=["POST"])
def submit_score():

    if "user" not in session:

        return jsonify({

            "status":"error"

        })

    history_collection.insert_one({

        "username": session["user"],

        "game": request.json.get("game"),

        "score": request.json.get("score"),

        "date": datetime.datetime.now().strftime(

            "%Y-%m-%d %H:%M"

        )

    })

    return jsonify({

        "status":"success"

    })

# ==============================
# ASSESSMENT
# ==============================

@app.route("/assessment", methods=["POST"])
def assessment():

    total_score = 0

    for i in range(1,11):

        total_score += int(

            request.form.get(f"q{i}",0)

        )

    users_collection.update_one(

        {

            "username": session["user"]

        },

        {

            "$set": {

                "assessment_result": total_score

            }

        }

    )

    session["assessment_result"] = total_score

    return redirect("/dashboard")

# ==============================
# SAVE LOCATION
# ==============================

@app.route("/save_location", methods=["POST"])
def save_location():

    if "user" not in session:

        return jsonify({

            "status":"error"

        })

    data = request.get_json()

    users_collection.update_one(

        {

            "username": session["user"]

        },

        {

            "$set": {

                "location": {

                    "latitude": data.get("latitude"),

                    "longitude": data.get("longitude")

                }

            }

        }

    )

    return jsonify({

        "status":"success"

    })

# ==============================
# CAREGIVER
# ==============================
@app.route("/caregiver")
def caregiver_portal():

    if "user" not in session:
        return redirect("/")

    if session.get("role") != "caregiver":
        return redirect("/")

    caregiver = users_collection.find_one({

        "username": session["user"]

    })

    if not caregiver:
        return redirect("/logout")

    linked_patients = caregiver.get(

        "linked_patients",
        []

    )

    patients = {}

    for linked_patient in linked_patients:

        patient_data = users_collection.find_one({

            "username": linked_patient

        })

        if patient_data:

            # HISTORY

            history = []

            records = history_collection.find({

                "username": linked_patient

            })

            for item in records:

                history.append({

                    "game": item.get("game"),

                    "score": item.get("score"),

                    "date": item.get("date")

                })

            history.reverse()

            # LAST TEST DAYS

            last_test_days = None

            if history:

                try:

                    last_date = datetime.datetime.strptime(

                        history[0]["date"],
                        "%Y-%m-%d %H:%M"

                    )

                    last_test_days = (

                        datetime.datetime.now() - last_date

                    ).days

                except:
                    pass

            # LOCATION

            location = None

            if patient_data.get("location"):

                location = {

                    "latitude":
                    patient_data["location"].get("latitude"),

                    "longitude":
                    patient_data["location"].get("longitude")

                }

            # SAVE

            patients[linked_patient] = {

                "history": history,

                "assessment_result":
                patient_data.get(
                    "assessment_result",
                    0
                ),

                "location": location,

                "last_test_days":
                last_test_days

            }

    return render_template(

        "caregiver.html",

        patients=patients

    )
#==============================
# ADMIN
# ==============================

@app.route("/admin")
def admin_portal():

    # LOGIN REQUIRED

    if "user" not in session:

        return redirect("/")

    # ONLY ADMIN ACCESS

    if session.get("role") != "admin":

        return redirect("/dashboard")

    users = {}

    records = users_collection.find()

    for user in records:

        users[user["username"]] = {

            "username": user.get("username"),

            "role": user.get("role"),

            "linked_patient":
            user.get("linked_patient","-")

        }

    return render_template(

        "admin.html",

        users=users

    )

# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ==============================
# RUN
# ==============================

if __name__ == "__main__":

    app.run(debug=True)