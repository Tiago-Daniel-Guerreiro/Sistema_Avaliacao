def get_contas_aluno_sem_turma():
    query = '''
        SELECT c.id, c.nome, c.email, c.id_cargo
        FROM contas c
        LEFT JOIN alunos a ON a.id_conta = c.id
        WHERE c.id_cargo = 3 AND (a.id IS NULL OR a.turma_id IS NULL)
    '''
    return _executar_select(query)
from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_alunos():
    query = '''
        SELECT 
            a.id, a.identificador, a.turma_id, a.id_conta,
            t.ano, t.identificador as turma_identificador,
            c.nome, c.email,
            t.ano || 'º ' || t.identificador as turma_display,
            c.nome as conta_display
        FROM alunos a
        LEFT JOIN turmas t ON a.turma_id = t.id
        LEFT JOIN contas c ON a.id_conta = c.id
    '''
    return _executar_select(query)

def get_aluno_by_id(aluno_id):
    query = '''
        SELECT 
            a.id, a.identificador, a.turma_id, a.id_conta,
            t.ano, t.identificador as turma_identificador,
            t.identificador as turma_nome,
            t.ano || 'º ' || t.identificador as turma_display,
            c.nome, c.email
        FROM alunos a
        LEFT JOIN turmas t ON a.turma_id = t.id
        LEFT JOIN contas c ON a.id_conta = c.id
        WHERE a.id = ?
    '''
    return _executar_select_um(query, (aluno_id,))

def get_alunos_by_turma(turma_id):
    query = '''
        SELECT 
            a.id, a.identificador, a.turma_id, a.id_conta,
            c.nome, c.email
        FROM alunos a
        LEFT JOIN contas c ON a.id_conta = c.id
        WHERE a.turma_id = ?
    '''
    return _executar_select(query, (turma_id,))

def get_aluno_by_conta_turma(conta_id, turma_id):
    query = '''
        SELECT 
            a.id, a.identificador, a.turma_id, a.id_conta,
            c.nome, c.email
        FROM alunos a
        LEFT JOIN contas c ON a.id_conta = c.id
        WHERE a.id_conta = ? AND a.turma_id = ?
    '''
    return _executar_select_um(query, (conta_id, turma_id))

def get_aluno_by_conta(conta_id):
    query = '''
        SELECT 
            a.id, a.identificador, a.turma_id, a.id_conta,
            c.nome, c.email
        FROM alunos a
        LEFT JOIN contas c ON a.id_conta = c.id
        WHERE a.id_conta = ?
        LIMIT 1
    '''
    return _executar_select_um(query, (conta_id,))

def add_aluno(identificador, turma_id, conta_id):
    if not identificador or not turma_id or not conta_id:
        return {'ok': False, 'aluno': None, 'erro': 'Identificador, turma_id e conta_id são obrigatórios'}

    query = '''
        INSERT INTO alunos (identificador, turma_id, id_conta) 
        VALUES (?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (identificador, turma_id, conta_id))
    if novo_id:
        return {'ok': True, 'aluno': get_aluno_by_id(novo_id)}
    return {'ok': False, 'aluno': None}

def update_aluno(aluno_id, conta_id=None, turma_id=None, identificador=None):
    aluno_atual = get_aluno_by_id(aluno_id)
    if not aluno_atual:
        return {'ok': False, 'aluno': None}
    
    # Usar valores existentes se não fornecidos
    if not conta_id:
        conta_id = aluno_atual.get('id_conta')
    if not turma_id:
        turma_id = aluno_atual.get('turma_id')
    if not identificador:
        identificador = aluno_atual.get('identificador')
    
    query = '''
        UPDATE alunos 
        SET identificador = ?, turma_id = ?, id_conta = ? 
        WHERE id = ?
    '''
    if _executar_query(query, (identificador, turma_id, conta_id, aluno_id)):
        return {'ok': True, 'aluno': get_aluno_by_id(aluno_id)}
    return {'ok': False, 'aluno': None}

def delete_aluno(aluno_id):
    aluno = get_aluno_by_id(aluno_id)
    query = 'DELETE FROM alunos WHERE id = ?'
    if _executar_query(query, (aluno_id,)):
        return {'ok': True, 'aluno': aluno}
    return {'ok': False, 'aluno': None}

