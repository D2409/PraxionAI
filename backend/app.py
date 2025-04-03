import string
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from PyPDF2 import PdfReader 
from werkzeug.utils import secure_filename
import uuid
import os
import sys
sys.path.append(os.path.abspath("../rag_example"))

from rag_pipeline import get_response, setup_qa_chain  # <- the main function we’ll use


import difflib

# Load environment variables
load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask app setup
app = Flask(
    __name__,
    template_folder=os.path.abspath("../frontend/templates"),
    static_folder=os.path.abspath("../frontend/static")
)

CORS(app, resources={r"/ask": {"origins": "*"}})
CORS(app, resources={r"/setup_chain": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    return response

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'compliance.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

# Compliance Policy model
class CompliancePolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)

# Uploaded Policy model
class UploadedPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Analytics Log model
class AnalyticsLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(1000), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Initialize database
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    print(f"Attempting login for username: {username}")
    print(f"User found in database: {user}")
    print(f"Stored password hash: {user.password if user else None}")

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login successful!"})
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

@app.route('/add_policy', methods=['POST'])
@login_required
def add_policy():
    if current_user.role not in ["admin", "compliance_manager"]:
        return jsonify({"error": "Unauthorized. Admin or Compliance Manager access required."}), 403

    try:
        data = request.json
        question = data.get("question")
        answer = data.get("answer")
        if not question or not answer:
            return jsonify({"error": "Question and Answer are required"}), 400

        policy = CompliancePolicy(question=question, answer=answer)
        db.session.add(policy)
        log = AnalyticsLog(action="add_policy", details=f"Added policy: {question}")
        db.session.add(log)
        db.session.commit()
        return jsonify({"message": "Policy added successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_policy/<int:policy_id>', methods=['PUT'])
@login_required
def edit_policy(policy_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    data = request.json
    question = data.get("question")
    answer = data.get("answer")

    policy = CompliancePolicy.query.get(policy_id)
    if not policy:
        return jsonify({"error": "Policy not found"}), 404

    policy.question = question
    policy.answer = answer
    db.session.commit()
    return jsonify({"message": "Policy updated successfully!"})


@app.route('/delete_policy/<int:policy_id>', methods=['DELETE'])
@login_required
def delete_policy(policy_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    policy = CompliancePolicy.query.get(policy_id)
    if not policy:
        return jsonify({"error": "Policy not found"}), 404

    db.session.delete(policy)
    db.session.commit()

    return jsonify({"message": "Policy deleted successfully!"})

@app.route('/view_policies', methods=['GET'])
@login_required
def view_policies():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    policies = CompliancePolicy.query.all()
    policies_list = [{"id": p.id, "question": p.question, "answer": p.answer} for p in policies]
    return jsonify({"policies": policies_list})

@app.route('/analytics', methods=['GET'])
@login_required
def analytics():
    if current_user.role not in ["admin", "compliance_manager"]:
        return jsonify({"error": "Unauthorized. Admin or Compliance Manager access required."}), 403

    logs = AnalyticsLog.query.all()
    logs_data = [
        {
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "N/A"
        }
        for log in logs
    ]
    return jsonify({"logs": logs_data})

@app.route('/upload_policy', methods=['POST'])
@login_required
def upload_policy():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    try:
        # Read and extract content from PDF
        reader = PdfReader(file)
        content = "".join(page.extract_text() for page in reader.pages)

        # Store policy in database
        uploaded_policy = UploadedPolicy(filename=file.filename, content=content)
        db.session.add(uploaded_policy)
        db.session.commit()

        # Log the upload action
        log = AnalyticsLog(action="upload_policy", details=f"Uploaded policy: {file.filename}")
        db.session.add(log)
        db.session.commit()

        return jsonify({"message": "Policy uploaded successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/view_uploaded_policies', methods=['GET'])
@login_required
def view_uploaded_policies():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    policies = UploadedPolicy.query.all()
    policies_list = [{"id": p.id, "filename": p.filename, "content": p.content[:200]} for p in policies]
    return jsonify({"uploaded_policies": policies_list})

@app.route('/delete_uploaded_policy/<int:policy_id>', methods=['DELETE'])
@login_required
def delete_uploaded_policy(policy_id):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    policy = UploadedPolicy.query.get(policy_id)
    if not policy:
        return jsonify({"error": "Policy not found"}), 404

    db.session.delete(policy)
    db.session.commit()

    # Log the delete action
    log = AnalyticsLog(action="delete_policy", details=f"Deleted policy ID: {policy_id}")
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Policy deleted successfully!"})

@app.route('/')
def index():
    return render_template("index.html")

# Route to render the main page
@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a valid message."})

    # Use the RAG-based function to get a smart response
    # bot_response = get_response(user_message)
    bot_response = get_response(user_message)

    return jsonify({"response": bot_response})

@app.route('/upload', methods=['GET'])
def upload_interface():
    # Render an HTML template that includes a file/directory picker
    return render_template('upload.html')

# Define a base directory for temporary uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "temp_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/setup_chain", methods=["POST"])
def setup_chain():
    """
    Receives aggregated PDF files from a folder (via FormData),
    saves them into a temporary directory, and calls setup_qa_chain.
    """
    uploaded_files = request.files.getlist("pdf_files")
    if not uploaded_files:
        return jsonify({"error": "No files received."}), 400

    # Create a unique temporary folder for this upload session
    session_folder = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(session_folder, exist_ok=True)

    # Save each uploaded file to the temporary folder
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(session_folder, filename))

    try:
        # Call your RAG pipeline function which expects a directory of PDFs
        setup_qa_chain(session_folder)
        saved_files = os.listdir(session_folder)
        return jsonify({
            "message": f"Successfully uploaded {len(saved_files)} file(s) and set up QA chain."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


""" 
@app.route('/debug_message', methods=['POST'])
def debug_message():
    data = request.json
    user_message = data.get("message", "").strip().lower()

    print("\n=== DEBUGGING START ===")
    print("Raw input:", data)
    print("user_message (repr):", repr(user_message))

    sample_qa = {
        "how do i report misconduct": "You can report misconduct anonymously through the Ethics Hotline.",
        "what is the company's harassment policy": "The company follows a strict zero-tolerance policy towards workplace harassment.",
        "can i accept gifts from vendors": "Accepting gifts, bribes, or personal favors from vendors or clients is prohibited.",
        "is compliance training mandatory": "Yes, all employees must complete annual ethics and compliance training."
    }

    print("\nChecking keys:")
    for key in sample_qa:
        print(">", repr(key))
        if user_message == key:
            print("Matched this key!")

    print("=== DEBUGGING END ===\n")

    return jsonify({"user_message": user_message})

"""

if __name__ == '__main__':
    app.run(debug=True)

