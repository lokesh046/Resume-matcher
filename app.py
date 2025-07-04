import os
import fitz  
import numpy as np
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def compute_similarity(resume_text, job_desc):
    embeddings = model.encode([resume_text, job_desc])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
    return round(similarity[0][0] * 100, 2)  

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "resume" not in request.files:
            return "No file uploaded", 400
        file = request.files["resume"]
        job_desc = request.form["job_desc"]

        if file.filename == "" or job_desc.strip() == "":
            return "Invalid input", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)


        resume_text = extract_text_from_pdf(filepath)
        score = compute_similarity(resume_text, job_desc)

        return render_template("index.html", score=score)

    return render_template("index.html", score=None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
