#!/bin/python3
import flask, flask_login
from flask import url_for, request, render_template, redirect
from flask_login import current_user
import collections, json, queue, random, functools, urllib.parse, re
from datetime import datetime,timedelta
from base import app,load_info,ajax,DBDict,DBList,random_id,hash_id,full_url_for
from bs4 import BeautifulSoup
import requests

# -- Info for every Hack-A-Day project --
load_info({
    "project_name": "Hack-An-Uptime",
    "source_url": "https://github.com/za3k/day34_uptime",
    "subdir": "/hackaday/uptime",
    "description": "Press the button once a day. Resets at midnight UTC.",
    "instructions": "",
    "login": True,
    "fullscreen": True,
})

# -- Routes specific to this Hack-A-Day project --
clicks = DBDict("click")
scores = DBDict("score")

def last_midnight():
    return clicks.get('server_last_check', datetime(2000,1,2))

@app.route("/")
def index():
    click, score = None, None
    has_clicked, alive = False, True
    if current_user.is_authenticated:
        click = clicks.get(current_user.id)
        score = scores.get(current_user.id, {"score": 0, "lost": False})
        if click: has_clicked = click["last_click"] > last_midnight()
    
    return render_template('index.html', has_clicked=has_clicked, score=score, click=click, scores=sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True))

@app.route("/click/<user>")
def click_page(user):
    assert user != 'server_last_check'

    click = clicks.get(user, { "clicks": 0, "last_click": datetime(2000,1,1) })
    score = scores.get(user, { "score": 0 , "lost": False })
    lc = last_midnight()

    if click["last_click"] < lc and not score["lost"]:
        score["score"] += 1
        scores[user] = score
    click["clicks"] += 1
    click["last_click"] = datetime.now()
    clicks[user] = click

    return redirect(url_for("index"))

@app.route("/update")
def update_page():
    if last_midnight() + timedelta(days=1) < datetime.utcnow():
        update()
        return "updated"
    return "no update"

def update():
    lc = last_midnight()
    for user in DBDict("users"):
        click = clicks.get(user)
        score = scores.get(user, { "score": 0, "lost": False })
        if (not click) or score["lost"]: continue
        if click["last_click"] > lc: # Still in
            click["clicks"]=0
        else: # lost
            score["lost"]=True
            click["clicks"]=0
        clicks[user] = click
        scores[user] = score
    clicks['server_last_check'] = datetime.combine(datetime.utcnow().date(), datetime.min.time());
