import os
import subprocess

def restart():
    os.system(f"kill -9 {os.getpid()}")
