from flask import Blueprint, request, session
from database.disciplina import get_disciplinas, get_disciplina_by_id, add_disciplina, update_disciplina, delete_disciplina
from database.aluno import get_aluno_by_conta
from database.disciplina_turma import get_disciplinas_by_turma
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.disciplinas import (
    render_page_disciplinas,
    build_table_disciplinas,
    build_modal_add_disciplina,
    build_modal_edit_disciplina,
    build_modal_delete_disciplina,
    render_linha_disciplina,
    render_cards_grid
)

disciplinas_route = Blueprint('disciplinas', __name__, url_prefix='/disciplinas')

@disciplinas_route.route('/')
def page_disciplinas():
    return render_page_disciplinas(table_disciplinas())

@disciplinas_route.route('/table')
def table_disciplinas():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        disciplinas = get_disciplinas()
        return build_table_disciplinas(disciplinas)
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/modal/add')
def modal_add_disciplina():
    try:
        return build_modal_add_disciplina()
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/<int:disciplina_id>/modal/edit')
def modal_edit_disciplina(disciplina_id):
    try:
        disciplina = get_disciplina_by_id(disciplina_id)
        
        if not disciplina:
            return erro_html('Disciplina não encontrada', 200)
        
        return build_modal_edit_disciplina(disciplina)
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/<int:disciplina_id>/modal/delete')
def modal_delete_disciplina(disciplina_id):
    try:
        disciplina = get_disciplina_by_id(disciplina_id)
        
        if not disciplina:
            return erro_html('Disciplina não encontrada', 200)
        
        return build_modal_delete_disciplina(disciplina)
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/', methods=['POST'])
def criar_disciplina():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = add_disciplina(
            nome=dados.get('nome'),
            codigo=dados.get('codigo')
        )
        
        if resultado['ok']:
            disciplina = resultado['disciplina']
            return render_linha_disciplina(disciplina)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/<int:disciplina_id>', methods=['PUT'])
def atualizar_disciplina(disciplina_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = update_disciplina(
            disciplina_id=disciplina_id,
            nome=dados.get('nome'),
            codigo=dados.get('codigo')
        )
        
        if resultado['ok']:
            disciplina = resultado['disciplina']
            return render_linha_disciplina(disciplina)
        
        return erro_html('Disciplina não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/<int:disciplina_id>', methods=['DELETE'])
def deletar_disciplina(disciplina_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        resultado = delete_disciplina(disciplina_id)
        
        if resultado['ok']:
            return '', 200
        
        return erro_html('Disciplina não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)

@disciplinas_route.route('/cards')
def disciplinas_cards():
    try:
        conta_id = session.get('user_id')
        if not conta_id:
            return '<div class="col-12"><p class="text-warning">Faça login para ver suas disciplinas</p></div>'
        
        aluno = get_aluno_by_conta(conta_id)
        if not aluno or not aluno.get('turma_id'):
            return '<div class="col-12"><p class="text-muted">Nenhuma turma atribuída</p></div>'
        
        disciplinas_turma = get_disciplinas_by_turma(aluno['turma_id'])
        if not disciplinas_turma:
            return '<div class="col-12"><p class="text-muted">Nenhuma disciplina disponível</p></div>'
        
        items = [{
            'title': dt.get('disciplina_nome', 'Sem nome'),
            'subtitle': dt.get('disciplina_codigo', 'Sem código'),
            'button_text': 'Ver Exames',
            'link': f"/disciplina-turma/{dt['id']}"
        } for dt in disciplinas_turma]
        
        return render_cards_grid(items, clickable=True, subtitle_size='small')
    except Exception as e:
        content, status = erro_html(f'Erro ao carregar disciplinas: {str(e)}', 500)
        return f'<div class="col-12">{content}</div>', status

@disciplinas_route.route('/turma/<int:turma_id>/cards')
def turma_disciplinas_cards(turma_id):
    try:
        disciplinas = get_disciplinas_by_turma(turma_id)
        
        if not disciplinas:
            return '<div class="col-12"><p class="text-muted">Nenhuma disciplina atribuída a essa turma</p></div>'
        
        items = [{
            'title': disc.get('disciplina_nome', 'Sem nome'),
            'subtitle': disc.get('disciplina_codigo', ''),
            'button_text': 'Gerir',
            'link': f"/disciplina-turma/{disc['id']}"
        } for disc in disciplinas]
        
        return render_cards_grid(items, clickable=True)
    except Exception as e:
        content, status = erro_html(f'Erro ao carregar disciplinas: {str(e)}', 500)
        return f'<div class="col-12">{content}</div>', status