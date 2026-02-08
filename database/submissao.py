from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id
from datetime import datetime

def get_submissoes_by_aluno_exame_questao(aluno_id, exame_id):
    query = '''
        SELECT 
            s.id, s.exame_id, s.aluno_id, s.questao_id, s.resposta, 
            s.data_hora_resposta, s.pontuacao_atribuida,
            e.id as exame_id, e.titulo as exame_titulo, e.data_hora_inicio, e.duracao_minutos,
            a.id as aluno_id, a.identificador,
            q.id as questao_id, q.texto as questao_texto, q.numero_questao
        FROM submissoes s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN questoes q ON s.questao_id = q.id
        WHERE s.aluno_id = ? AND s.exame_id = ?
        ORDER BY q.numero_questao
    '''
    return _executar_select(query, (aluno_id, exame_id))

def get_submissoes():
    query = '''
        SELECT 
            s.id, s.exame_id, s.aluno_id, s.questao_id, s.resposta, 
            s.data_hora_resposta, s.pontuacao_atribuida,
            e.id as exame_id, e.titulo as exame_titulo, e.data_hora_inicio, e.duracao_minutos,
            a.id as aluno_id, a.identificador,
            q.id as questao_id, q.texto as questao_texto,
            e.titulo as exame_display,
            a.identificador as aluno_display,
            SUBSTR(q.texto, 1, 50) as questao_display
        FROM submissoes s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN questoes q ON s.questao_id = q.id
    '''
    return _executar_select(query)

def get_submissao_by_id(submissao_id):
    query = '''
        SELECT 
            s.id, s.exame_id, s.aluno_id, s.questao_id, s.resposta, 
            s.data_hora_resposta, s.pontuacao_atribuida,
            e.id as exame_id, e.titulo as exame_titulo, e.data_hora_inicio, e.duracao_minutos,
            a.id as aluno_id, a.identificador,
            q.id as questao_id, q.texto as questao_texto
        FROM submissoes s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN questoes q ON s.questao_id = q.id
        WHERE s.id = ?
    '''
    return _executar_select_um(query, (submissao_id,))

def get_submissoes_by_aluno(aluno_id):
    query = '''
        SELECT 
            s.id, s.exame_id, s.aluno_id, s.questao_id, s.resposta, 
            s.data_hora_resposta, s.pontuacao_atribuida,
            e.id as exame_id, e.titulo as exame_titulo, e.data_hora_inicio, e.duracao_minutos,
            a.id as aluno_id, a.identificador,
            q.id as questao_id, q.texto as questao_texto
        FROM submissoes s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN questoes q ON s.questao_id = q.id
        WHERE s.aluno_id = ?
    '''
    return _executar_select(query, (aluno_id,))

def get_submissoes_by_exame(exame_id):
    query = '''
        SELECT 
            s.id, s.exame_id, s.aluno_id, s.questao_id, s.resposta, 
            s.data_hora_resposta, s.pontuacao_atribuida,
            e.id as exame_id, e.titulo as exame_titulo, e.data_hora_inicio, e.duracao_minutos,
            a.id as aluno_id, a.identificador,
            q.id as questao_id, q.texto as questao_texto
        FROM submissoes s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN questoes q ON s.questao_id = q.id
        WHERE s.exame_id = ?
    '''
    return _executar_select(query, (exame_id,))

def get_submissoes_by_aluno_exame(aluno_id, exame_id):
    query = '''
        SELECT 
            s.id, s.exame_id, s.aluno_id, s.questao_id, s.resposta, 
            s.data_hora_resposta, s.pontuacao_atribuida,
            e.id as exame_id, e.titulo as exame_titulo, e.data_hora_inicio, e.duracao_minutos,
            a.id as aluno_id, a.identificador,
            q.id as questao_id, q.texto as questao_texto
        FROM submissoes s
        JOIN exames e ON s.exame_id = e.id
        JOIN alunos a ON s.aluno_id = a.id
        JOIN questoes q ON s.questao_id = q.id
        WHERE s.aluno_id = ? AND s.exame_id = ?
    '''
    return _executar_select(query, (aluno_id, exame_id))

