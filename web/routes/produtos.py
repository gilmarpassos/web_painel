from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3

bp_produtos = Blueprint("produtos", __name__)
DB = "painel.db"

def get_conexao():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con
@bp_produtos.route("/produtos/novo", methods=["GET", "POST"])
def cadastro_produto():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        valor_str = request.form.get("valor")
        estoque = request.form.get("estoque")

        # Verificação e conversão do valor
        if not valor_str:
            flash("O campo valor é obrigatório.", "erro")
            return redirect(url_for("produtos.cadastro_produto"))

        try:
            valor = float(valor_str)
        except ValueError:
            flash("Valor inválido. Use ponto para decimais, ex: 12.50", "erro")
            return redirect(url_for("produtos.cadastro_produto"))

        con = get_conexao()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO produtos (nome, descricao, valor, estoque) VALUES (?, ?, ?, ?)",
            (nome, descricao, valor, estoque)
        )
        con.commit()
        con.close()
        flash("Produto cadastrado com sucesso!", "produto")
        return redirect(url_for("produtos.listar_produtos"))

    return render_template("produtos/cadastro_produto.html")

@bp_produtos.route("/produtos/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    con = get_conexao()
    cur = con.cursor()
    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        valor = request.form.get("valor")
        estoque = request.form.get("estoque")
        cur.execute(
            "UPDATE produtos SET nome=?, descricao=?, valor=?, estoque=? WHERE id=?",
            (nome, descricao, valor, estoque, id)
        )
        con.commit()
        con.close()
        flash("Produto atualizado com sucesso!", "produto")
        return redirect(url_for("produtos.listar_produtos"))
    cur.execute("SELECT * FROM produtos WHERE id=?", (id,))
    produto = cur.fetchone()
    con.close()
    return render_template("produtos/editar_produto.html", produto=produto)
# routes/produtos.py
@bp_produtos.route("/produtos")
def listar_produtos():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    con = get_conexao()
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cur.fetchall()
    con.close()
    return render_template("produtos/listar_produtos.html", produtos=produtos)
@bp_produtos.route("/produtos/excluir/<int:id>")
def excluir_produto(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    con = get_conexao()
    cur = con.cursor()
    cur.execute("DELETE FROM produtos WHERE id=?", (id,))
    con.commit()
    con.close()
    flash("Produto excluído com sucesso!", "produto")
    return redirect(url_for("produtos.listar_produtos"))

# ...restante das rotas...

# Não precisa nada depois da última função!
