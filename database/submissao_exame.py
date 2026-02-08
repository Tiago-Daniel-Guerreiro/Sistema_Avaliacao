from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id
from datetime import datetime, timedelta
from .questao import get_questao_by_id

def get_submissoes_exame():
    query = '''
        SELECT 
            se.id, se.exame_id, se.aluno_id, se.data_hora_inicio, se.data_hora_fim, se.estado,
            e.id as exam_id, e.titulo as exam_titulo, e.duracao_minutos, e.data_hora_inicio as exam_data_inicio,
            a.id as aluno_id, a.identificador,
            c.id as conta_id, c.nome as aluno_nome, c.email as aluno_email
        FROM submissoes_exame se
        JOIN exames e ON se.exame_id = e.id
        JOIN alunos a ON se.aluno_id = a.id
        JOIN contas c ON a.id_conta = c.id
        ORDER BY se.data_hora_inicio DESC
    '''
    return _executar_select(query)

def get_submissao_exame_by_id(submissao_id):
    query = '''
        SELECT 
            se.id, se.exame_id, se.aluno_id, se.data_hora_inicio, se.data_hora_fim, se.estado,
            e.id as exam_id, e.titulo as exam_titulo, e.duracao_minutos, e.data_hora_inicio as exam_data_inicio,
            a.id as aluno_id, a.identificador,
            c.id as conta_id, c.nome as aluno_nome, c.email as aluno_email
        FROM submissoes_exame se
        JOIN exames e ON se.exame_id = e.id
        JOIN alunos a ON se.aluno_id = a.id
        JOIN contas c ON a.id_conta = c.id
        WHERE se.id = ?
    '''
    return _executar_select_um(query, (submissao_id,))

def get_submissoes_exame_by_exame(exame_id):
    query = '''
        SELECT 
            se.id, se.exame_id, se.aluno_id, se.data_hora_inicio, se.data_hora_fim, se.estado,
            e.id as exam_id, e.titulo as exam_titulo, e.duracao_minutos, e.data_hora_inicio as exam_data_inicio,
            a.id as aluno_id, a.identificador,
            c.id as conta_id, c.nome as aluno_nome, c.email as aluno_email
        FROM submissoes_exame se
        JOIN exames e ON se.exame_id = e.id
        JOIN alunos a ON se.aluno_id = a.id
        JOIN contas c ON a.id_conta = c.id
        WHERE se.exame_id = ?
        ORDER BY c.nome
    '''
    return _executar_select(query, (exame_id,))

def get_submissoes_exame_by_aluno(aluno_id):
    query = '''
        SELECT 
            se.id, se.exame_id, se.aluno_id, se.data_hora_inicio, se.data_hora_fim, se.estado,
            e.id as exam_id, e.titulo as exam_titulo, e.duracao_minutos, e.data_hora_inicio as exam_data_inicio,
            a.id as aluno_id, a.identificador,
            c.id as conta_id, c.nome as aluno_nome, c.email as aluno_email
        FROM submissoes_exame se
        JOIN exames e ON se.exame_id = e.id
        JOIN alunos a ON se.aluno_id = a.id
        JOIN contas c ON a.id_conta = c.id
        WHERE se.aluno_id = ?
        ORDER BY se.data_hora_inicio DESC
    '''
    return _executar_select(query, (aluno_id,))

def get_submissoes_exame_by_exame_aluno(exame_id, aluno_id):
    query = '''
        SELECT 
            se.id, se.exame_id, se.aluno_id, se.data_hora_inicio, se.data_hora_fim, se.estado,
            e.id as exam_id, e.titulo as exam_titulo, e.duracao_minutos, e.data_hora_inicio as exam_data_inicio,
            a.id as aluno_id, a.identificador,
            c.id as conta_id, c.nome as aluno_nome, c.email as aluno_email
        FROM submissoes_exame se
        JOIN exames e ON se.exame_id = e.id
        JOIN alunos a ON se.aluno_id = a.id
        JOIN contas c ON a.id_conta = c.id
        WHERE se.exame_id = ? AND se.aluno_id = ?
    '''
    return _executar_select_um(query, (exame_id, aluno_id))

def add_submissao_exame(exame_id, aluno_id):
    try:
        data_hora_inicio = datetime.now().isoformat()
        
        query = '''
            INSERT INTO submissoes_exame (exame_id, aluno_id, data_hora_inicio, estado)
            VALUES (?, ?, ?, ?)
        '''
        novo_id = _executar_query_com_id(query, (exame_id, aluno_id, data_hora_inicio, 'em_andamento'))
        
        if novo_id:
            return {
                'ok': True,
                'submissao_id': novo_id,
                'exame_id': exame_id,
                'aluno_id': aluno_id,
                'data_hora_inicio': data_hora_inicio
            }
        return {'ok': False, 'erro': 'Erro ao criar submissão'}
    except Exception as e:
        return {'ok': False, 'erro': str(e)}

