from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import uuid
import os
import requests

app = Flask(__name__)

# 📁 Output directory
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form["name"].strip()
    school = request.form["school"].strip()
    event = request.form["event"].strip()
    email = request.form["email"].strip()

    GOOGLE_SCRIPT_URL = os.environ.get(
        "https://docs.google.com/spreadsheets/d/1hlZopqrcHKu1asgkLDjTu-wA7DG4OFzJa-pisyaNacE/edit?gid=0#gid=0",
        "https://script.google.com/u/2/home/projects/1H-RqmdPQ7L-f375PZPfSw9yHXOlvn5hQUZWVbaRXc2LERBy_enmLlEuv/edit"
    )

    payload = {
        "name": name,
        "school": school,
        "event": event,
        "email": email,
        "certificate_id": str(uuid.uuid4()),
        "ip": request.remote_addr
    }

    try:
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            json=payload,
            timeout=5
        )
        result = response.json()
    except Exception as e:
        return "Server error. Please try again later.", 500

    # 🚫 BLOCK certificate generation
    if result.get("status") != "valid":
        return (
            "❌ Details do not match our records.<br>"
            "Please check your Name, School, Event, and Email.",
            403
        )

    # ✅ ONLY VALID USERS REACH HERE
    img = Image.open("certificate.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Arial.ttf", 60)

    draw.text((800, 600), name, fill="black", font=font)

    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PDF")

    return send_file(filepath, as_attachment=True)

# ▶ Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
