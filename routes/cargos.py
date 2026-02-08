from flask import Blueprint
from database.roles import get_roles, get_role_by_id, add_role, update_role, delete_role
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.cargos import (
    render_page_cargos,
    ui_table_cargos,
    ui_modal_add_cargo,
    ui_modal_edit_cargo,
    ui_modal_delete_cargo,
    ui_row_cargo,
)

cargos_route = Blueprint('cargos', __name__, url_prefix='/cargos')

@cargos_route.route('/')
def page_cargos():
    return render_page_cargos(table_cargos())

@cargos_route.route('/table')
def table_cargos():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        cargos = get_roles()
        return ui_table_cargos(cargos)
        
    except Exception as e:
        return erro_500(e)

@cargos_route.route('/modal/add')
def modal_add_cargo():
    try:
        return ui_modal_add_cargo()
        
    except Exception as e:
        return erro_500(e)

@cargos_route.route('/<int:cargo_id>/modal/edit')
def modal_edit_cargo(cargo_id):
    try:
        cargo = get_role_by_id(cargo_id)
        
        if not cargo:
            return erro_html('Cargo não encontrado', 200)

        return ui_modal_edit_cargo(cargo)
        
    except Exception as e:
        return erro_500(e)

@cargos_route.route('/<int:cargo_id>/modal/delete')
def modal_delete_cargo(cargo_id):
    try:
        cargo = get_role_by_id(cargo_id)
        
        if not cargo:
            return erro_html('Cargo não encontrado', 200)

        return ui_modal_delete_cargo(cargo)
        
    except Exception as e:
        return erro_500(e)

@cargos_route.route('/', methods=['POST'])
def criar_cargo():
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = add_role(nome=dados.get('nome'))
        
        if resultado['ok']:
            cargo = resultado['role']
            return ui_row_cargo(cargo)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@cargos_route.route('/<int:cargo_id>', methods=['PUT'])
def atualizar_cargo(cargo_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = update_role(role_id=cargo_id, nome=dados.get('nome'))
        
        if resultado['ok']:
            cargo = resultado['role']
            return ui_row_cargo(cargo)
        
        return erro_html('Cargo não encontrado', 200)
        
    except Exception as e:
        return erro_500(e)

@cargos_route.route('/<int:cargo_id>', methods=['DELETE'])
def deletar_cargo(cargo_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()

        resultado = delete_role(cargo_id)

        if resultado['ok']:
            return '', 200

        return erro_html('Cargo não encontrado', 200)
    except Exception as e:
        return erro_500(e)
