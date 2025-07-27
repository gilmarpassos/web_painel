import sqlite3

# Nome do novo banco de dados
NOME_BANCO = 'painel.db'

# Conexão
con = sqlite3.connect(NOME_BANCO)
cur = con.cursor()

# Criação da tabela clientes
cur.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    cpf TEXT UNIQUE,
    rg TEXT,
    cep TEXT,
    endereco TEXT NOT NULL,
    numero TEXT,
    bairro TEXT,
    cidade TEXT,
    estado TEXT,
    referencia TEXT,
    outros TEXT,
    data_cadastro TEXT DEFAULT (datetime('now', 'localtime'))
)
""")

# Confirma e fecha
con.commit()
con.close()

print("✅ Banco de dados e tabela 'clientes' criados com sucesso!")
