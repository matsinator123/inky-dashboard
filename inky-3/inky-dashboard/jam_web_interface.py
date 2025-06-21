from flask import Flask, request, render_template_string

app = Flask(__name__)
JAM_URL_FILE = "jam_url.txt"

HTML = """
<!doctype html>
<title>Spotify Jam Link</title>
<h1>Oppgi Spotify Jam-link</h1>
<form method="post">
  <input type="text" name="jam_url" size="60">
  <input type="submit" value="Lagre">
</form>
{% if message %}
  <p><strong>{{ message }}</strong></p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        jam_url = request.form["jam_url"].strip()
        if jam_url:
            with open(JAM_URL_FILE, "w") as f:
                f.write(jam_url)
            message = "Jam-link lagret!"
        else:
            message = "Vennligst skriv inn en gyldig lenke."
    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
