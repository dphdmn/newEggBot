import os
import subprocess

git_info = subprocess.check_output(["git", "show", "-s", "--format=%h, %ci", "HEAD"], universal_newlines=True).strip()

def restart():
    os.system(f"kill -9 {os.getpid()}")

def update():
    subprocess.call(["git", "stash"])
    subprocess.call(["git", "pull"])
    subprocess.call(["git", "checkout", "master"])
