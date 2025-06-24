from flask import render_template
from app.routes import Blueprints


@Blueprints.main.route("/")
@Blueprints.main.route("/index")
def index():
    return render_template("main/index.html")
