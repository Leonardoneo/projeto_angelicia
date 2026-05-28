# database/connection.py
import sqlite3
import os
import sys
from utils.security import gerar_hash_senha

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'angelicia.db')

def conectar():
    # 🎯 Descobre se o programa está rodando como um .exe compilado ou como script Python normal
    if hasattr(sys, '_MEIPASS'):
        # Se for o .exe, pega a pasta real onde o .exe está localizado
        base_dir = os.path.dirname(sys.executable)
    else:
        # Se for rodando direto no VS Code, mantém a lógica original do projeto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 🔗 AJUSTADO: Agora aponta exatamente para o seu banco real 'angelicia.db'
    caminho_real_banco = os.path.join(base_dir, "angelicia.db")
    
    # Conecta usando o caminho corrigido
    return sqlite3.connect(caminho_real_banco)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabela de Usuários (Segurança)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        perfil TEXT NOT NULL
    )
    """)
    
    # 2. NOVA: Tabela Dinâmica de Categorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )
    """)
    
    # Inserir categorias padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_padrao = [("Bolo",), ("Torta",), ("Salgado",), ("Doce Geral",)]
        cursor.executemany("INSERT INTO categorias (nome) VALUES (?)", categorias_padrao)
    
    # 3. Tabela de Produtos (Atualizada conceitualmente para vincular com a tabela categorias)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT NOT NULL, 
        preco_venda REAL NOT NULL,
        custo_producao REAL NOT NULL,
        data_cadastro DATE DEFAULT CURRENT_DATE,
        ingredientes TEXT,
        foto_path TEXT
        em_promocao INTEGER DEFAULT 0,    -- 🎯 0 = Não, 1 = Sim
        preco_promocao REAL DEFAULT 0.00  -- 🎯 Preço especial com desconto
    )
    """)
    
    # 4. Tabela de Vendas (Atualizada com Vínculo de Cliente para CRM)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        contato_id INTEGER, -- <-- NOVA COLUNA: Vincula a venda ao Cliente da tabela contatos
        quantidade INTEGER NOT NULL,
        data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
        valor_total REAL NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (contato_id) REFERENCES contatos(id) -- Chave Estrangeira
    )
    """)

    # 5. NOVA: Tabela de Contatos (Clientes e Fornecedores) - ATUALIZADA PARA ENTREGAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL, -- 'Cliente' ou 'Fornecedor'
        email TEXT,
        telefone TEXT,
        senha_acesso TEXT, -- Caso eles ganhem um portal no futuro
        cep TEXT,          -- 🎯 ADICIONADO: CEP do cliente
        endereco TEXT,     -- 🎯 ADICIONADO: Rua, número, complemento
        bairro TEXT,       -- 🎯 ADICIONADO: Bairro para entrega
        estado TEXT        -- 🎯 ADICIONADO: Estado / UF
    )
    """)
    conn.commit()
    
    # ─────────────────────────────────────────────────────────────────
    # PASSO 2: BLOCO DE ATUALIZAÇÃO DA TABELA PRODUTOS (ALINHADO)
    # ─────────────────────────────────────────────────────────────────
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass # <-- Corrigido! Agora alinhado perfeitamente na mesma linha do try/except
    # ─────────────────────────────────────────────────────────────────

    # Criando o usuário ROOT padrão de segurança
    cursor.execute("SELECT * FROM usuarios WHERE perfil = 'root'")
    if not cursor.fetchone():
        # Importação local para blindar o hash contra erros de carregamento
        from utils.security import gerar_hash_senha
        senha_root_hash = gerar_hash_senha("AngeliciaRoot2026")
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, perfil) VALUES (?, ?, ?)",
            ("admin_root", senha_root_hash, "root")
        )
        conn.commit()
        print("[DATABASE] Novo acesso admin_root gerado com sucesso!")
    
    # ─────────────────────────────────────────────────────────────────
    # 🩹 COLOQUE O CÓDIGO EXATAMENTE AQUI (NO FINAL DE TODA A FUNÇÃO!)
    # ─────────────────────────────────────────────────────────────────
    try:
        # Tenta injetar as colunas novas de promoção na tabela que já existe
        cursor.execute("ALTER TABLE produtos ADD COLUMN em_promocao INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE produtos ADD COLUMN preco_promocao REAL DEFAULT 0.00")
        conn.commit()
    except:
        # Se as colunas já existirem de um teste anterior, o SQLite gera um erro controlado 
        # e o Python passa batido sem travar o sistema. Segurança total!
        pass
    # ─────────────────────────────────────────────────────────────────

    conn.commit()
    conn.close()
    print("[DATABASE] Engenharia de dados atualizada. Tabelas Prontas!")

# ─────────────────────────────────────────────────────────────────
#  COLE A NOVA FUNÇÃO EXATAMENTE AQUI (FORA DA ANTERIOR, SEM ESPAÇOS NO INÍCIO)
# ─────────────────────────────────────────────────────────────────
def cadastrar_novo_usuario(username, senha_pura, perfil):
    """Cadastra o login na tabela 'usuarios' e joga na tabela 'contatos' de forma padronizada."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        from utils.security import gerar_hash_senha
        hash_senha = gerar_hash_senha(senha_pura)
        
        # 1. Salva na tabela de logins (usuarios)
        # Se o seu login rejeita 'master', forçamos a gravação como 'admin' ou mantemos o perfil limpo
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, perfil) VALUES (?, ?, ?)",
            (username.strip(), hash_senha, perfil.strip().lower())
        )
        
        # 2. 🔥 O AJUSTE CRÍTICO: Para a lista do Flet, todo funcionário/master DEVE ser do tipo 'Operador'
        # Isso evita que o Flet não reconheça o tipo e desenhe a barra cinza!
        tipo_ajustado = "Operador"
        
        cursor.execute(
            "INSERT INTO contatos (nome, tipo) VALUES (?, ?)",
            (username.strip(), tipo_ajustado)
        )
        
        conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return False, "Erro ao cadastrar usuário."
    finally:
        conn.close()

def deletar_usuario_banco(id_ou_nome):
    # 🎯 O SEGREDO: Em vez de criar um "banco.db" novo do zero, 
    # nós chamamos a função conectar() que já sabe a pasta e o nome correto do banco real!
    try:
        conn = conectar() 
        cursor = conn.cursor()
    except Exception as e_conn:
        print(f"❌ Erro ao abrir conexão real do banco: {e_conn}")
        return
    
    try:
        # 1. Tenta deletar pelo ID (número)
        cursor.execute("DELETE FROM contatos WHERE id = ?", (id_ou_nome,))
        
        # 2. Se não apagou nada pelo ID, tenta pelo Nome (texto)
        if cursor.rowcount == 0:
            cursor.execute("DELETE FROM contatos WHERE nome = ?", (id_ou_nome,))
            
        # Grava a exclusão no banco real
        conn.commit() 
        print(f"✅ Sucesso! Linhas apagadas no banco real: {cursor.rowcount}")
        
    except Exception as e:
        print(f"❌ Erro interno do banco ao deletar: {e}")
        conn.rollback()
    finally:
        conn.close()