from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import sqlite3
import os

bp_configuracoes = Blueprint("configuracoes", __name__, template_folder='configuracoes')
DB = "painel.db"

def get_conexao():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp_configuracoes.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()
    cur.execute("SELECT * FROM configuracoes WHERE id = 1")
    config = cur.fetchone()

    if request.method == "POST":
        nome_empresa = request.form.get("nome_empresa")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        tema = request.form.get("tema")
        logotipo_antigo = config["logotipo"] if config else None

        logotipo = logotipo_antigo
        if "logotipo" in request.files:
            file = request.files["logotipo"]
            if file and file.filename:
                filename = f"logotipo_empresa_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                logotipo = os.path.join("uploads", filename)

        cur.execute("""
            UPDATE configuracoes SET nome_empresa=?, telefone=?, email=?, tema=?, logotipo=? WHERE id=1
        """, (nome_empresa, telefone, email, tema, logotipo))
        con.commit()
        con.close()
        flash("Configurações atualizadas!", "success")
        return redirect(url_for("configuracoes.configuracoes"))

    con.close()
    return render_template("configuracoes/configuracoes.html", config=config)
