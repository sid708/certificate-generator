from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import uuid
import os
import requests

app = Flask(__name__)

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

    GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxcc-wzbaB-eiu5mZWryc4iy6udJi7pO1f-ljrhkPdgU25C3aH0Nwj-krLdo1zYabRmeA/exec"

    payload = {
        "name": name,
        "school": school,
        "event": event,
        "email": email,
        "certificate_id": str(uuid.uuid4()),
        "ip": request.remote_addr
    }

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        print("Google Script Response:", response.text)  # debug log
        result = response.json()
    except Exception as e:
        print("Error calling Google Script:", e)
        return f"Server error: {e}", 500

    # Block invalid info
    if result.get("status") != "valid":
        return (
            "❌ Details do not match our records.<br>"
            "Please check your Name, School, Event, and Email.",
            403
        )

    # Generate certificate ONLY for valid info
    img = Image.open("certificate.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Arial.ttf", 60)
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (img.width - text_width) / 2
    y = 600
    draw.text((x, y), name, fill="black", font=font)


    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PDF")

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
