from flask import Flask, request, jsonify, send_file, redirect, make_response, url_for, render_template, Response, abort, session
from flask_sock import Sock
from flask_cors import CORS
import asyncio
import functools
import json
import requests
import random
import colorama
import datetime
from colorama import Fore
import os
import base64
import sys
from enum import Enum
import jwt
from dotenv import load_dotenv

from OldRecRoom import auth

load_dotenv()

name = f"{__name__}.py"

debug = os.getenv("DEBUG")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
sock = Sock(app)
CORS(app)

@app.errorhandler(500)
def q405(e):
    data = {"Message":"An error has occurred."}
    return jsonify(data), 500

@app.route("/test", methods=["GET"])
def test():
    data = auth.makeToken("tews", [], [])
    return jsonify(data)

def run():
    Port = 9020
    Ip = "0.0.0.0"
    app.run(str(Ip), int(Port), debug)#, ssl_context='adhoc')

run()