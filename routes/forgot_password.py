from flask import Blueprint, request, jsonify
from database.contas import get_conta_by_email, update_conta, add_conta
import secrets
import json
import os
from datetime import datetime, timedelta
from ui.forgot_password import render_forgot_password_partial, render_forgot_password_page

forgot_password_route = Blueprint('forgot_password', __name__, url_prefix='/forgot-password')

@forgot_password_route.route('/')
def form_forgot_password():
    return render_forgot_password_page()

@forgot_password_route.route('/', methods=['POST'])
def forgot_password():
    try:
        dados = request.get_json(force=True, silent=True) or {}
        email = dados.get('email')
        cargo_id = dados.get('cargo_id')
        
        if not email or not cargo_id:
            return jsonify({'ok': False, 'erro': 'Email e cargo são obrigatórios'}), 400
        
        conta = get_conta_by_email(email)

        if conta:
            conta_cargo_id = str(conta.get('id_cargo') or conta.get('cargo_id'))
            if conta_cargo_id != str(cargo_id):
                return jsonify({
                    'ok': False,
                    'erro': 'Conta encontrada, mas o tipo de conta selecionado não corresponde ao cadastrado.'
                }), 400

            # Se for aluno
            if cargo_id == '3':
                return jsonify({
                    'ok': True,
                    'message': 'Entre em contato com o professor para recuperar acesso.'
                }), 200
            # Se for professor
            elif cargo_id == '2':
                return jsonify({
                    'ok': True,
                    'message': 'Entre em contato com a equipa técnica para recuperar acesso.'
                }), 200
            # Se for admin existente
            else:
                # Gerar código de recuperação
                code = secrets.token_hex(16)
                expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
                recovery_data = {
                    'email': email,
                    'code': code,
                    'expires_at': expires_at
                }
                codes_path = os.path.join(os.path.dirname(__file__), '../data/recovery_codes.json')
                codes_path = os.path.abspath(codes_path)
                try:
                    with open(codes_path, 'r', encoding='utf-8') as f:
                        codes_json = json.load(f)
                except Exception:
                    codes_json = {"codes": {}}
                codes_json["codes"][email] = recovery_data
                with open(codes_path, 'w', encoding='utf-8') as f:
                    json.dump(codes_json, f, indent=4)
                return jsonify({
                    'ok': True,
                    'message': 'Código de recuperação gerado e armazenado no servidor. Solicite à equipa técnica para obter o código.'
                }), 200
        else:
            # Conta não existe
            if str(cargo_id) == '1':  # Admin
                # Permitir criar código de acesso único para login
                code = secrets.token_hex(16)
                expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
                recovery_data = {
                    'email': email,
                    'code': code,
                    'expires_at': expires_at,
                    'one_time': True
                }
                codes_path = os.path.join(os.path.dirname(__file__), '../data/recovery_codes.json')
                codes_path = os.path.abspath(codes_path)
                try:
                    with open(codes_path, 'r', encoding='utf-8') as f:
                        codes_json = json.load(f)
                except Exception:
                    codes_json = {"codes": {}}
                codes_json["codes"][email] = recovery_data
                with open(codes_path, 'w', encoding='utf-8') as f:
                    json.dump(codes_json, f, indent=4)
                return jsonify({
                    'ok': True,
                    'message': 'Código de acesso único gerado para administrador inexistente. Solicite à equipa técnica para obter o código.'
                }), 200
            else:
                return jsonify({
                    'ok': False,
                    'action': 'register',
                    'message': 'Conta não existe. Deseja registar-se? Depois poderá pedir para que a conta seja associada à devida turma.'
                }), 404
            
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500
