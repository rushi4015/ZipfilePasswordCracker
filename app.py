import os
import time
import pyzipper
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    time_taken = 0

    if request.method == "POST":
        start = time.time()

        zip_file = request.files.get("zipfile")
        if not zip_file or not zip_file.filename:
            result = "Please upload a ZIP file."
        else:
            filename = secure_filename(zip_file.filename)
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            zip_file.save(zip_path)

            with open("dictionary.txt", "r") as f:
                wordlist = [line.strip() for line in f]

            try:
                with pyzipper.AESZipFile(zip_path) as zf:
                    found = False
                    for word in wordlist:
                        variants = {
                            word,
                            word.lower(),
                            word.upper(),
                            word.capitalize(),
                            word.title(),
                            word.swapcase()
                        }

                        for variant in variants:
                            try:
                                zf.pwd = bytes(variant, 'utf-8')
                                zf.extractall(path=os.path.join(app.config['UPLOAD_FOLDER'], 'extracted'))
                                result = f"✅ Password found: {variant}"
                                found = True
                                break
                            except:
                                continue
                        if found:
                            break

                    if not found:
                        result = "❌ Password not found in dictionary (with case variations)."
            except:
                result = "❌ Not a valid AES-encrypted ZIP file."

        time_taken = round(time.time() - start, 2)

    return render_template("index.html", result=result, time=time_taken)

if __name__ == "__main__":
    app.run(debug=True)
