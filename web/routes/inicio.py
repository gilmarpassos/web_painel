from flask import Blueprint, render_template, session, redirect, url_for

bp_inicio = Blueprint("inicio", __name__)

@bp_inicio.route("/inicio")
def menu():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    return render_template("menu.html")
