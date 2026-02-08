import sqlite3
import os
import json
from pathlib import Path
from .testes import adicionar_dados_teste

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_FILE = os.path.join(DB_PATH, 'database.db')

def set_db_file(db_file):
    global DB_FILE
    DB_FILE = db_file

def _criar_diretorio_dados():
    Path(DB_PATH).mkdir(parents=True, exist_ok=True)

def _get_connection():
    _criar_diretorio_dados()
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
    conn.execute('PRAGMA journal_mode=WAL')  # Modo WAL para evitar locks
    conn.execute('PRAGMA busy_timeout=30000')  # 30s timeout
    return conn

def _executar_query(query, params=None):
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao executar query: {e}")
        return False

def _executar_query_com_id(query, params=None):
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id
    except sqlite3.Error as e:
        print(f"Erro ao executar query: {e}")
        return None

def _executar_select(query, params=None):
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        return [dict(row) for row in resultados]
    except sqlite3.Error as e:
        print(f"Erro ao executar SELECT: {e}")
        return []

def _executar_select_um(query, params=None):
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        resultado = cursor.fetchone()
        conn.close()
        return dict(resultado) if resultado else None
    except sqlite3.Error as e:
        print(f"Erro ao executar SELECT: {e}")
        return None

def inicializar_database(test=False, extras=False):
    _criar_diretorio_dados()
    
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_questao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_file TEXT NOT NULL,
            nome TEXT NOT NULL UNIQUE,
            list_options BOOLEAN DEFAULT 0,
            correcao_automatica BOOLEAN DEFAULT 1,
            multiplas_respostas BOOLEAN DEFAULT 0
        )
    ''')

    # Migração: Adicionar coluna input_file se não existir
    try:
        cursor.execute("PRAGMA table_info(tipos_questao)")
        colunas = {row[1] for row in cursor.fetchall()}
        if 'input_file' not in colunas:
            print("Migrando: Adicionando coluna input_file à tabela tipos_questao...")
            cursor.execute("ALTER TABLE tipos_questao ADD COLUMN input_file TEXT DEFAULT 'text'")
            # Atualizar nomes existentes para serem o input_file
            cursor.execute("UPDATE tipos_questao SET input_file = nome")
            cursor.execute("ALTER TABLE tipos_questao MODIFY COLUMN input_file TEXT NOT NULL")
            conn.commit()
            print("Migração concluída com sucesso!")
    except sqlite3.Error as e:
        print(f"Aviso durante migração: {e}")

    # Tipos de questão são inicializados em extras.py quando extras=True
    # Fallback com nomes amigáveis quando extras não é usado
    if not extras:
        cursor.execute("""INSERT OR IGNORE INTO tipos_questao (input_file, nome, list_options, correcao_automatica) VALUES 
            ('text', 'Texto', 0, 0), 
            ('choices', 'Opções (única resposta)', 1, 1), 
            ('true_false', 'Verdadeiro ou Falso', 0, 1), 
            ('true_false_justificado', 'Verdadeiro ou Falso justificado', 0, 0)
        """)
        # Ajustar nomes antigos iguais ao input_file
        cursor.execute("""
            UPDATE tipos_questao
            SET nome = CASE input_file
                WHEN 'text' THEN 'Texto'
                WHEN 'choices' THEN 'Opções (única resposta)'
                WHEN 'true_false' THEN 'Verdadeiro ou Falso'
                WHEN 'true_false_justificado' THEN 'Verdadeiro ou Falso justificado'
                ELSE nome
            END
            WHERE nome = input_file
        """)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            codigo TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INTEGER NOT NULL,
            identificador TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            id_cargo INTEGER NOT NULL DEFAULT 3,
            senha TEXT NOT NULL DEFAULT 'senha.123@2025',
            FOREIGN KEY (id_cargo) REFERENCES roles(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute("INSERT OR IGNORE INTO roles (nome) VALUES ('admin'), ('professor'), ('aluno')")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplina_turma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            professor_id INTEGER NOT NULL,
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE RESTRICT,
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE RESTRICT,
            FOREIGN KEY (professor_id) REFERENCES contas(id) ON DELETE RESTRICT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificador TEXT NOT NULL UNIQUE,
            turma_id INTEGER NOT NULL,
            id_conta INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE RESTRICT,
            FOREIGN KEY (id_conta) REFERENCES contas(id) ON DELETE RESTRICT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disciplina_turma_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            data_hora_inicio TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            publico INTEGER DEFAULT 1,
            FOREIGN KEY (disciplina_turma_id) REFERENCES disciplina_turma(id) ON DELETE RESTRICT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            tipo_questao_id INTEGER NOT NULL,
            exame_id INTEGER NOT NULL,
            numero_questao TEXT,
            pontuacao_maxima REAL NOT NULL,
            FOREIGN KEY (tipo_questao_id) REFERENCES tipos_questao(id) ON DELETE RESTRICT,
            FOREIGN KEY (exame_id) REFERENCES exames(id) ON DELETE RESTRICT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            questao_id INTEGER NOT NULL UNIQUE,
            opcoes JSON NOT NULL,
            opcao_correta TEXT,
            FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exame_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            questao_id INTEGER NOT NULL,
            resposta TEXT NOT NULL,
            data_hora_resposta TEXT NOT NULL,
            pontuacao_atribuida REAL DEFAULT 0,
            corrigido_professor BOOLEAN DEFAULT 0,
            FOREIGN KEY (exame_id) REFERENCES exames(id),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id),
            FOREIGN KEY (questao_id) REFERENCES questoes(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissoes_exame (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exame_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            data_hora_inicio TEXT NOT NULL,
            data_hora_fim TEXT,
            estado TEXT DEFAULT 'em_andamento',
            FOREIGN KEY (exame_id) REFERENCES exames(id) ON DELETE RESTRICT,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE RESTRICT
        )
    ''')
    
    # CREATE TABLE: submissoes_questao
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissoes_questao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submissao_exame_id INTEGER NOT NULL,
            questao_id INTEGER NOT NULL,
            resposta TEXT,
            pontuacao REAL DEFAULT 0,
            data_hora_resposta TEXT,
            pontuacao_atribuida REAL DEFAULT 0,
            estado TEXT DEFAULT 'nao_corrigido',
            FOREIGN KEY (submissao_exame_id) REFERENCES submissoes_exame(id) ON DELETE CASCADE,
            FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE RESTRICT
        )
    ''')
    
    conn.commit()
    
    # Validar integridade de respostas
    _validar_integridade_respostas(cursor)
    
    if test:
        adicionar_dados_teste(cursor)
    elif extras:
        conn.close()  # Fechar conexão antes de chamar extras (que abre suas próprias conexões)
        from .extras import adicionar_dados_extras
        adicionar_dados_extras()
        return
    
    conn.commit()
    conn.close()


def _validar_integridade_respostas(cursor):
    # Criar respostas vazias para questões que deveriam ter mas não têm
    cursor.execute('''
        INSERT INTO respostas (questao_id, opcoes, opcao_correta)
        SELECT q.id, '[]', NULL
        FROM questoes q
        JOIN tipos_questao t ON q.tipo_questao_id = t.id
        WHERE (t.list_options = 1 OR t.correcao_automatica = 1)
        AND NOT EXISTS (SELECT 1 FROM respostas WHERE questao_id = q.id)
    ''')
    # Eliminar respostas de questões que não deveriam ter respostas
    cursor.execute('''
        DELETE FROM respostas
        WHERE questao_id IN (
            SELECT q.id
            FROM questoes q
            JOIN tipos_questao t ON q.tipo_questao_id = t.id
            WHERE t.list_options = 0 AND t.correcao_automatica = 0
        )
    ''')

# Função pública para limpeza de respostas inválidas
def limpar_respostas_invalidas():
    conn = _get_connection()
    cursor = conn.cursor()
    _validar_integridade_respostas(cursor)
    conn.commit()
    conn.close()

def _limpar_resposta_incompativel(questao_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE respostas
        SET opcoes = '[]', opcao_correta = NULL
        WHERE questao_id = ?
    ''', (questao_id,))
    conn.commit()
    conn.close()

    inicializar_database()

