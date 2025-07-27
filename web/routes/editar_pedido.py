@bp_pedidos.route("/pedidos/editar/<int:id>", methods=["GET", "POST"])
def editar_pedido(id):
    if "usuario" not in session:
        return redirect("/login")

    con = get_conexao()
    cur = con.cursor()

    # Busca dados do pedido
    cur.execute("""
        SELECT p.id, c.nome, p.status, p.data
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = ?
    """, (id,))
    pedido = cur.fetchone()
    if not pedido:
        con.close()
        flash("Pedido não encontrado!", "danger")
        return redirect(url_for("pedidos.listar_pedidos"))

    if request.method == "POST":
        novo_status = request.form.get("status")
        cur.execute("UPDATE pedidos SET status=? WHERE id=?", (novo_status, id))
        con.commit()
        con.close()
        flash("Status do pedido atualizado!", "success")
        return redirect(url_for("pedidos/pedidos.listar_pedidos"))

    con.close()
    return render_template("pedidos/editar_pedido.html", pedido={
        "id": pedido[0],
        "cliente": pedido[1],
        "status": pedido[2],
        "data": pedido[3]
    })
