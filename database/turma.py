from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id
from datetime import datetime

def get_turmas():
    query = "SELECT id, ano, identificador, ano || 'º ' || identificador as turma_display FROM turmas ORDER BY identificador"
    return _executar_select(query)

def get_turma_by_id(turma_id):
    query = 'SELECT * FROM turmas WHERE id = ?'
    return _executar_select_um(query, (turma_id,))

def add_turma(ano, identificador):    
    if not identificador:
        return {'ok': False, 'erro': 'Identificador é obrigatório'}
    
    if not ano:
        return {'ok': False, 'erro': 'Ano é obrigatório'}
    
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        return {'ok': False, 'erro': 'Ano inválido'}
    
    query = '''
        INSERT INTO turmas (ano, identificador) 
        VALUES (?, ?)
    '''
    novo_id = _executar_query_com_id(query, (ano, identificador))
    if novo_id:
        resultado = _executar_select_um('SELECT * FROM turmas WHERE id = ?', (novo_id,))
        return {'ok': True, 'turma': resultado}
    return {'ok': False, 'erro': 'Erro ao criar turma'}

def update_turma(turma_id, ano, identificador):
    query = '''
        UPDATE turmas 
        SET ano = ?, identificador = ? 
        WHERE id = ?
    '''
    if _executar_query(query, (ano, identificador, turma_id)):
        resultado = _executar_select_um('SELECT * FROM turmas WHERE id = ?', (turma_id,))
        return {'ok': True, 'turma': resultado}
    return {'ok': False, 'turma': None}

def delete_turma(turma_id):
    turma = _executar_select_um('SELECT * FROM turmas WHERE id = ?', (turma_id,))
    query = 'DELETE FROM turmas WHERE id = ?'
    if _executar_query(query, (turma_id,)):
        return {'ok': True, 'turma': turma}
    return {'ok': False, 'turma': None}

def add_disciplina_turma(turma_id, disciplina_id, professor_id):
    query = '''
        INSERT INTO disciplina_turma (turma_id, disciplina_id, professor_id) 
        VALUES (?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (turma_id, disciplina_id, professor_id))
    if novo_id:
        resultado = _executar_select_um('SELECT * FROM disciplina_turma WHERE id = ?', (novo_id,))
        return {'ok': True, 'disciplina_turma': resultado}
    return {'ok': False, 'disciplina_turma': None}

