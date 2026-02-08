from flask import Blueprint, request
from database.contas import get_contas, get_conta_by_id, add_conta, update_conta, delete_conta
from database.roles import get_roles
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.contas import (
    render_page_contas,
    build_table_contas,
    build_modal_add_conta,
    build_modal_edit_conta,
    build_modal_delete_conta,
    render_linha_conta
)

contas_route = Blueprint('contas', __name__, url_prefix='/contas')

@contas_route.route('/')
def page_contas():
    return render_page_contas(table_contas())

@contas_route.route('/table')
def table_contas():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        contas = get_contas()
        return build_table_contas(contas)
        
    except Exception as e:
        return erro_500(e)

@contas_route.route('/modal/add')
def modal_add_conta():
    try:
        roles = get_roles()
        return build_modal_add_conta(roles)
        
    except Exception as e:
        return erro_500(e)

@contas_route.route('/<int:conta_id>/modal/edit')
def modal_edit_conta(conta_id):
    try:
        conta = get_conta_by_id(conta_id)
        
        if not conta:
            return erro_html('Conta não encontrada', 200)
        
        roles = get_roles()
        return build_modal_edit_conta(conta, roles)
        
    except Exception as e:
        return erro_500(e)

@contas_route.route('/<int:conta_id>/modal/delete')
def modal_delete_conta(conta_id):
    try:
        conta = get_conta_by_id(conta_id)
        
        if not conta:
            return erro_html('Conta não encontrada', 200)
        
        return build_modal_delete_conta(conta)
        
    except Exception as e:
        return erro_500(e)

@contas_route.route('/', methods=['POST'])
def criar_conta():
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = add_conta(
            nome=dados.get('nome'),
            email=dados.get('email'),
            id_cargo=int(dados.get('id_cargo')),
            senha=dados.get('senha')
        )
        
        if resultado['ok']:
            conta = resultado['conta']
            return render_linha_conta(conta)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@contas_route.route('/<int:conta_id>', methods=['PUT'])
def atualizar_conta(conta_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = update_conta(
            conta_id=conta_id,
            nome=dados.get('nome'),
            email=dados.get('email'),
            cargo_id=int(dados.get('id_cargo')),
            senha=dados.get('senha') if dados.get('senha') else None
        )
        
        if resultado['ok']:
            conta = resultado['conta']
            return render_linha_conta(conta)
        
        return erro_html('Conta não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)

@contas_route.route('/<int:conta_id>', methods=['DELETE'])
def deletar_conta(conta_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()

        resultado = delete_conta(conta_id)

        if resultado['ok']:
            return '', 200

        return erro_html('Conta não encontrada', 200)
    except Exception as e:
        return erro_500(e)
