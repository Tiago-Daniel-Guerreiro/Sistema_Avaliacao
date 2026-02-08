from .geral import _executar_select, _executar_select_um, _executar_query, _executar_query_com_id

def get_contas():
    query = '''
        SELECT 
            c.id, c.nome, c.email, c.id_cargo, c.senha,
            r.nome as cargo_display
        FROM contas c
        LEFT JOIN roles r ON c.id_cargo = r.id
    '''
    return _executar_select(query)

def get_conta_by_id(conta_id):
    query = '''
        SELECT 
            c.id, c.nome, c.email, c.id_cargo, c.senha,
            r.nome as cargo_display,
            c.id_cargo as cargo_id
        FROM contas c
        LEFT JOIN roles r ON c.id_cargo = r.id
        WHERE c.id = ?
    '''
    return _executar_select_um(query, (conta_id,))

def get_conta_by_email(email):
    query = 'SELECT * FROM contas WHERE email = ?'
    return _executar_select_um(query, (email,))

def get_contas_by_cargo(cargo_nome):
    query = '''
        SELECT c.id, c.nome, c.email, c.id_cargo FROM contas c
        JOIN roles r ON c.id_cargo = r.id
        WHERE LOWER(r.nome) = LOWER(?)
    '''
    return _executar_select(query, (cargo_nome,))

def add_conta(nome, email, id_cargo, senha='senha.123@2025'):    
    if get_conta_by_email(email):
        return {'ok': False, 'conta': None}
    
    query = '''
        INSERT INTO contas (nome, email, id_cargo, senha) 
        VALUES (?, ?, ?, ?)
    '''
    novo_id = _executar_query_com_id(query, (nome, email, id_cargo, senha))
    
    if novo_id:
        return {'ok': True, 'conta': get_conta_by_id(novo_id)}
    return {'ok': False, 'conta': None}

def update_conta(conta_id, nome, email, cargo_id=None, senha=None):
    if senha:
        query = '''
            UPDATE contas 
            SET nome = ?, email = ?, id_cargo = ?, senha = ? 
            WHERE id = ?
        '''
        sucesso = _executar_query(query, (nome, email, cargo_id, senha, conta_id))
    else:
        if cargo_id is not None:
            query = '''
                UPDATE contas 
                SET nome = ?, email = ?, id_cargo = ? 
                WHERE id = ?
            '''
            sucesso = _executar_query(query, (nome, email, cargo_id, conta_id))
        else:
            query = '''
                UPDATE contas 
                SET nome = ?, email = ? 
                WHERE id = ?
            '''
            sucesso = _executar_query(query, (nome, email, conta_id))
    
    if sucesso:
        return {'ok': True, 'conta': get_conta_by_id(conta_id)}
    return {'ok': False, 'conta': None}

def delete_conta(conta_id):
    conta = get_conta_by_id(conta_id)
    query = 'DELETE FROM contas WHERE id = ?'
    if _executar_query(query, (conta_id,)):
        return {'ok': True, 'conta': conta}
    return {'ok': False, 'conta': None}

def verify_login(email, senha):
    query = 'SELECT * FROM contas WHERE email = ? AND senha = ?'
    conta = _executar_select_um(query, (email, senha))
    if conta:
        return {'ok': True, 'conta': conta}
    return {'ok': False, 'conta': None}

def role_for_email(email):
    query = 'SELECT id_cargo FROM contas WHERE email = ?'
    conta = _executar_select_um(query, (email,))
    if conta:
        return conta['id_cargo']
    
    query = 'SELECT id_cargo FROM contas WHERE email = ? JOIN cargos ON contas.id_cargo = cargos.id'
    return _executar_select_um(query, (email,))

def register_email(nome, email, senha='senha.123@2025'):
    try:
        existente = get_conta_by_email(email)
        if existente:
            return {'ok': False, 'erro': 'Email já registado'}
        
        # Inserir nova conta
        query = 'INSERT INTO contas (nome, email, id_cargo, senha) VALUES (?, ?, ?, ?)'
        novo_id = _executar_query_com_id(query, (nome, email, '3', senha))
        
        if novo_id:
            return {
                'ok': True, 
                'conta': get_conta_by_id(novo_id)
            }
        return {'ok': False, 'erro': 'Erro ao registar conta'}
    except Exception as e:
        print(f"Erro ao registar email: {e}")
        return {'ok': False, 'erro': str(e)}
