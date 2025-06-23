from flask import Blueprint, render_template

import app.modules.database.static as static
import app.routes.blueprints as blueprints


@blueprints.main.route("/")
@blueprints.main.route("/index")
def index():
    return render_template("main/index.html")
