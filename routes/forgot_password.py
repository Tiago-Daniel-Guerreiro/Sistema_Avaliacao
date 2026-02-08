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
        
        # Lógica simplificada para demonstração
        if cargo_id == '3':  # Aluno
            if not conta:
                return jsonify({
                    'ok': False, 
                    'action': 'register',
                    'message': 'Conta não existe. Deseja registar-se? Depois poderá pedir para que a conta seja associada à devida turma.'
                }), 404
            return jsonify({
                'ok': True,
                'message': 'Entre em contato com o professor para recuperar acesso.'
            }), 200
        
        elif cargo_id == '2':  # Professor
            return jsonify({
                'ok': True,
                'message': 'Entre em contato com a equipa técnica para recuperar acesso.'
            }), 200
        
        else:  # Administrador
            if not conta:
                return jsonify({'ok': False, 'erro': 'Conta não encontrada'}), 404
            
            # Gerar código de recuperação
            code = secrets.token_hex(16)
            return jsonify({
                'ok': True,
                'message': f'Código de recuperação gerado (simulado): {code}'
            }), 200
            
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500
