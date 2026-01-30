from flask import Flask, request, jsonify
import pdfplumber
import re

app = Flask(__name__)

def is_topic(line):
    if len(line) > 50:
        return False
    if line.endswith("."):
        return False
    words = line.split()
    if len(words) > 6:
        return False
    return True

@app.route("/parse-pdf", methods=["POST"])
def parse_pdf():
    file = request.files["file"]
    file.save("temp.pdf")

    course = []
    current_module = None
    current_topic = None

    with pdfplumber.open("temp.pdf") as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                # MODULE
                if re.match(r"MODULE\s+\d+", line, re.IGNORECASE):
                    current_module = {
                        "title": line,
                        "topics": []
                    }
                    course.append(current_module)
                    current_topic = None

                # TOPIC
                elif current_module and is_topic(line):
                    current_topic = {
                        "title": line,
                        "content": []
                    }
                    current_module["topics"].append(current_topic)

                # CONTENT
                else:
                    if current_topic:
                        current_topic["content"].append(line)

    return jsonify(course)

if __name__ == "__main__":
    app.run()
