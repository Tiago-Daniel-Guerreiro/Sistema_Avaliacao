from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_questoes():
    query = '''
        SELECT 
            q.id, q.texto, q.tipo_questao_id, q.exame_id, q.numero_questao,
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome,
            e.id as exame_id, e.titulo as exame_titulo,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id,
            d.nome as disciplina_nome, d.codigo as disciplina_codigo,
            tm.ano, tm.identificador,
            t.nome as tipo_questao_display,
            dt.id as disciplina_turma_display,
            e.titulo as exame_display,
            r.id as resposta_id
        FROM questoes q
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        LEFT JOIN exames e ON q.exame_id = e.id
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN disciplinas d ON dt.disciplina_id = d.id
        LEFT JOIN turmas tm ON dt.turma_id = tm.id
        LEFT JOIN respostas r ON r.questao_id = q.id
    '''
    return _executar_select(query)

def get_questao_by_id(questao_id):
    query = '''
        SELECT 
            q.id, q.texto, q.tipo_questao_id, q.exame_id, q.numero_questao,
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome,
            e.id as exame_id, e.titulo as exame_titulo,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id,
            r.id as resposta_id
        FROM questoes q
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        LEFT JOIN exames e ON q.exame_id = e.id
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN respostas r ON r.questao_id = q.id
        WHERE q.id = ?
    '''
    return _executar_select_um(query, (questao_id,))

def get_questoes_by_professor(professor_id):
    query = '''
        SELECT 
            q.id, q.texto, q.tipo_questao_id, q.numero_questao,
            q.pontuacao_maxima,
            e.disciplina_turma_id,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            t.id as tipo_id, t.nome as tipo_nome
        FROM questoes q
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        LEFT JOIN exames e ON q.exame_id = e.id
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        WHERE dt.professor_id = ?
    '''
    return _executar_select(query, (professor_id,))

def get_questoes_by_tipo(tipo_questao_id):
    query = '''
        SELECT 
            q.id, q.texto, q.tipo_questao_id, q.numero_questao,
            q.pontuacao_maxima,
            e.disciplina_turma_id,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            t.id as tipo_id, t.nome as tipo_nome
        FROM questoes q
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        LEFT JOIN exames e ON q.exame_id = e.id
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        WHERE q.tipo_questao_id = ?
    '''
    return _executar_select(query, (tipo_questao_id,))

def get_questoes_by_exame(exame_id):
    query = '''
        SELECT 
            q.id, q.texto, q.tipo_questao_id, q.exame_id, q.numero_questao,
            q.pontuacao_maxima,
            e.disciplina_turma_id,
            dt.id as dt_id, dt.turma_id, dt.disciplina_id, dt.professor_id,
            t.id as tipo_id, t.nome as tipo_nome, t.nome as tipo_questao, t.nome as tipo_questao_display,
            r.id as resposta_id
        FROM questoes q
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        LEFT JOIN exames e ON q.exame_id = e.id
        LEFT JOIN disciplina_turma dt ON e.disciplina_turma_id = dt.id
        LEFT JOIN respostas r ON r.questao_id = q.id
        WHERE q.exame_id = ?
        ORDER BY q.numero_questao
    '''
    return _executar_select(query, (exame_id,))

def add_questao(exame_id, numero_questao, tipo_questao_id, texto, pontuacao_maxima):
    query = '''
        INSERT INTO questoes (texto, tipo_questao_id, exame_id, numero_questao, pontuacao_maxima) 
        VALUES (?, ?, ?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (texto, tipo_questao_id, exame_id, numero_questao, pontuacao_maxima))
    if novo_id:
        return {'ok': True, 'questao': get_questao_by_id(novo_id)}
    return {'ok': False, 'questao': None}

def update_questao(questao_id, exame_id, numero_questao, tipo_questao_id, texto, pontuacao_maxima):
    query = '''
        UPDATE questoes 
        SET texto = ?, tipo_questao_id = ?, pontuacao_maxima = ?, exame_id = ?, numero_questao = ? 
        WHERE id = ?
    '''
    if _executar_query(query, (texto, tipo_questao_id, pontuacao_maxima, exame_id, numero_questao, questao_id)):
        return {'ok': True, 'questao': get_questao_by_id(questao_id)}
    return {'ok': False, 'questao': None}

def delete_questao(questao_id):
    questao = get_questao_by_id(questao_id)
    query = 'DELETE FROM questoes WHERE id = ?'
    if _executar_query(query, (questao_id,)):
        return {'ok': True, 'questao': questao}
    return {'ok': False, 'questao': None}

