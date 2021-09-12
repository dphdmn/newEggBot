from flask import Flask, send_from_directory
from threading import Thread

app = Flask(__name__, static_folder="./web")

@app.route("/")
def index():
    return send_from_directory("./web", "index.html")

@app.route("/<path:path>")
def other(path):
    return send_from_directory("./web", path)

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
