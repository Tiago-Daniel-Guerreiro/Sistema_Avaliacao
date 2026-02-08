from flask import Blueprint, request, jsonify
from database.contas import verify_login, role_for_email, register_email
from database.aluno import get_aluno_by_conta
from ui.register import render_register_partial, render_register_page

register = Blueprint('register', __name__, url_prefix='/register')

@register.route('/')
def form_register():
    return render_register_page()

@register.route('/', methods=['POST'])
def api_register():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')
        
        # Validar dados obrigatórios
        if not nome or not email or not senha:
            return jsonify({'ok': False, 'erro': 'Nome, email e senha são obrigatórios'}), 400
        
        resultado = register_email(nome, email, senha)
        if resultado['ok']:
            role = role_for_email(email)
            conta = resultado['conta']
            
            response = {
                'ok': True,
                'mensagem': 'Conta criada com sucesso!',
                'user': email,
                'userId': conta['id'],
                'role': role
            }
            
            # Se for aluno, buscar alunoId
            if role == 3:
                aluno = get_aluno_by_conta(conta['id'])
                if aluno:
                    response['alunoId'] = aluno['id']
            
            return jsonify(response), 201
        
        # Retornar erro específico
        erro = resultado.get('erro', 'Erro ao registar conta')
        return jsonify({'ok': False, 'erro': erro}), 400
        
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500
