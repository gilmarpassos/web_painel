from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3

bp_usuarios = Blueprint("usuarios", __name__)
DB = "painel.db"

def get_conexao():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

# LOGIN
@bp_usuarios.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        senha = request.form.get("senha")
        con = get_conexao()
        cur = con.cursor()
        cur.execute("SELECT * FROM usuarios WHERE login=? AND senha=?", (login, senha))
        usuario = cur.fetchone()
        con.close()
        if usuario:
            session["usuario"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["perfil"] = usuario["perfil"]
            flash(f"Bem-vindo(a), {usuario['nome']}!", "success")
            return redirect(url_for("inicio.menu"))
        else:
            flash("Login ou senha incorretos!", "erro")
    return render_template("usuarios/login.html")

# LOGOUT
@bp_usuarios.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema!", "info")
    return redirect(url_for("usuarios.login"))
@bp_usuarios.route("/usuarios/novo", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "POST":
        nome = request.form.get("nome")
        login = request.form.get("login")
        senha = request.form.get("senha")
        perfil = request.form.get("perfil", "usuario")  # Pode ser admin ou usuario

        # Aqui pode adicionar validações se quiser

        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome, login, senha, perfil) VALUES (?, ?, ?, ?)",
            (nome, login, senha, perfil)
        )
        con.commit()
        con.close()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("usuarios.login"))
    return render_template("usuarios/cadastro_usuario.html")
