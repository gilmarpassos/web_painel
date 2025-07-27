import sqlite3

DB = "painel.db"

def ajustar_banco():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # Criar tabela de configurações
    cur.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes (
        id INTEGER PRIMARY KEY,
        nome_empresa TEXT,
        telefone TEXT,
        email TEXT
    )
    """)

    # Inserir configuração padrão (se não existir)
    cur.execute("SELECT COUNT(*) FROM configuracoes WHERE id=1")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO configuracoes (id, nome_empresa, telefone, email)
        VALUES (1, 'Minha Empresa', '(00) 0000-0000', 'exemplo@email.com')
        """)

    # Verificar se coluna 'cor' já existe em pedidos
    cur.execute("PRAGMA table_info(pedidos)")
    colunas = [col[1] for col in cur.fetchall()]
    if "cor" not in colunas:
        cur.execute("ALTER TABLE pedidos ADD COLUMN cor TEXT DEFAULT ''")
        print("Coluna 'cor' adicionada na tabela pedidos.")

    con.commit()
    con.close()
    print("Banco ajustado com sucesso.")

if __name__ == "__main__":
    ajustar_banco()
