from flask import Blueprint, request, jsonify
from database.turma import get_turmas, get_turma_by_id, add_turma, update_turma, delete_turma
from database.disciplina_turma import get_disciplina_turmas
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.turmas import (
    render_page_turmas,
    render_base_with_content,
    build_table_turmas,
    build_turma_view_content,
    render_cards_turmas,
    build_modal_add_turma,
    build_modal_edit_turma,
    build_modal_delete_turma,
    render_linha_turma
)

turmas_route = Blueprint('turmas', __name__, url_prefix='/turmas')

@turmas_route.route('/')
def page_turmas():
    return render_page_turmas(table_turmas())

@turmas_route.route('/table')
def table_turmas():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        elif cargo == Cargo.PROFESSOR:
            return cards_turmas()
        
        turmas = get_turmas()
        
        return build_table_turmas(turmas)
        
    except Exception as e:
        return erro_500(e)

@turmas_route.route('/<int:turma_id>')
def view_turma(turma_id):
    try:
        turma = get_turma_by_id(turma_id)
        if not turma:
            content, status = erro_html('Turma não encontrada', 200)
            return render_base_with_content(content, status)
        
        todas_disciplinas_turma = get_disciplina_turmas()
        disciplinas_turma = [dt for dt in todas_disciplinas_turma if dt.get('turma_id') == turma_id]
        
        content = build_turma_view_content(turma, disciplinas_turma)
        return render_base_with_content(content, 200)
    except Exception as e:
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)



@turmas_route.route('/cards')
def cards_turmas():
    turmas = get_turmas()
    return render_cards_turmas(turmas)

@turmas_route.route('/cards')
def get_turmas_cards():
    return cards_turmas()

@turmas_route.route('/modal/add')
def modal_add_turma():
    try:
        return build_modal_add_turma()
        
    except Exception as e:
        return erro_500(e)


@turmas_route.route('/<int:turma_id>/modal/edit')
def modal_edit_turma(turma_id):
    try:
        turma = get_turma_by_id(turma_id)
        
        if not turma:
            return erro_html('Turma não encontrada', 200)
        
        return build_modal_edit_turma(turma)
        
    except Exception as e:
        return erro_500(e)


@turmas_route.route('/<int:turma_id>/modal/delete')
def modal_delete_turma(turma_id):
    try:
        turma = get_turma_by_id(turma_id)
        
        if not turma:
            return erro_html('Turma não encontrada', 200)
        
        return build_modal_delete_turma(turma)
        
    except Exception as e:
        return erro_500(e)

@turmas_route.route('/', methods=['POST'])
def criar_turma():
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = add_turma(
            ano=int(dados.get('ano')),
            identificador=dados.get('identificador')
        )
        
        if resultado['ok']:
            turma = resultado['turma']
            return render_linha_turma(turma)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@turmas_route.route('/<int:turma_id>', methods=['PUT'])
def atualizar_turma(turma_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = update_turma(
            turma_id=turma_id,
            ano=int(dados.get('ano')),
            identificador=dados.get('identificador')
        )
        
        if resultado['ok']:
            turma = resultado['turma']
            return render_linha_turma(turma)
        
        return erro_html('Turma não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)

@turmas_route.route('/<int:turma_id>', methods=['DELETE'])
def deletar_turma(turma_id):
    try:
        if obter_cargo_usuario() != Cargo.ADMIN:
            return obter_div_acesso_negado()
        
        resultado = delete_turma(turma_id)
        
        if resultado['ok']:
            return '', 200
        
        return erro_html('Turma não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)