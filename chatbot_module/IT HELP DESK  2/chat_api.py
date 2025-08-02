import os
import jwt
import uuid
import bcrypt
import pyodbc
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS , cross_origin
from datetime import datetime, timedelta
from system_prompt import SYSTEM_PROMPT


load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)


# Azure & JWT credentials
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOIN")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
SECRET_KEY = os.getenv("SECRET_KEY")

# Azure SQL connection
def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
        f"DATABASE={os.getenv('AZURE_SQL_DATABASE')};"
        f"UID={os.getenv('AZURE_SQL_USERNAME')};"
        f"PWD={os.getenv('AZURE_SQL_PASSWORD')}"
    )
    return pyodbc.connect(conn_str)
def get_employee_id_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT EmployeeID FROM Employees WHERE UserID = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_ticket_number(username):
    emp_id = get_employee_id_by_username(username)
    if not emp_id:
        return "No employee found for this user."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 TicketNumber FROM Tickets WHERE OpenedByID = ?", (emp_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "You have not raised any tickets."

def get_ticket_status(username):
    emp_id = get_employee_id_by_username(username)
    if not emp_id:
        return "No employee found for this user."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 StatusCode FROM Tickets WHERE OpenedByID = ?", (emp_id,))
    row = cursor.fetchone()
    conn.close()
    return f"Your ticket status is: {row[0]}" if row else "No ticket found."


# Store for session messages
conversations = {}



# ------------------- Login --------------------
@app.route("/login", methods=["POST"])
@cross_origin()
def login():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Check if username exists in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM dbo.Users WHERE Username = ?", (username,))
    user_exists = cursor.fetchone()
    conn.close()

    if not user_exists:
        return jsonify({"error": "Invalid username"}), 401

    # Generate JWT token
    token = jwt.encode({
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }, SECRET_KEY, algorithm="HS256")

    print("Username received:", username)

    return jsonify({"token": token})

# ------------------- Chat --------------------

@app.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["username"]  # This is the 'UserID' (e.g., michele.jones)

        data = request.get_json()
        session_id = data.get("session_id")
        user_question = data.get("user_message")

        print(f"Username received: {username}")
        print(f"Session: {session_id}")
        print(f"Question: {user_question}")

        if not session_id or not user_question:
            return jsonify({"error": "Missing session_id or user_message"}), 400

        if session_id not in conversations:
            conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]


        # Handle predefined responses
        response = ""
        if user_question.lower() == "my ticket number":
            response = get_ticket_number(username)

        elif user_question.lower() == "my ticket status":
            response = get_ticket_status(username)

        elif user_question.lower() == "how long will it take to resolve my ticket?":
            response = "It usually takes 2–5 business days to resolve a ticket."

        elif user_question.lower() == "hi" or user_question.lower() == "hello":
            response = f"Hi {username.split('.')[0].capitalize()}, how can I help you today?"

        elif user_question.lower() in ["logout", "sign out"]:
            response = "You have been logged out. See you again!"

        else:
            # fallback to default LLM (if applicable)
            response = generate_gpt_response(session_id, user_question)

        conversations[session_id].append({"role": "user", "content": user_question})
        conversations[session_id].append({"role": "assistant", "content": response})

        return jsonify({"response": response})

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print("Chat error:", e)
        return jsonify({"error": "Something went wrong"}), 500

# ✅ GPT generation (new API format)
def generate_gpt_response(session_id, user_msg):
    client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))

    messages = conversations[session_id]
    messages.append({"role": "user", "content": user_msg})
    chat_response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=0.3
    )
    return chat_response.choices[0].message.content


# ------------------- Main --------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
