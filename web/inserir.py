import sqlite3

con = sqlite3.connect("painel.db")
cur = con.cursor()

# Adiciona o campo se não existir (o SQLite ignora caso já exista)
try:
    cur.execute("ALTER TABLE configuracoes ADD COLUMN logotipo TEXT;")
    print("Campo 'logotipo ' adicionado com sucesso!")
except sqlite3.OperationalError as e:
    print("Campo já existe ou outro erro:", e)

con.commit()
con.close()
