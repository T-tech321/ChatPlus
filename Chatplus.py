from flask import Flask, request, jsonify, render_template, redirect, url_for
import threading, time, json, os, torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from langdetect import detect

app = Flask(__name__)
users_file = "users.json"

# ---------------------------
# Load GPT-2 Model
# ---------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
model.eval()

# ---------------------------
# Shared context
# ---------------------------
context = ""

# ---------------------------
# AI Generate Function
# ---------------------------
def ai_generate(prompt, max_length=200):
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if text.startswith(prompt):
            text = text[len(prompt):].strip()
        return text
    except Exception as e:
        print("AI generation error:", e)
        return "Error generating response."

# ---------------------------
# User management
# ---------------------------
def load_users():
    if not os.path.exists(users_file):
        return {}
    with open(users_file, "r") as f:
        return json.load(f)

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = load_users()
    username = data.get("username")
    if username in users:
        return jsonify({"status":"error","message":"Username taken"})
    users[username] = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "password": data.get("password"),
        "dob": data.get("dob")
    }
    save_users(users)
    return jsonify({"status":"ok"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()
    username = data.get("username")
    password = data.get("password")
    if username in users and users[username]["password"] == password:
        return jsonify({"status":"ok"})
    return jsonify({"status":"error","message":"Invalid credentials"})

# ---------------------------
# Chat Endpoint
# ---------------------------
@app.route("/chat", methods=["POST"])
def chat():
    global context
    data = request.json
    user_msg = data.get("message", "")
    lang = detect(user_msg)
    context += f"\nUser: {user_msg}\nAI: "
    ai_response = ai_generate(context)
    context += ai_response
    return jsonify({"response": ai_response})

# ---------------------------
# Background Self-Improvement
# ---------------------------
def background_self_improvement():
    global context
    while True:
        try:
            prompt = "Self-reflection: "
            response = ai_generate(prompt, max_length=150)
            context += f"\nAI Self-Reflection: {response}"
        except Exception as e:
            print("Background improvement error:", e)
        time.sleep(60)

threading.Thread(target=background_self_improvement, daemon=True).start()

# ---------------------------
# Web Interface
# ---------------------------
@app.route("/")
def index():
    return render_template("chat.html")

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
