from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_disciplina_turmas():
    query = '''
        SELECT 
            dt.id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            t.ano, t.identificador as turma_identificador,
            d.nome as disciplina_nome, d.codigo as disciplina_codigo,
            c.nome as professor_nome, c.email as professor_email,
            t.ano || 'º ' || t.identificador as turma_display,
            d.nome as disciplina_display,
            c.nome as professor_display,
            d.nome || ' ' || t.ano || 'º ' || t.identificador as disciplina_turma_display
        FROM disciplina_turma dt
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        ORDER BY t.identificador, d.nome
    '''
    return _executar_select(query)

def get_disciplina_turma_by_id(disciplina_turma_id):
    query = '''
        SELECT 
            dt.id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            t.ano, t.identificador as turma_identificador,
            d.nome as disciplina_nome, d.codigo as disciplina_codigo,
            c.nome as professor_nome, c.email as professor_email
        FROM disciplina_turma dt
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE dt.id = ?
    '''
    return _executar_select_um(query, (disciplina_turma_id,))

def get_turmas_by_professor(professor_id):
    query = '''
        SELECT DISTINCT
            t.id, t.ano, t.identificador,
            t.ano || 'º ' || t.identificador as turma_display
        FROM disciplina_turma dt
        LEFT JOIN turmas t ON dt.turma_id = t.id
        WHERE dt.professor_id = ?
        ORDER BY t.identificador
    '''
    turmas = _executar_select(query, (professor_id,))
    # Adicionar link para cada turma
    for turma in turmas:
        turma['link'] = f"/turmas/{turma['id']}"
    return turmas

def get_disciplinas_by_aluno(turma_id):
    query = '''
        SELECT 
            dt.id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            d.nome as disciplina_nome, d.codigo as disciplina_codigo,
            c.nome as professor_nome, c.email as professor_email,
            d.nome || ' (' || c.nome || ')' as disciplina_display
        FROM disciplina_turma dt
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE dt.turma_id = ?
        ORDER BY d.nome
    '''
    disciplinas = _executar_select(query, (turma_id,))
    # Adicionar link para cada disciplina
    for disciplina in disciplinas:
        disciplina['link'] = f"/disciplina-turma/{disciplina['id']}"
    return disciplinas

def get_disciplinas_by_turma(turma_id):
    query = '''
        SELECT 
            dt.id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            d.nome as disciplina_nome, d.codigo as disciplina_codigo,
            c.nome as professor_nome, c.email as professor_email
        FROM disciplina_turma dt
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE dt.turma_id = ?
    '''
    return _executar_select(query, (turma_id,))

def get_turmas_by_disciplina(disciplina_id):
    query = '''
        SELECT 
            dt.id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            t.ano, t.identificador as turma_identificador,
            c.nome as professor_nome, c.email as professor_email
        FROM disciplina_turma dt
        LEFT JOIN turmas t ON dt.turma_id = t.id
        LEFT JOIN contas c ON dt.professor_id = c.id
        WHERE dt.disciplina_id = ?
    '''
    return _executar_select(query, (disciplina_id,))

def add_disciplina_turma(turma_id, disciplina_id, professor_id):
    query = '''
        INSERT INTO disciplina_turma (turma_id, disciplina_id, professor_id) 
        VALUES (?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (turma_id, disciplina_id, professor_id))
    if novo_id:
        return {'ok': True, 'disciplina_turma': get_disciplina_turma_by_id(novo_id)}
    return {'ok': False, 'disciplina_turma': None}

def update_disciplina_turma(disciplina_turma_id, turma_id, disciplina_id, professor_id):
    query = '''
        UPDATE disciplina_turma 
        SET turma_id = ?, disciplina_id = ?, professor_id = ? 
        WHERE id = ?
    '''
    if _executar_query(query, (turma_id, disciplina_id, professor_id, disciplina_turma_id)):
        return {'ok': True, 'disciplina_turma': get_disciplina_turma_by_id(disciplina_turma_id)}
    return {'ok': False, 'disciplina_turma': None}

def delete_disciplina_turma(disciplina_turma_id):
    disciplina_turma = get_disciplina_turma_by_id(disciplina_turma_id)
    query = 'DELETE FROM disciplina_turma WHERE id = ?'
    if _executar_query(query, (disciplina_turma_id,)):
        return {'ok': True, 'disciplina_turma': disciplina_turma}
    return {'ok': False, 'disciplina_turma': None}