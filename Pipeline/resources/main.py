from Resources_Processor.resources import Resources_Processor
import time
import logging
from flask import Flask

app = Flask(__name__)

rp = Resources_Processor()

@app.route("/start-brand-new")
def start_brand_new():
    rp.start_brand_new()
    return "Executed"

@app.route("/")
def index():
    return "Resources Service"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")