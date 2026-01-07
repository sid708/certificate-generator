from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import uuid
import os

app = Flask(__name__)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form["name"]
    school = request.form["school"]
    event = request.form["event"]
    email = request.form["email"]

    # ✅ SAVE PARTICIPANT DATA HERE
    with open("participants.csv", "a", encoding="utf-8") as f:
        f.write(f"{name},{school},{event},{email}\n")

    img = Image.open("certificate.png")
    draw = ImageDraw.Draw(img)

    font_big = ImageFont.truetype("Arial.ttf", 60)

    # Only participant name on certificate
    draw.text((800, 600), name, fill="black", font=font_big)

    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    img.save(filepath, "PDF")

    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
