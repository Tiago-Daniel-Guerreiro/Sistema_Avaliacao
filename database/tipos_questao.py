from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_tipos_questao():
    query = "SELECT * FROM tipos_questao ORDER BY nome"
    return _executar_select(query)

def get_tipo_questao_by_id(tipo_id):
    query = "SELECT * FROM tipos_questao WHERE id = ?"
    return _executar_select_um(query, (tipo_id,))

def get_tipo_questao_by_nome(nome):
    query = "SELECT * FROM tipos_questao WHERE nome = ?"
    return _executar_select_um(query, (nome,))

def get_tipo_questao_by_input_file(input_file):
    query = "SELECT * FROM tipos_questao WHERE input_file = ? ORDER BY correcao_automatica DESC"
    return _executar_select(query, (input_file,))

def add_tipo_questao(input_file, nome, list_options=False, correcao_automatica=True, multiplas_respostas=False):
    query = "INSERT INTO tipos_questao (input_file, nome, list_options, correcao_automatica, multiplas_respostas) VALUES (?, ?, ?, ?, ?)"
    novo_id = _executar_query_com_id(query, (input_file, nome, int(list_options), int(correcao_automatica), int(multiplas_respostas)))
    if novo_id:
        return {'ok': True, 'tipo_questao': get_tipo_questao_by_id(novo_id)}
    return {'ok': False, 'tipo_questao': None}

def add_tipo_questao_or_get(input_file, nome, list_options=False, correcao_automatica=True, multiplas_respostas=False):
    """Adiciona tipo de questão ou retorna o existente se já houver."""
    tipo_existente = get_tipo_questao_by_nome(nome)
    if tipo_existente:
        return {'ok': True, 'tipo_questao': tipo_existente}
    return add_tipo_questao(input_file, nome, list_options, correcao_automatica, multiplas_respostas)

def update_tipo_questao(tipo_id, input_file, nome, list_options=False, correcao_automatica=True, multiplas_respostas=False):
    query = "UPDATE tipos_questao SET input_file = ?, nome = ?, list_options = ?, correcao_automatica = ?, multiplas_respostas = ? WHERE id = ?"
    if _executar_query(query, (input_file, nome, int(list_options), int(correcao_automatica), int(multiplas_respostas), tipo_id)):
        return {'ok': True, 'tipo_questao': get_tipo_questao_by_id(tipo_id)}
    return {'ok': False, 'tipo_questao': None}

def delete_tipo_questao(tipo_id):
    tipo = get_tipo_questao_by_id(tipo_id)
    query = "DELETE FROM tipos_questao WHERE id = ?"
    if _executar_query(query, (tipo_id,)):
        return {'ok': True, 'tipo_questao': tipo}
    return {'ok': False, 'tipo_questao': None}
