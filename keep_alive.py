from flask import Flask, send_from_directory
from threading import Thread
import os

app = Flask(__name__, static_folder="./web")

@app.route("/")
def index():
    return send_from_directory("./web", "index.html")

@app.route("/<path:path>")
def other(path):
    return send_from_directory("./web", path)

def run():
    port = int(os.environ["PORT"])
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
