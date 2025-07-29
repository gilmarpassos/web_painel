from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
import sqlite3
from datetime import datetime
import csv
import io

bp_financeiro = Blueprint("financeiro", __name__, url_prefix="/financeiro")
DB = "painel.db"

def conexao():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

bp_financeiro = Blueprint("financeiro", __name__)

@bp_financeiro.route("/financeiro")
def painel_financeiro():
    con = sqlite3.connect("painel.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    filtro_tipo = request.args.get("tipo")
    filtro_data_inicio = request.args.get("inicio")
    filtro_data_fim = request.args.get("fim")

    query = "SELECT * FROM financeiro WHERE 1=1"
    params = []

    if filtro_tipo:
        query += " AND tipo = ?"
        params.append(filtro_tipo)
    if filtro_data_inicio:
        query += " AND data >= ?"
        params.append(filtro_data_inicio)
    if filtro_data_fim:
        query += " AND data <= ?"
        params.append(filtro_data_fim)

    cur.execute(query, params)
    lancamentos = cur.fetchall()

    # Totais
    cur.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'receita'")
    total_receitas = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'despesa'")
    total_despesas = cur.fetchone()[0] or 0

    total = total_receitas - total_despesas

    con.close()

    return render_template(
        "financeiro/listar.html",
        lancamentos=lancamentos,
        total=total,
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        filtro_tipo=filtro_tipo,
        filtro_data_inicio=filtro_data_inicio,
        filtro_data_fim=filtro_data_fim
    )
@bp_financeiro.route("/novo", methods=["GET", "POST"])
def novo_lancamento():
    if "usuario" not in session or session.get("perfil") != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("usuarios.login"))

    if request.method == "POST":
        descricao = request.form["descricao"]
        valor = request.form["valor"]
        tipo = request.form["tipo"]
        forma_pagamento = request.form["forma_pagamento"]
        data = request.form["data"] or datetime.now().strftime("%Y-%m-%d")

        con = conexao()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO financeiro (descricao, valor, tipo, forma_pagamento, data)
            VALUES (?, ?, ?, ?, ?)
        """, (descricao, valor, tipo, forma_pagamento, data))
        con.commit()
        con.close()

        flash("Lançamento adicionado com sucesso!", "success")
        return redirect(url_for("financeiro.painel_financeiro"))

    return render_template("financeiro/novo.html")

@bp_financeiro.route("/excluir/<int:id>")
def excluir_lancamento(id):
    if "usuario" not in session or session.get("perfil") != "admin":
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("usuarios.login"))

    con = conexao()
    cur = con.cursor()
    cur.execute("DELETE FROM financeiro WHERE id = ?", (id,))
    con.commit()
    con.close()

    flash("Lançamento excluído com sucesso.", "info")
    return redirect(url_for("financeiro.painel_financeiro"))
