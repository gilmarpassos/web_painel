from flask import Blueprint, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

bp_financeiro = Blueprint("financeiro", __name__)
DB = "painel.db"

def get_conexao():
    return sqlite3.connect(DB)

@bp_financeiro.route("/financeiro", methods=["GET", "POST"])
def painel_financeiro():
    if "usuario" not in session or session["usuario"]["perfil"] != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect("/")

    conn = get_conexao()
    cur = conn.cursor()

    filtro_data_ini = request.args.get("data_ini")
    filtro_data_fim = request.args.get("data_fim")

    query = """
        SELECT p.id, c.nome, p.status, p.data, 
               SUM(i.quantidade * i.preco_unitario) AS total
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN itens_pedido i ON i.pedido_id = p.id
    """
    params = []

    if filtro_data_ini and filtro_data_fim:
        query += " WHERE date(p.data) BETWEEN ? AND ?"
        params.extend([filtro_data_ini, filtro_data_fim])

    query += " GROUP BY p.id ORDER BY p.data DESC"
    cur.execute(query, params)
    pedidos = cur.fetchall()

    total_geral = sum([p[4] for p in pedidos])
    conn.close()

    return render_template("financeiro/painel_financeiro.html", pedidos=pedidos, total_geral=total_geral,
                           data_ini=filtro_data_ini, data_fim=filtro_data_fim)
