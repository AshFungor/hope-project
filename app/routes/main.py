from flask import render_template

import app.routes.blueprints as blueprints


@blueprints.main.route("/")
@blueprints.main.route("/index")
def index():
    return render_template("main/index.html")
