from flask import Flask, render_template, request, json
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader
import os

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.5-flash")


@app.route("/", methods=["GET", "POST"])
def home():

    feedback = ""

    if request.method == "POST":

        resume_text = request.form.get("resume_text", "")

        uploaded_file = request.files.get("resume_file")

        if uploaded_file and uploaded_file.filename.endswith(".pdf"):

            pdf = PdfReader(uploaded_file)

            extracted_text = ""

            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    extracted_text += text + "\n"

            resume_text = extracted_text

        prompt = f"""
You are an expert resume reviewer.

Return ONLY JSON in this format:

{{
  "score": 0,
  "summary": "2-3 lines max",
  "strengths": ["point 1", "point 2", "point 3"],
  "weaknesses": ["point 1", "point 2", "point 3"],
  "suggestions": ["point 1", "point 2", "point 3"]
}}

Rules:
- No extra text
- Strict JSON only

Resume:
{resume_text}
"""

        response = model.generate_content(prompt)

        feedback = json.loads(response.text)

    return render_template("index.html", feedback=feedback)


if __name__ == "__main__":
    app.run(debug=True)