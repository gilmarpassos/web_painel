import sqlite3
from flask import Blueprint, render_template, request, redirect, flash, session, url_for
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp_entregadores = Blueprint("entregadores", __name__)

DB = "painel.db"
UPLOAD_DIR = "static/uploads/entregadores"

# Criar diretório de uploads, caso não exista
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Função para conectar ao banco de dados com sqlite3.Row
def get_conexao():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # Permite acessar as colunas como atributos (e.g., row.id)
    return conn
# ----------- Exclusão de entregador ----------- 
@bp_entregadores.route('/excluir_entregador/<int:id>', methods=['GET'])
def excluir_entregador(id):
    if "usuario" not in session:
        return redirect("/login")
    
    con = get_conexao()
    cur = con.cursor()

    # Deletando o entregador com base no id
    cur.execute("DELETE FROM entregadores WHERE id = ?", (id,))
    con.commit()
    con.close()

    flash("Entregador excluído com sucesso!", "success")
    return redirect(url_for('entregadores.listar_entregadores'))

# ----------- Cadastro de entregador ----------- 
@bp_entregadores.route("/entregadores", methods=["GET", "POST"])
def cadastrar_entregador():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        rg = request.form.get("rg")
        telefone = request.form.get("telefone")
        placa = request.form.get("placa")
        cnh = request.form.get("cnh")
        obs = request.form.get("obs")
        foto = request.files.get("foto")
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Lógica para salvar a foto
        foto_path = ""
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            foto_path = os.path.join(UPLOAD_DIR, filename)
            foto.save(foto_path)
            foto_path = os.path.relpath(foto_path, "static")  # Salva o caminho relativo para uso no HTML

        # Conectando ao banco e inserindo os dados
        con = get_conexao()
        cur = con.cursor()

        # Criação da tabela (se não existir)
        cur.execute(""" 
            CREATE TABLE IF NOT EXISTS entregadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                cpf TEXT,
                rg TEXT,
                telefone TEXT,
                placa TEXT,
                cnh TEXT,
                obs TEXT,
                foto TEXT,
                data_cadastro TEXT
            )
        """)

        # Inserção dos dados na tabela
        cur.execute(""" 
            INSERT INTO entregadores (nome, cpf, rg, telefone, placa, cnh, obs, foto, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, rg, telefone, placa, cnh, obs, foto_path, data_cadastro))

        con.commit()
        con.close()

        flash("Entregador cadastrado com sucesso!", "success")
        return redirect(url_for("entregadores.cadastrar_entregador"))

    return render_template("entregadores/cadastrar_entregador.html")

# ----------- Listagem de entregadores ----------- 
@bp_entregadores.route("/entregadores/listar", methods=["GET"])
def listar_entregadores():
    if "usuario" not in session:
        return redirect("/login")

    con = get_conexao()
    cur = con.cursor()
    cur.execute("SELECT * FROM entregadores ORDER BY data_cadastro DESC")
    entregadores = cur.fetchall()  # Agora isso vai retornar uma lista de objetos Row
    con.close()
    return render_template("entregadores/listar_entregadores.html", entregadores=entregadores)

# ----------- Edição de entregador ----------- 
# ----------- Edição de entregador ----------- 
@bp_entregadores.route('/editar_entregador/<int:id>', methods=['GET', 'POST'])
def editar_entregador(id):
    if "usuario" not in session:
        return redirect("/login")
    
    # Conectar ao banco de dados
    con = get_conexao()
    cur = con.cursor()
    
    # Consultar o entregador com o id
    cur.execute("SELECT * FROM entregadores WHERE id = ?", (id,))
    entregador = cur.fetchone()  # Retorna um objeto Row
    
    if not entregador:
        flash("Entregador não encontrado.", "danger")
        return redirect(url_for('entregadores.listar_entregadores'))
    
    if request.method == 'POST':
        # Pega os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        rg = request.form['rg']
        telefone = request.form['telefone']
        placa = request.form['placa']
        cnh = request.form['cnh']
        obs = request.form['obs']
        
        # Lógica para atualizar a foto, se fornecida
        foto = request.files.get('foto')
        foto_path = entregador['foto']  # Mantém a foto anterior, caso não tenha sido alterada

        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            foto_path = os.path.join(UPLOAD_DIR, filename)
            foto.save(foto_path)
            foto_path = os.path.relpath(foto_path, "static")

        # Atualizando os dados no banco de dados
        cur.execute("""
            UPDATE entregadores
            SET nome = ?, cpf = ?, rg = ?, telefone = ?, placa = ?, cnh = ?, obs = ?, foto = ?
            WHERE id = ?
        """, (nome, cpf, rg, telefone, placa, cnh, obs, foto_path, id))
        
        con.commit()
        con.close()

        flash("Entregador atualizado com sucesso!", "success")
        return redirect(url_for('entregadores.listar_entregadores'))

    con.close()
    
    return render_template('entregadores/editar_entregador.html', entregador=entregador)


    con.close()
    return render_template('entregadores/editar_entregador.html', entregador=entregador)
