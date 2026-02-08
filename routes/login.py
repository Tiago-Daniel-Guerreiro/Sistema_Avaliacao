from flask import Blueprint, request, jsonify, session, redirect, url_for
from database.contas import (verify_login, role_for_email, register_email)
from database.aluno import get_aluno_by_conta
import json
import os
import traceback
from ui.login import render_login_partial, render_login_page

login = Blueprint('login', __name__, url_prefix='/login')

@login.route('/')
def form_login():
    return render_login_page()

@login.route('/', methods=['POST'])
def api_login():
    try:        
        dados = request.get_json()
        email = dados.get('email')
        senha = dados.get('senha')
                
        # Primeiro tentar login normal (com dados da base de dados)
        resultado = verify_login(email, senha)
        if resultado['ok']:
            role = role_for_email(email)
            conta = resultado['conta']
            
            # Armazenar na sessão Flask (incluindo email e senha para validações posteriores)
            session['user_id'] = conta['id']
            session['email'] = email
            session['senha'] = senha  # Armazenar senha para verificações de sessão
            session['cargo'] = 'admin' if role == 1 else ('professor' if role == 2 else 'aluno')
            session['role'] = role
            session['logged_in'] = True
            
            response = {
                'ok': True,
                'user': email,
                'userId': conta['id'],
                'role': role
            }
            
            # Se for aluno (role 3), buscar aluno_id
            if role == 3:
                aluno = get_aluno_by_conta(conta['id'])
                if aluno:
                    response['alunoId'] = aluno['id']
                    session['aluno_id'] = aluno['id']
            
            return jsonify(response), 200
                
        # Se falhou, verificar se é código de acesso único de recovery_codes.json
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        recovery_codes_file = os.path.join(data_dir, 'recovery_codes.json')

        if os.path.exists(recovery_codes_file):
            try:
                with open(recovery_codes_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    recovery_codes = json.loads(content) if content else {'codes': {}}
                codes = recovery_codes.get('codes', {})
                if email in codes:
                    code_data = codes[email]
                    # Verifica se o código bate e se está expirado
                    if code_data['code'] == senha:
                        expires_at = code_data.get('expires_at')
                        from datetime import datetime
                        if expires_at and datetime.utcnow() > datetime.fromisoformat(expires_at):
                            return jsonify({'ok': False, 'erro': 'Código expirado'}), 401
                        # Se for one_time, remove após uso
                        if code_data.get('one_time'):
                            del codes[email]
                            with open(recovery_codes_file, 'w', encoding='utf-8') as f:
                                json.dump({'codes': codes}, f, indent=4)
                        # Preencher sessão Flask para acesso admin temporário
                        session['user_id'] = 0
                        session['email'] = email
                        session['senha'] = senha
                        session['cargo'] = 'admin'
                        session['role'] = 1
                        session['logged_in'] = True
                        return jsonify({
                            'ok': True,
                            'user': email,
                            'userId': 0,
                            'role': 1,
                            'conta': {
                                'id': 0,
                                'email': email,
                                'nome': 'Acesso Único',
                                'id_cargo': 1,
                                'temp_access': True
                            }
                        }), 200
            except json.JSONDecodeError:
                traceback.print_exc()
            except Exception:
                traceback.print_exc()
        return jsonify({'ok': False, 'erro': 'Credenciais inválidas'}), 401
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'erro': str(e)}), 500

@login.route('/necessario', methods=['GET'])
def verificar_login():
    try:
        # Verificar se tem sessão ativa
        if not session.get('logged_in'):
            return jsonify({'ok': False, 'erro': 'Não autenticado'}), 401
        
        # Validar credenciais armazenadas na sessão
        email = session.get('email')
        senha = session.get('senha')
        
        if not email or not senha:
            session.clear()
            return jsonify({'ok': False, 'erro': 'Sessão inválida'}), 401
        
        # Verificar se as credenciais ainda são válidas
        resultado = verify_login(email, senha)
        if not resultado['ok']:
            session.clear()
            return jsonify({'ok': False, 'erro': 'Credenciais de sessão inválidas'}), 401
        
        # Sessão válida
        return jsonify({
            'ok': True,
            'user_id': session.get('user_id'),
            'email': email,
            'role': session.get('role'),
            'cargo': session.get('cargo')
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'erro': str(e)}), 500

@login.route('/terminar_sessao', methods=['GET', 'POST'])
def terminar_sessao():
    try:
        session.clear()
        
        # Se for requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
            return jsonify({'ok': True, 'mensagem': 'Sessão terminada com sucesso'}), 200
        
        # Caso contrário, redirecionar para login
        return redirect(url_for('login.form_login'))
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'erro': str(e)}), 500