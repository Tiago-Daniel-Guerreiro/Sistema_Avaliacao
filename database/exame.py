from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_exames():
    query = '''
        SELECT 
            e.id, e.disciplina_turma_id, e.titulo, e.data_hora_inicio, e.duracao_minutos, e.publico,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            d.id as disc_id, d.nome as disc_nome,
            t.id as turma_id, t.ano, t.identificador as turma_identificador,
            c.id as prof_id, c.nome as prof_nome, c.email as prof_email,
            (d.nome || ' ' || t.ano || 'º ' || t.identificador) as disciplina_turma_display
        FROM exames e
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN contas c ON dt.professor_id = c.id
    '''
    return _executar_select(query)

def get_exame_by_id(exame_id):
    query = '''
        SELECT 
            e.id, e.disciplina_turma_id, e.titulo, e.data_hora_inicio, e.duracao_minutos, e.publico,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            d.id as disc_id, d.nome as disc_nome,
            t.id as turma_id, t.ano, t.identificador as turma_identificador,
            c.id as prof_id, c.nome as prof_nome, c.email as prof_email,
            (d.nome || ' ' || t.ano || 'º ' || t.identificador) as disciplina_turma_display
        FROM exames e
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE e.id = ?
    '''
    return _executar_select_um(query, (exame_id,))

def get_exames_by_turma(turma_id):
    query = '''
        SELECT 
            e.id, e.disciplina_turma_id, e.titulo, e.data_hora_inicio, e.duracao_minutos, e.publico,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            d.id as disc_id, d.nome as disc_nome,
            t.id as turma_id, t.ano, t.identificador as turma_identificador,
            c.id as prof_id, c.nome as prof_nome, c.email as prof_email
        FROM exames e
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE dt.turma_id = ?
    '''
    return _executar_select(query, (turma_id,))

def get_exames_by_disciplina_turma(disciplina_turma_id):
    query = '''
        SELECT 
            e.id, e.disciplina_turma_id, e.titulo, e.data_hora_inicio, e.duracao_minutos, e.publico,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            d.id as disc_id, d.nome as disc_nome,
            t.id as turma_id, t.ano, t.identificador as turma_identificador,
            c.id as prof_id, c.nome as prof_nome, c.email as prof_email
        FROM exames e
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE e.disciplina_turma_id = ?
    '''
    return _executar_select(query, (disciplina_turma_id,))

def add_exame(disciplina_turma_id, titulo, data_hora_inicio, duracao_minutos, publico=1):
    query = '''
        INSERT INTO exames (disciplina_turma_id, titulo, data_hora_inicio, duracao_minutos, publico) 
        VALUES (?, ?, ?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (disciplina_turma_id, titulo, data_hora_inicio, duracao_minutos, int(publico)))
    if novo_id:
        return {'ok': True, 'exame': get_exame_by_id(novo_id)}
    return {'ok': False, 'exame': None}

def update_exame(exame_id, disciplina_turma_id=None, titulo=None, data_hora_inicio=None, duracao_minutos=None, publico=None):
    atual = get_exame_by_id(exame_id)
    if not atual:
        return {'ok': False, 'erro': 'Exame não encontrado'}
    
    disciplina_turma_id = disciplina_turma_id if disciplina_turma_id is not None else atual['disciplina_turma_id']
    titulo = titulo if titulo is not None else atual['titulo']
    data_hora_inicio = data_hora_inicio if data_hora_inicio is not None else atual['data_hora_inicio']
    duracao_minutos = duracao_minutos if duracao_minutos is not None else atual['duracao_minutos']
    publico = int(publico) if publico is not None else atual.get('publico', 1)
    
    query = '''
        UPDATE exames 
        SET disciplina_turma_id = ?, titulo = ?, data_hora_inicio = ?, duracao_minutos = ?, publico = ? 
        WHERE id = ?
    '''
    if _executar_query(query, (disciplina_turma_id, titulo, data_hora_inicio, duracao_minutos, publico, exame_id)):
        return {'ok': True, 'exame': get_exame_by_id(exame_id)}
    return {'ok': False, 'erro': 'Erro ao atualizar exame'}

def delete_exame(exame_id):
    exame = get_exame_by_id(exame_id)
    query = 'DELETE FROM exames WHERE id = ?'
    if _executar_query(query, (exame_id,)):
        return {'ok': True, 'exame': exame}
    return {'ok': False, 'exame': None}