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

        if not cliente_id or not itens_json:
            flash("Preencha todos os dados corretamente!", "pedido")
            return redirect(url_for("pedidos.pedidos"))

        try:
            itens = json.loads(itens_json)
        except Exception:
            flash("Erro ao ler os itens do pedido!", "pedido")
            return redirect(url_for("pedidos.pedidos"))

        if not itens:
            flash("Adicione pelo menos um item ao pedido!", "pedido")
            return redirect(url_for("pedidos.pedidos"))

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO pedidos (cliente_id, status, data) VALUES (?, ?, ?)", (cliente_id, status, data))
        pedido_id = cur.lastrowid

        for item in itens:
            cur.execute("""
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
            """, (pedido_id, item["produto_id"], item["quantidade"], item["preco"]))

        con.commit()
        flash("Pedido salvo com sucesso!", "pedido")
        return redirect(url_for("pedidos.listar_pedidos"))

    cur.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cur.fetchall()

    cur.execute("SELECT id, nome, preco FROM produtos ORDER BY nome")
    produtos = cur.fetchall()

    con.close()
    return render_template("pedidos/novo_pedido.html", clientes=clientes, produtos=produtos)

# LISTAGEM DE PEDIDOS
@bp_pedidos.route("/pedidos/listar")
def listar_pedidos():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    filtro_status = request.args.get("status")
    if filtro_status:
        cur.execute("""
            SELECT p.id, c.nome, p.status, p.data, p.hora_saida, p.hora_entrega
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE p.status = ?
            ORDER BY p.data DESC
        """, (filtro_status,))
    else:
        cur.execute("""
            SELECT p.id, c.nome, p.status, p.data, p.hora_saida, p.hora_entrega
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.data DESC
        """)

    pedidos = cur.fetchall()
    pedidos_com_itens = []
    for pedido in pedidos:
        cur.execute("""
            SELECT pr.nome, i.quantidade, i.preco_unitario
            FROM itens_pedido i
            JOIN produtos pr ON pr.id = i.produto_id
            WHERE i.pedido_id = ?
        """, (pedido["id"],))
        itens = cur.fetchall()
        pedidos_com_itens.append({
            "id": pedido["id"],
            "cliente": pedido["nome"],
            "status": pedido["status"],
            "data": pedido["data"],
            "hora_saida": pedido["hora_saida"],
            "hora_entrega": pedido["hora_entrega"],
            "itens": itens
        })

    con.close()
    return render_template("pedidos/listar_pedidos.html", pedidos=pedidos_com_itens, filtro_status=filtro_status)

# EXCLUIR PEDIDO
@bp_pedidos.route("/pedidos/excluir/<int:id>")
def excluir_pedido(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()
    cur.execute("DELETE FROM itens_pedido WHERE pedido_id=?", (id,))
    cur.execute("DELETE FROM pedidos WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Pedido excluído com sucesso!", "pedido")
    return redirect(url_for("pedidos.listar_pedidos"))

# EDITAR PEDIDO
@bp_pedidos.route("/pedidos/editar/<int:id>", methods=["GET", "POST"])
def editar_pedido(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    con = get_conexao()
    cur = con.cursor()

    # Carrega pedido e cliente
    cur.execute("""
        SELECT p.id, p.cliente_id, c.nome, p.status, p.data
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = ?
    """, (id,))
    pedido = cur.fetchone()
    if not pedido:
        con.close()
        flash("Pedido não encontrado!", "danger")
        return redirect(url_for("pedidos.listar_pedidos"))

    # Carrega itens
    cur.execute("""
        SELECT ip.produto_id, pr.nome, ip.quantidade, ip.preco_unitario
        FROM itens_pedido ip
        JOIN produtos pr ON pr.id = ip.produto_id
        WHERE ip.pedido_id = ?
    """, (id,))
    itens = cur.fetchall()

    # Carrega lista de produtos para formulário
    cur.execute("SELECT id, nome, preco FROM produtos ORDER BY nome")
    produtos = cur.fetchall()

    if request.method == "POST":
        novo_status = request.form.get("status")
        itens_json = request.form.get("itens_json")

        try:
            novos_itens = json.loads(itens_json)
        except:
            flash("Erro ao ler os itens atualizados!", "danger")
            return redirect(url_for("pedidos.editar_pedido", id=id))

        if not novos_itens:
            flash("Adicione ao menos um item!", "danger")
            return redirect(url_for("pedidos.editar_pedido", id=id))

        # Atualiza status
        cur.execute("UPDATE pedidos SET status=? WHERE id=?", (novo_status, id))

        # Remove itens antigos
        cur.execute("DELETE FROM itens_pedido WHERE pedido_id=?", (id,))
        for item in novos_itens:
            cur.execute("""
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
            """, (id, item["produto_id"], item["quantidade"], item["preco"]))

        con.commit()
        con.close()
        flash("Pedido atualizado com sucesso!", "success")
        return redirect(url_for("pedidos.listar_pedidos"))

    con.close()
    return render_template("pedidos/editar_pedido.html", pedido={
        "id": pedido["id"],
        "cliente_id": pedido["cliente_id"],
        "cliente": pedido["nome"],
        "status": pedido["status"],
        "data": pedido["data"],
        "itens": itens
    }, produtos=produtos)

# ATUALIZAR STATUS (AJAX)
@bp_pedidos.route("/pedidos/status/<int:id>", methods=["POST"])
def atualizar_status(id):
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))

    novo_status = request.form.get("status")
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con = get_conexao()
    cur = con.cursor()

    # Verifica o status atual e horários
    cur.execute("SELECT status, hora_saida, hora_entrega FROM pedidos WHERE id=?", (id,))
    pedido = cur.fetchone()

    if not pedido:
        con.close()
        return "Erro: Pedido não encontrado", 404

    if novo_status == "saiu" and not pedido["hora_saida"]:
        cur.execute("UPDATE pedidos SET status=?, hora_saida=? WHERE id=?", (novo_status, agora, id))
    elif novo_status == "entregue" and not pedido["hora_entrega"]:
        cur.execute("UPDATE pedidos SET status=?, hora_entrega=? WHERE id=?", (novo_status, agora, id))
    else:
        cur.execute("UPDATE pedidos SET status=? WHERE id=?", (novo_status, id))

    con.commit()
    con.close()
    return "OK"
