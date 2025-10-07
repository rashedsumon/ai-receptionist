# utils.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name, default=None):
    val = os.getenv(name)
    if val is None:
        return default
    return val
