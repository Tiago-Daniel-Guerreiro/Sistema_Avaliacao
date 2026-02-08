from flask import Blueprint, request
from database.tipos_questao import get_tipos_questao, get_tipo_questao_by_id, add_tipo_questao, update_tipo_questao, delete_tipo_questao
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from database.geral import _validar_integridade_respostas, _limpar_resposta_incompativel, _get_connection
from ui.tipos_questao import (
    render_page_tipos_questao,
    build_table_tipos_questao,
    build_modal_add_tipo_questao,
    build_modal_edit_tipo_questao,
    build_modal_delete_tipo_questao,
    render_linha_tipo_questao
)

tipos_questao_route = Blueprint('tipos_questao', __name__, url_prefix='/tipos-questao')

@tipos_questao_route.route('/')
def page_tipos_questao():
    return render_page_tipos_questao(table_tipos_questao())

@tipos_questao_route.route('/table')
def table_tipos_questao():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        tipos = get_tipos_questao()
        
        return build_table_tipos_questao(tipos)
        
    except Exception as e:
        return erro_500(e)

@tipos_questao_route.route('/modal/add')
def modal_add_tipo_questao():
    try:
        return build_modal_add_tipo_questao()
        
    except Exception as e:
        return erro_500(e)

@tipos_questao_route.route('/<int:tipo_id>/modal/edit')
def modal_edit_tipo_questao(tipo_id):
    try:
        tipo = get_tipo_questao_by_id(tipo_id)
        
        if not tipo:
            return erro_html('Tipo de questão não encontrado', 200)
        
        return build_modal_edit_tipo_questao(tipo)
        
    except Exception as e:
        return erro_500(e)

@tipos_questao_route.route('/<int:tipo_id>/modal/delete')
def modal_delete_tipo_questao(tipo_id):
    try:
        tipo = get_tipo_questao_by_id(tipo_id)
        
        if not tipo:
            return erro_html('Tipo de questão não encontrado', 200)
        
        return build_modal_delete_tipo_questao(tipo)
        
    except Exception as e:
        return erro_500(e)

@tipos_questao_route.route('/', methods=['POST'])
def criar_tipo_questao():
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        input_file = dados.get('input_file') or dados.get('file_name') or dados.get('file_namme')
        resultado = add_tipo_questao(
            input_file=input_file,
            nome=dados.get('nome'),
            list_options=dados.get('list_options', False),
            correcao_automatica=dados.get('correcao_automatica', True)
        )
        
        if resultado['ok']:
            conn = _get_connection()
            cursor = conn.cursor()
            _validar_integridade_respostas(cursor)
            conn.commit()
            conn.close()

            tipo = resultado['tipo_questao']
            return render_linha_tipo_questao(tipo)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@tipos_questao_route.route('/<int:tipo_id>', methods=['PUT'])
def atualizar_tipo_questao(tipo_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        input_file = dados.get('input_file') or dados.get('file_name') or dados.get('file_namme')
        resultado = update_tipo_questao(
            tipo_id=tipo_id,
            input_file=input_file,
            nome=dados.get('nome'),
            list_options=dados.get('list_options', False),
            correcao_automatica=dados.get('correcao_automatica', True)
        )
        
        if resultado['ok']:
            conn = _get_connection()
            cursor = conn.cursor()
            _validar_integridade_respostas(cursor)
            conn.commit()
            conn.close()

            tipo = resultado['tipo_questao']
            return render_linha_tipo_questao(tipo)
        
        return erro_html('Tipo de questão não encontrado', 200)
        
    except Exception as e:
        return erro_500(e)

@tipos_questao_route.route('/<int:tipo_id>', methods=['DELETE'])
def deletar_tipo_questao(tipo_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        resultado = delete_tipo_questao(tipo_id)
        
        if resultado['ok']:
            conn = _get_connection()
            cursor = conn.cursor()
            _validar_integridade_respostas(cursor)
            conn.commit()
            conn.close()
            return '', 200
        
        return erro_html('Tipo de questão não encontrado', 200)       
    except Exception as e:
        return erro_500(e)