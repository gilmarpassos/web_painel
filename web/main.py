from flask import Flask, session, redirect, url_for
from routes.usuarios import bp_usuarios
from routes.pedidos import bp_pedidos
from routes.clientes import bp_clientes
from routes.produtos import bp_produtos
from routes.entregadores import bp_entregadores
from routes.configuracoes import bp_configuracoes
from routes.financeiro import bp_financeiro
from routes.inicio import bp_inicio

app = Flask(__name__)
app.secret_key = 'chave-secreta-painel'

# Registro dos blueprints (rotas separadas)
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_pedidos)
app.register_blueprint(bp_clientes)
app.register_blueprint(bp_produtos)
app.register_blueprint(bp_entregadores)
app.register_blueprint(bp_configuracoes)
app.register_blueprint(bp_financeiro)
app.register_blueprint(bp_inicio)


# Rota inicial: redireciona para login ou menu
@app.route("/")
def inicio():
    if "usuario" not in session:
        return redirect(url_for("usuarios.login"))
    return redirect(url_for("inicio.menu"))

if __name__ == "__main__":
    app.run(debug=True)
import sqlite3

def get_config():
    try:
        con = sqlite3.connect("painel.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM configuracoes LIMIT 1")
        config = cur.fetchone()
        con.close()
        return config
    except:
        return {}

@app.context_processor
def inject_config():
    config = get_config()
    return dict(config=config)
