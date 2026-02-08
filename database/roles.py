from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_roles():
    query = 'SELECT * FROM roles'
    return _executar_select(query)

def get_role_by_id(role_id):
    query = 'SELECT * FROM roles WHERE id = ?'
    return _executar_select_um(query, (role_id,))

def get_role_by_nome(nome):
    query = 'SELECT * FROM roles WHERE nome = ?'
    return _executar_select_um(query, (nome,))

def add_role(nome):
    if get_role_by_nome(nome):
        return {'ok': False, 'role': None}
    
    query = 'INSERT INTO roles (nome) VALUES (?)'
    novo_id = _executar_query_com_id(query, (nome,))
    
    if novo_id:
        return {'ok': True, 'role': get_role_by_id(novo_id)}
    return {'ok': False, 'role': None}

def update_role(role_id, nome):
    query = 'UPDATE roles SET nome = ? WHERE id = ?'
    if _executar_query(query, (nome, role_id)):
        return {'ok': True, 'role': get_role_by_id(role_id)}
    return {'ok': False, 'role': None}

def delete_role(role_id):
    role = get_role_by_id(role_id)
    query = 'DELETE FROM roles WHERE id = ?'
    if _executar_query(query, (role_id,)):
        return {'ok': True, 'role': role}
    return {'ok': False, 'role': None}
