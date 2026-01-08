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
    name = request.form.get("name")
    school = request.form.get("school")
    event = request.form.get("event")
    email = request.form.get("email")

    # 🔗 Google Apps Script URL
    GOOGLE_SCRIPT_URL = os.environ.get(
        "GOOGLE_SHEET_URL",
        "https://script.google.com/macros/s/AKfycbwTph_gvHOWdGdzqcpMNeK0_-FsW0agehn7ViJKyhyNHFbwh3BULZl2IBHn9wAUcCAu_Q/exec"
    )

    # 📤 Send data to Google Sheets
    try:
        requests.post(
            GOOGLE_SCRIPT_URL,
            json={
                "name": name,
                "school": school,
                "event": event,
                "email": email
            },
            timeout=5
        )
    except Exception as e:
        print("Google Sheets error:", e)

    # 🎓 Load certificate template
    img = Image.open("certificate.png").convert("RGB")
    draw = ImageDraw.Draw(img)

    # 🔤 Load font (fallback safe)
    try:
        font_big = ImageFont.truetype("Arial.ttf", 60)
    except:
        font_big = ImageFont.load_default()

    # 🖊 Write name on certificate
    text_x = 800
    text_y = 600
    draw.text((text_x, text_y), name, fill="black", font=font_big)

    # 📄 Save as PDF
    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PDF")

    return send_file(filepath, as_attachment=True)

# ▶ Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
