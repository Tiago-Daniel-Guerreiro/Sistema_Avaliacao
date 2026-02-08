from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id
import json

def get_respostas():
    query = '''
        SELECT 
            r.id, r.questao_id, r.opcoes, r.opcao_correta,
            q.id as q_id, q.texto as q_texto, q.tipo_questao_id, q.exame_id,
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome,
            SUBSTR(q.texto, 1, 50) as questao_display
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
    '''
    resultados = _executar_select(query)
    for resultado in resultados:
        if resultado.get('opcoes'):
            resultado['opcoes'] = json.loads(resultado['opcoes'])
    return resultados

def get_resposta_by_id(resposta_id):
    query = '''
        SELECT 
            r.id, r.questao_id, r.opcoes, r.opcao_correta,
            q.id as q_id, q.texto as q_texto, q.tipo_questao_id, q.exame_id,
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        WHERE r.id = ?
    '''
    resultado = _executar_select_um(query, (resposta_id,))
    if resultado and resultado.get('opcoes'):
        resultado['opcoes'] = json.loads(resultado['opcoes'])
    return resultado

def get_respostas_by_questao(questao_id):
    query = '''
        SELECT 
            r.id, r.questao_id, r.opcoes, r.opcao_correta,
            q.id as q_id, q.texto as q_texto, q.tipo_questao_id, q.exame_id,
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        LEFT JOIN tipos_questao t ON q.tipo_questao_id = t.id
        WHERE r.questao_id = ?
    '''
    resultados = _executar_select(query, (questao_id,))
    for resultado in resultados:
        if resultado.get('opcoes'):
            resultado['opcoes'] = json.loads(resultado['opcoes'])
    return resultados

def add_resposta(questao_id, opcoes, opcao_correta=None):
    opcoes_json = json.dumps(opcoes) if not isinstance(opcoes, str) else opcoes
    query = '''
        INSERT INTO respostas (questao_id, opcoes, opcao_correta) 
        VALUES (?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (questao_id, opcoes_json, opcao_correta))
    if novo_id:
        return {'ok': True, 'resposta': get_resposta_by_id(novo_id)}
    return {'ok': False, 'resposta': None}

def update_resposta(resposta_id, opcoes, opcao_correta=None):
    opcoes_json = json.dumps(opcoes) if not isinstance(opcoes, str) else opcoes
    query = '''
        UPDATE respostas 
        SET opcoes = ?, opcao_correta = ?
        WHERE id = ?
    '''
    if _executar_query(query, (opcoes_json, opcao_correta, resposta_id)):
        return {'ok': True, 'resposta': get_resposta_by_id(resposta_id)}
    return {'ok': False, 'resposta': None}

def delete_resposta(resposta_id):
    resposta = get_resposta_by_id(resposta_id)
    query = 'DELETE FROM respostas WHERE id = ?'
    if _executar_query(query, (resposta_id,)):
        return {'ok': True, 'resposta': resposta}
    return {'ok': False, 'resposta': None}

