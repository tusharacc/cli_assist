#!/usr/bin/env python3
"""Simple test app.py file to test execution detection"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from app.py!"

if __name__ == "__main__":
    app.run(debug=True)