def update_submissao_exame_fim(submissao_id):
    try:
        data_hora_fim = datetime.now().isoformat()
        
        query = '''
            UPDATE submissoes_exame 
            SET data_hora_fim = ?, estado = ?
            WHERE id = ?
        '''
        _executar_query(query, (data_hora_fim, 'finalizado', submissao_id))
        
        return {'ok': True, 'mensagem': 'Submissão finalizada'}
    except Exception as e:
        return {'ok': False, 'erro': str(e)}

def get_submissoes_questao_by_submissao(submissao_exame_id):
    query = '''
        SELECT 
            sq.id, sq.submissao_exame_id, sq.questao_id, sq.resposta, 
            sq.data_hora_resposta, sq.pontuacao_atribuida, sq.estado,
            q.id as quest_id, q.texto, q.numero_questao, q.tipo_questao_id, 
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome
        FROM submissoes_questao sq
        JOIN questoes q ON sq.questao_id = q.id
        JOIN tipos_questao t ON q.tipo_questao_id = t.id
        WHERE sq.submissao_exame_id = ?
        ORDER BY q.numero_questao
    '''
    return _executar_select(query, (submissao_exame_id,))

def get_submissao_questao_by_id(submissao_questao_id):
    query = '''
        SELECT 
            sq.id, sq.submissao_exame_id, sq.questao_id, sq.resposta, 
            sq.data_hora_resposta, sq.pontuacao_atribuida, sq.estado,
            q.id as quest_id, q.texto, q.numero_questao, q.tipo_questao_id, 
            q.pontuacao_maxima,
            t.id as tipo_id, t.nome as tipo_nome
        FROM submissoes_questao sq
        JOIN questoes q ON sq.questao_id = q.id
        JOIN tipos_questao t ON q.tipo_questao_id = t.id
        WHERE sq.id = ?
    '''
    return _executar_select_um(query, (submissao_questao_id,))

def add_submissao_questao(submissao_exame_id, questao_id, resposta, pontuacao=None):
    try:
        data_hora_resposta = datetime.now().isoformat()

        # Validar que a pontuação não ultrapassa o máximo
        questao = get_questao_by_id(questao_id)
        if questao and pontuacao is not None:
            pontuacao_maxima = questao.get('pontuacao_maxima', 0)
            if pontuacao > pontuacao_maxima:
                return {'ok': False, 'erro': f'Pontuação não pode ser superior a {pontuacao_maxima}'}

        # Verificar se já existe resposta para esta questão
        query_check = '''
            SELECT id FROM submissoes_questao
            WHERE submissao_exame_id = ? AND questao_id = ?
        '''
        resultado = _executar_select_um(query_check, (submissao_exame_id, questao_id))

        if resultado:
            # Atualizar resposta existente
            if pontuacao is not None:
                query = '''
                    UPDATE submissoes_questao
                    SET resposta = ?, data_hora_resposta = ?, pontuacao_atribuida = ?, estado = ?
                    WHERE id = ?
                '''
                _executar_query(query, (resposta, data_hora_resposta, pontuacao, 'respondida', resultado['id']))
            else:
                query = '''
                    UPDATE submissoes_questao
                    SET resposta = ?, data_hora_resposta = ?, estado = ?
                    WHERE id = ?
                '''
                _executar_query(query, (resposta, data_hora_resposta, 'respondida', resultado['id']))
            return {'ok': True, 'mensagem': 'Resposta atualizada'}

        # Criar nova resposta
        query = '''
            INSERT INTO submissoes_questao
            (submissao_exame_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        novo_id = _executar_query_com_id(
            query,
            (submissao_exame_id, questao_id, resposta, data_hora_resposta, pontuacao or 0, 'respondida')
        )
        if novo_id:
            return {'ok': True, 'submissao_questao_id': novo_id}
        return {'ok': False, 'erro': 'Erro ao registar resposta'}
    except Exception as e:
        return {'ok': False, 'erro': str(e)}

def update_pontuacao_questao(submissao_questao_id, pontuacao):
    try:
        query = '''
            UPDATE submissoes_questao 
            SET pontuacao_atribuida = ?, estado = ?
            WHERE id = ?
        '''
        _executar_query(query, (pontuacao, 'corrigida', submissao_questao_id))
        return {'ok': True, 'mensagem': 'Pontuação atualizada'}
    except Exception as e:
        return {'ok': False, 'erro': str(e)}
