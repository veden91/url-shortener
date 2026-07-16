from flask import Flask, render_template, request, redirect, abort
from config import Config
from models import db, URL, Click
from sqlalchemy import func

import random
import string

from urllib.parse import urlparse
from user_agents import parse

def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code= "".join(random.choices(characters,k=length))

        existing =URL.query.filter_by(short_code=code).first()
        if not existing:
            return code


app=Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/home")
def home():
     return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():

    original_url = request.form["url"]

    parsed = urlparse(original_url)
    domain = parsed.netloc

    code = generate_code()

    new_url = URL(
        original_url=original_url,
        short_code=code,
        domain=domain
    )

    db.session.add(new_url)
    db.session.commit()

    short_url = request.host_url + code

    return render_template(
        "index.html",
        short_url=short_url
    )

@app.route("/<short_code>")
def redirect_url(short_code):

    url = URL.query.filter_by(
        short_code=short_code,
        is_active=True
    ).first()

    if not url:
        abort(404)

    url.total_clicks += 1

    user_agent_string = request.headers.get("User-Agent", "")
    ua = parse(user_agent_string)

    if ua.is_mobile:
        device = "Mobile"
    elif ua.is_tablet:
        device = "Tablet"
    elif ua.is_pc:
        device = "PC"
    else:
        device = "Other"

    click = Click(
        url_id=url.id,
        ip_address=request.remote_addr,
        browser=ua.browser.family,
        browser_version=ua.browser.version_string,
        operating_system=ua.os.family,
        device_type=device,
        user_agent=user_agent_string,
        referrer=request.referrer
    )
    db.session.add(click)
    db.session.commit()

    return redirect(url.original_url)


@app.route("/dashboard")
def dashboard():

    urls = URL.query.order_by(URL.created_at.desc()).all()

    total_urls = URL.query.count()

    total_clicks = db.session.query(
        func.sum(URL.total_clicks)
    ).scalar() or 0

    return render_template(
        "dashboard.html",
        urls=urls,
        total_urls=total_urls,
        total_clicks=total_clicks
    )

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
