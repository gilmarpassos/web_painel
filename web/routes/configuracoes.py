from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3

bp_configuracoes = Blueprint("configuracoes", __name__)
DB = "painel.db"

def get_conexao():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

@bp_configuracoes.route("/configuracoes")
def configuracoes():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    
    con = get_conexao()
    cur = con.cursor()
    cur.execute("SELECT * FROM configuracoes LIMIT 1")
    config = cur.fetchone()
    con.close()

    return render_template("configuracoes/configuracoes.html", config=config)

@bp_configuracoes.route("/configuracoes/editar", methods=["POST"])
def editar_configuracoes():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    tema = request.form.get("tema")
    nome_empresa = request.form.get("nome_empresa")
    telefone = request.form.get("telefone")
    email = request.form.get("email")

    con = get_conexao()
    cur = con.cursor()
    cur.execute("""
        UPDATE configuracoes 
        SET tema=?, nome_empresa=?, telefone=?, email=? 
        WHERE id=1
    """, (tema, nome_empresa, telefone, email))
    con.commit()
    con.close()

    flash("Configurações atualizadas com sucesso!", "config")
    return redirect(url_for("configuracoes.configuracoes"))
