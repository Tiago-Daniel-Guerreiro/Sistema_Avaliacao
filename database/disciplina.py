from database.geral import _executar_query, _executar_query_com_id, _executar_select, _executar_select_um

def get_disciplinas():
    query = "SELECT * FROM disciplinas ORDER BY nome"
    return _executar_select(query, None)

def get_disciplina_by_id(disciplina_id):
    query = "SELECT * FROM disciplinas WHERE id = ?"
    return _executar_select_um(query, (disciplina_id,))

def add_disciplina(nome, codigo=None):
    try:        
        if not nome or len(nome.strip()) == 0:
            return {'ok': False, 'erro': 'Nome é obrigatório'}
        
        if not codigo:
            palavras = nome.upper().split()
            codigo = palavras[0][:6]
        
        query = "INSERT INTO disciplinas (nome, codigo) VALUES (?, ?)"
        novo_id = _executar_query_com_id(query, (nome, codigo))
        
        if novo_id:
            return {'ok': True, 'disciplina': get_disciplina_by_id(novo_id)}
        return {'ok': False, 'erro': 'Erro ao criar disciplina'}
    except Exception as e:
        return {'ok': False}

def update_disciplina(disciplina_id, nome, codigo=None):
    try:
        disciplina = get_disciplina_by_id(disciplina_id)
        if not disciplina:
            return {'ok': False}
        
        if not codigo:
            palavras = nome.upper().split()
            codigo = palavras[0][:6]
        
        query = "UPDATE disciplinas SET nome = ?, codigo = ? WHERE id = ?"
        if _executar_query(query, (nome, codigo, disciplina_id)):
            return {'ok': True}
        return {'ok': False}
    except Exception as e:
        return {'ok': False}

def delete_disciplina(disciplina_id):
    try:        
        disciplina = get_disciplina_by_id(disciplina_id)
        
        if not disciplina:
            return {'ok': False}
        
        query = "DELETE FROM disciplinas WHERE id = ?"
        sucesso = _executar_query(query, (disciplina_id,))
                
        if sucesso:
            return {'ok': True}
        return {'ok': False}
    except Exception as e:
        return {'ok': False}