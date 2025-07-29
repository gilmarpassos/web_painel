from flask import Blueprint, render_template, request, redirect, session, flash, url_for
import sqlite3
import json
from datetime import datetime

bp_pedidos = Blueprint("pedidos", __name__)
DB = "painel.db"

def get_conexao():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con

# NOVO PEDIDO
@bp_pedidos.route("/pedidos", methods=["GET", "POST"])
def pedidos():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        status = request.form.get("status", "pendente")
        itens_json = request.form.get("itens_json")
        mesa_id = request.form.get("mesa_id")

        if not cliente_id or not itens_json or not mesa_id:
            flash("Preencha todos os dados corretamente!", "danger")
            return redirect(url_for("pedidos.pedidos"))

        try:
            itens = json.loads(itens_json)
        except Exception:
            flash("Erro ao processar os itens!", "danger")
            return redirect(url_for("pedidos.pedidos"))

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO pedidos (cliente_id, status, data, mesa_id) VALUES (?, ?, ?, ?)",
            (cliente_id, status, data, mesa_id)
        )
        pedido_id = cur.lastrowid

        for item in itens:
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["valor"])
            )

        con.commit()
        con.close()

        flash("Pedido salvo com sucesso!", "success")
        return redirect(url_for("pedidos.listar_pedidos"))

    # GET
    cur.execute("SELECT * FROM clientes ORDER BY nome")
    clientes = cur.fetchall()

    cur.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cur.fetchall()

    cur.execute("SELECT * FROM mesas ORDER BY nome")
    mesas = cur.fetchall()

    con.close()
    return render_template("pedidos/novo_pedido.html", clientes=clientes, produtos=produtos, mesas=mesas)

# LISTAR PEDIDOS
@bp_pedidos.route("/pedidos/listar")
def listar_pedidos():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    cur.execute(
    """
    SELECT p.*, c.nome AS nome_cliente, m.numero AS numero_mesa
    FROM pedidos p
    LEFT JOIN clientes c ON p.cliente_id = c.id
    LEFT JOIN mesas m ON p.mesa_id = m.id
    ORDER BY p.data DESC
    """
)
    pedidos = cur.fetchall()

    lista = []
    timers_json = []

    for p in pedidos:
        pedido = dict(p)

        cur.execute("""
            SELECT ip.*, pr.nome FROM itens_pedido ip
            JOIN produtos pr ON ip.produto_id = pr.id
            WHERE ip.pedido_id = ?
        """, (p["id"],))
        itens = cur.fetchall()

        pedido["itens"] = [{
            "produto_id": item["produto_id"],
            "nome": item["nome"],
            "quantidade": item["quantidade"],
            "valor": item["preco_unitario"]
        } for item in itens]

        pedido["total"] = sum(item["valor"] * item["quantidade"] for item in pedido["itens"])

        if pedido["status"] == "saiu":
            timers_json.append({"id": pedido["id"], "hora_saida": pedido.get("hora_saida")})

        lista.append(pedido)

    con.close()
    return render_template("pedidos/listar_pedidos.html", pedidos=lista, timers_json=timers_json)

# ALTERAR STATUS
@bp_pedidos.route("/pedidos/status/<int:id>/<novo_status>")
def alterar_status(id, novo_status):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    # Atualiza status + hora_saida/hora_entrega se necessário
    if novo_status == "saiu":
        cur.execute("UPDATE pedidos SET status = ?, hora_saida = ? WHERE id = ?", (novo_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    elif novo_status == "entregue":
        cur.execute("UPDATE pedidos SET status = ?, hora_entrega = ? WHERE id = ?", (novo_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    else:
        cur.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, id))
    
    cur.execute("SELECT * FROM pedidos WHERE id = ?", (id,))
    pedido = cur.fetchone()

    if pedido and novo_status in ["entregue", "pago"]:
        cur.execute("""
        SELECT quantidade, preco_unitario FROM itens_pedido WHERE pedido_id = ?""", (id,))
    itens = cur.fetchall()

    total = sum(i["quantidade"] * i["preco_unitario"] for i in itens)
    descricao = f"Pedido #{id} - Mesa {pedido['mesa_id'] or 'N/A'}"
    data = datetime.now().strftime("%Y-%m-%d")
    tipo = "receita"  # <-- Aqui o ajuste!
    forma_pagamento = "dinheiro"
    cur.execute(
        "INSERT INTO financeiro (descricao, valor, tipo, forma_pagamento, data) VALUES (?, ?, ?, ?, ?)",
        (descricao, total, tipo, forma_pagamento, data)
    )

    con.commit()
    con.close()

    flash(f"Status do pedido #{id} alterado para {novo_status}.", "success")
    return redirect(url_for("pedidos.listar_pedidos"))

# EDITAR PEDIDO
@bp_pedidos.route("/pedidos/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    cur.execute("SELECT * FROM pedidos WHERE id = ?", (id,))
    pedido = cur.fetchone()
    if not pedido:
        flash("Pedido não encontrado!", "danger")
        return redirect(url_for("pedidos.listar_pedidos"))

    if request.method == "POST":
        status = request.form.get("status")
        mesa_id = request.form.get("mesa_id")
        itens_json = request.form.get("itens_json")

        try:
            itens = json.loads(itens_json)
        except:
            flash("Erro ao processar os itens!", "danger")
            return redirect(url_for("pedidos.editar", id=id))

        cur.execute("UPDATE pedidos SET status = ?, mesa_id = ? WHERE id = ?", (status, mesa_id, id))
        cur.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (id,))
        for item in itens:
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (id, item["produto_id"], item["quantidade"], item["valor"])
            )

        con.commit()
        con.close()

        flash("Pedido atualizado com sucesso!", "success")
        return redirect(url_for("pedidos.listar_pedidos"))

    cur.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = cur.fetchall()

    cur.execute("SELECT * FROM mesas ORDER BY nome")
    mesas = cur.fetchall()

    cur.execute("""
        SELECT ip.*, pr.nome FROM itens_pedido ip
        JOIN produtos pr ON ip.produto_id = pr.id
        WHERE ip.pedido_id = ?
    """, (id,))
    itens_db = cur.fetchall()
    itens = [{
        "produto_id": i["produto_id"],
        "nome": i["nome"],
        "valor": i["preco_unitario"],
        "quantidade": i["quantidade"]
    } for i in itens_db]

    con.close()
    return render_template("pedidos/editar_pedido.html", pedido=pedido, produtos=produtos, itens=itens, mesas=mesas)

# EXCLUIR PEDIDO
@bp_pedidos.route("/pedidos/excluir/<int:id>")
def excluir_pedido(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    cur.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (id,))
    cur.execute("DELETE FROM pedidos WHERE id = ?", (id,))
    con.commit()
    con.close()

    flash(f"Pedido #{id} excluído com sucesso.", "success")
    return redirect(url_for("pedidos.listar_pedidos"))