def add_submissao(exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida=0):
    check_query = '''
        SELECT id FROM submissoes 
        WHERE exame_id = ? AND aluno_id = ? AND questao_id = ?
    '''
    existente = _executar_select_um(check_query, (exame_id, aluno_id, questao_id))
    if existente:
        return {'ok': False, 'erro': 'Já existe uma resposta para esta questão. Não é permitido responder novamente.'}
    
    query = '''
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida) 
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida))
    if novo_id:
        return {'ok': True, 'submissao': get_submissao_by_id(novo_id)}
    return {'ok': False, 'erro': 'Erro ao criar submissão'}

def update_submissao(submissao_id, exame_id=None, aluno_id=None, questao_id=None, resposta=None, data_hora_resposta=None, pontuacao_atribuida=None):
    atual = get_submissao_by_id(submissao_id)
    if not atual:
        return {'ok': False, 'erro': 'Submissão não encontrada'}
    
    # Usar valores atuais para campos não fornecidos
    exame_id = exame_id if exame_id is not None else atual['exame_id']
    aluno_id = aluno_id if aluno_id is not None else atual['aluno_id']
    questao_id = questao_id if questao_id is not None else atual['questao_id']
    resposta = resposta if resposta is not None else atual['resposta']
    data_hora_resposta = data_hora_resposta if data_hora_resposta is not None else atual['data_hora_resposta']
    pontuacao_atribuida = pontuacao_atribuida if pontuacao_atribuida is not None else atual.get('pontuacao_atribuida', 0)
    
    query = '''
        UPDATE submissoes 
        SET exame_id = ?, aluno_id = ?, questao_id = ?, resposta = ?, 
            data_hora_resposta = ?, pontuacao_atribuida = ? 
        WHERE id = ?
    '''
    if _executar_query(query, (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, submissao_id)):
        return {'ok': True, 'submissao': get_submissao_by_id(submissao_id)}
    return {'ok': False, 'erro': 'Erro ao atualizar submissão'}

def delete_submissao(submissao_id):
    submissao = get_submissao_by_id(submissao_id)
    query = 'DELETE FROM submissoes WHERE id = ?'
    if _executar_query(query, (submissao_id,)):
        return {'ok': True, 'submissao': submissao}
    return {'ok': False, 'submissao': None}


def get_submissoes_exame_by_aluno_exame(aluno_id, exame_id):
    query = '''
        SELECT 
            se.id, se.exame_id, se.aluno_id, se.data_hora_inicio, 
            se.data_hora_fim, se.estado,
            e.titulo as exame_titulo, e.data_hora_inicio as exame_inicio, e.duracao_minutos,
            a.identificador as aluno_display
        FROM submissoes_exame se
        JOIN exames e ON se.exame_id = e.id
        JOIN alunos a ON se.aluno_id = a.id
        WHERE se.aluno_id = ? AND se.exame_id = ?
    '''
    return _executar_select_um(query, (aluno_id, exame_id))

def get_questoes_respondidas_by_submissao(submissao_exame_id):
    query = '''
        SELECT 
            sq.id, sq.submissao_exame_id, sq.questao_id, sq.resposta, 
            sq.data_hora_resposta, sq.pontuacao_atribuida, sq.estado,
            q.texto, q.tipo_questao_id, q.opcoes, q.numero_questao,
            q.pontuacao_maxima, tq.nome as tipo_questao
        FROM submissoes_questao sq
        JOIN questoes q ON sq.questao_id = q.id
        JOIN tipos_questao tq ON q.tipo_questao_id = tq.id
        WHERE sq.submissao_exame_id = ?
        ORDER BY q.numero_questao
    '''
    return _executar_select(query, (submissao_exame_id,))

def get_submissoes_questao_by_exame_professor(exame_id):
    query = '''
        SELECT 
            sq.id, sq.submissao_exame_id, sq.questao_id, sq.resposta, 
            sq.data_hora_resposta, sq.pontuacao_atribuida, sq.estado,
            q.texto, q.numero_questao, q.pontuacao_maxima,
            se.aluno_id, a.identificador as aluno_display,
            tq.nome as tipo_questao
        FROM submissoes_questao sq
        JOIN questoes q ON sq.questao_id = q.id
        JOIN submissoes_exame se ON sq.submissao_exame_id = se.id
        JOIN alunos a ON se.aluno_id = a.id
        JOIN tipos_questao tq ON q.tipo_questao_id = tq.id
        WHERE se.exame_id = ?
        ORDER BY a.identificador, q.numero_questao
    '''
    return _executar_select(query, (exame_id,))

def create_submissao_exame(exame_id, aluno_id):
    data_hora_inicio = datetime.now().isoformat()
    
    query = '''
        INSERT INTO submissoes_exame (exame_id, aluno_id, data_hora_inicio, estado)
        VALUES (?, ?, ?, 'em_progresso')
    '''
    novo_id = _executar_query_com_id(query, (exame_id, aluno_id, data_hora_inicio))
    
    if novo_id:
        return get_submissoes_exame_by_aluno_exame(aluno_id, exame_id)
    return None

def create_submissao_questao(submissao_exame_id, questao_id, resposta):
    data_hora_resposta = datetime.now().isoformat()
    
    query = '''
        INSERT INTO submissoes_questao (submissao_exame_id, questao_id, resposta, data_hora_resposta)
        VALUES (?, ?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (submissao_exame_id, questao_id, resposta, data_hora_resposta))
    
    if novo_id:
        return _executar_select_um(
            'SELECT * FROM submissoes_questao WHERE id = ?',
            (novo_id,)
        )
    return None

def update_pontuacao_questao(submissao_questao_id, pontuacao_atribuida):
    query = '''
        UPDATE submissoes_questao
        SET pontuacao_atribuida = ?, estado = 'avaliado'
        WHERE id = ?
    '''
    if _executar_query(query, (pontuacao_atribuida, submissao_questao_id)):
        return _executar_select_um(
            'SELECT * FROM submissoes_questao WHERE id = ?',
            (submissao_questao_id,)
        )
    return None

def finalizar_submissao_exame(submissao_exame_id):
    data_hora_fim = datetime.now().isoformat()
    
    query = '''
        UPDATE submissoes_exame
        SET data_hora_fim = ?, estado = 'finalizado'
        WHERE id = ?
    '''
    return _executar_query(query, (data_hora_fim, submissao_exame_id))

def get_alunos_com_submissoes_exame(exame_id):
    query = '''
        SELECT DISTINCT
            a.id, a.identificador as aluno_display,
            COUNT(DISTINCT sq.id) as total_questoes_respondidas,
            SUM(CASE WHEN sq.pontuacao_atribuida IS NOT NULL THEN 1 ELSE 0 END) as questoes_avaliadas
        FROM submissoes_exame se
        JOIN alunos a ON se.aluno_id = a.id
        LEFT JOIN submissoes_questao sq ON se.id = sq.submissao_exame_id
        WHERE se.exame_id = ?
        GROUP BY a.id
    '''
    return _executar_select(query, (exame_id,))
