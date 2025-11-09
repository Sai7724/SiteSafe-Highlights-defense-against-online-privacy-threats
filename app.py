from flask import Flask, render_template, request
from privacy_checker import analyze_url

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if not url.startswith("http"):
            url = "https://" + url  # Ensure proper URL
        score, report = analyze_url(url)
        return render_template('result.html', url=url, score=score, report=report)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
