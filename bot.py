import os
import subprocess

git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], universal_newlines=True)

def restart():
    os.system(f"kill -9 {os.getpid()}")

def update():
    subprocess.call(["git", "stash"])
    subprocess.call(["git", "pull"])
    subprocess.call(["git", "checkout", "master"])
