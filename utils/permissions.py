from functools import wraps
from flask import session, abort, jsonify, Blueprint, request, redirect, url_for, render_template
from enum import Enum

class Cargo(Enum):
    ALUNO = 'aluno'
    PROFESSOR = 'professor'
    ADMIN = 'admin'

def obter_cargo_usuario():
    if 'user_id' not in session or 'cargo' not in session:
        return None
    
    cargo_str = session.get('cargo', '').lower()
    try:
        return Cargo[cargo_str.upper()]
    except KeyError:
        return None
    
def obter_id_usuario():
    return session.get('user_id')

def obter_aluno_id():
    aluno_id = session.get('aluno_id')
    if aluno_id:
        return aluno_id

    conta_id = session.get('user_id')
    if not conta_id:
        return None

    try:
        from database.aluno import get_aluno_by_conta
        aluno = get_aluno_by_conta(conta_id)
        if aluno:
            session['aluno_id'] = aluno.get('id')
            return aluno.get('id')
    except Exception:
        return None

    return None

def obter_div_acesso_negado():
    def criar_conteudo():
        return '<div class="alert alert-danger">Acesso negado</div>'
    
    if request.headers.get('X-Partial') == '1':
        return criar_conteudo()
    
    return render_template('base.html', content=criar_conteudo())

def get_request_data():
    if request.method in ['PUT', 'DELETE'] or request.is_json:
        return request.get_json(force=True, silent=True) or {}
    return request.form.to_dict()

def erro_html(mensagem, status=500):
    return render_template('componentes/alert.html', type='danger', text=mensagem), status

def erro_500(e):
    return erro_html(f'Erro: {str(e)}', 500)

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'logged_in' not in session:
            if request.headers.get('X-Partial') == '1':
                return jsonify({'ok': False, 'erro': 'Não autenticado'}), 401
            return redirect(url_for('login.form_login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cargo = obter_cargo_usuario()
            
            if cargo is None:
                if request.headers.get('X-Partial') == '1':
                    return jsonify({'ok': False, 'erro': 'Não autenticado'}), 401
                return redirect(url_for('login.form_login'))
            
            if cargo not in allowed_roles:
                if request.headers.get('X-Partial') == '1':
                    return obter_div_acesso_negado(), 403
                return obter_div_acesso_negado(), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

permissions_route = Blueprint('permissions', __name__)

@permissions_route.errorhandler(400)
def bad_request(e):
    return jsonify({'ok': False, 'erro': 'Pedido inválido'}), 400

@permissions_route.errorhandler(401)
def unauthorized(e):
    return jsonify({'ok': False, 'erro': 'Não autorizado'}), 401

@permissions_route.errorhandler(403)
def forbidden(e):
    return jsonify({'ok': False, 'erro': 'Acesso proibido'}), 403

@permissions_route.errorhandler(404)
def not_found(e):
    return jsonify({'ok': False, 'erro': 'Recurso não encontrado'}), 404
@permissions_route.errorhandler(500)
def internal_error(e):
    print(f'Erro interno: {e}')
    return jsonify({'ok': False, 'erro': 'Erro interno do servidor'}), 500

@permissions_route.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return '', 204

@permissions_route.route('/sessao')
def api_sessao():
    if 'user_id' not in session or 'logged_in' not in session:
        return jsonify({
            'autenticado': False,
            'ok': False
        }), 401
    
    return jsonify({
        'autenticado': True,
        'ok': True,
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'cargo': session.get('cargo'),
        'role': session.get('role')
    }), 200
