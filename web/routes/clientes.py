from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3
from datetime import datetime

bp_clientes = Blueprint("clientes", __name__)
DB = "painel.db"

def get_conexao():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # ← permite usar cliente['nome'], etc.
    return conn

# LISTAGEM DE CLIENTES
@bp_clientes.route("/clientes")
def listar_clientes():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    con = get_conexao()
    cur = con.cursor()
    cur.execute("SELECT * FROM clientes ORDER BY nome")
    clientes = cur.fetchall()
    con.close()
    return render_template("clientes/listar_clientes.html", clientes=clientes)

# CADASTRAR NOVO CLIENTE
@bp_clientes.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        cpf = request.form.get("cpf")
        rg = request.form.get("rg")
        cep = request.form.get("cep")
        endereco = request.form.get("endereco")
        numero = request.form.get("numero")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        referencia = request.form.get("referencia")
        outros = request.form.get("outros")
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cliente = request.form.to_dict()  # para reaproveitar os dados no template

        if not endereco:
            flash("O campo Endereço é obrigatório!", "erro")
            return render_template("clientes/novo_cliente.html", cliente=cliente)

        con = get_conexao()
        cur = con.cursor()

        # Verificar se CPF já existe
        cur.execute("SELECT id FROM clientes WHERE cpf = ?", (cpf,))
        if cur.fetchone():
            flash("CPF já cadastrado no sistema!", "erro")
            con.close()
            return render_template("clientes/novo_cliente.html", cliente=cliente)

        cur.execute("""
            INSERT INTO clientes 
            (nome, telefone, cpf, rg, cep, endereco, numero, bairro, cidade, estado, referencia, outros, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, telefone, cpf, rg, cep, endereco, numero, bairro, cidade, estado, referencia, outros, data_cadastro))
        con.commit()
        con.close()

        flash("Cliente cadastrado com sucesso!", "cliente")
        return redirect(url_for("clientes.listar_clientes"))

    # cliente vazio se for GET
    cliente = {}
    return render_template("clientes/novo_cliente.html", cliente=cliente)

@bp_clientes.route("/clientes/verificar_cpf", methods=["POST"])
def verificar_cpf():
    cpf = request.json.get("cpf")
    con = get_conexao()
    cur = con.cursor()
    cur.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
    cliente = cur.fetchone()
    con.close()

    if cliente:
        return {
            "existe": True,
            "dados": {
                "nome": cliente["nome"],
                "telefone": cliente["telefone"],
                "rg": cliente["rg"],
                "cep": cliente["cep"],
                "endereco": cliente["endereco"],
                "numero": cliente["numero"],
                "bairro": cliente["bairro"],
                "cidade": cliente["cidade"],
                "estado": cliente["estado"],
                "referencia": cliente["referencia"],
                "outros": cliente["outros"],
            }
        }
    return { "existe": False }

# EDITAR CLIENTE
@bp_clientes.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    con.row_factory = sqlite3.Row  # <-- ESSENCIAL
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        cpf = request.form.get("cpf")
        rg = request.form.get("rg")
        cep = request.form.get("cep")
        endereco = request.form.get("endereco")
        numero = request.form.get("numero")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        referencia = request.form.get("referencia")
        outros = request.form.get("outros")

        if not endereco:
            flash("Endereço é obrigatório!", "erro")
            return redirect(url_for("clientes.editar_cliente", id=id))

        cur.execute("""
            UPDATE clientes SET nome=?, telefone=?, cpf=?, rg=?, cep=?, endereco=?, numero=?, 
            bairro=?, cidade=?, estado=?, referencia=?, outros=?
            WHERE id=?
        """, (nome, telefone, cpf, rg, cep, endereco, numero, bairro, cidade, estado, referencia, outros, id))
        con.commit()
        con.close()

        flash("Cliente atualizado com sucesso!", "cliente")
        return redirect(url_for("clientes.listar_clientes"))

    cur.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = cur.fetchone()
    con.close()

    return render_template("clientes/editar_cliente.html", cliente=cliente)
# EXCLUIR CLIENTE
@bp_clientes.route("/clientes/excluir/<int:id>")
def excluir_cliente(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()
    cur.execute("DELETE FROM clientes WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Cliente excluído com sucesso!", "cliente")
    return redirect(url_for("clientes.listar_clientes"))
