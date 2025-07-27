from flask import Blueprint, render_template, session, redirect

bp_configuracoes = Blueprint("configuracoes", __name__)

@bp_configuracoes.route("/configuracoes")
def configuracoes():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("configuracoes.html")
