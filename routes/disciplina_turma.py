from flask import Blueprint, request
from database.disciplina_turma import (
    get_disciplina_turmas, get_disciplina_turma_by_id,
    add_disciplina_turma, update_disciplina_turma, delete_disciplina_turma
)
from database.turma import get_turmas
from database.disciplina import get_disciplinas
from database.contas import get_contas_by_cargo
from database.exame import get_exames_by_disciplina_turma
from database.submissao_exame import get_submissoes_exame_by_exame_aluno
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, obter_aluno_id, get_request_data, erro_500, erro_html
from ui.disciplina_turma import (
    render_page_disciplina_turma,
    render_base_with_content,
    build_table_disciplina_turma,
    build_disciplina_turma_exames_content,
    build_modal_add_disciplina_turma,
    build_modal_edit_disciplina_turma,
    build_modal_delete_disciplina_turma,
    render_linha_disciplina_turma
)

disciplina_turma_route = Blueprint('disciplina_turma', __name__, url_prefix='/disciplina-turma')

@disciplina_turma_route.route('/')
def page_disciplina_turma():
    return render_page_disciplina_turma(table_disciplina_turma())

@disciplina_turma_route.route('/table')
def table_disciplina_turma():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        items = get_disciplina_turmas()
        
        return build_table_disciplina_turma(items)
        
    except Exception as e:
        return erro_500(e)

@disciplina_turma_route.route('/<int:dt_id>')
def view_disciplina_turma(dt_id):
    try:
        dt = get_disciplina_turma_by_id(dt_id)
        if not dt:
            content, status = erro_html('Disciplina-Turma não encontrada', 200)
            return render_base_with_content(content, status)
        
        cargo = obter_cargo_usuario()
        exames = get_exames_by_disciplina_turma(dt_id)

        aluno_id = obter_aluno_id() if cargo == Cargo.ALUNO else None
        if cargo == Cargo.ALUNO:
            exames = [e for e in exames if e.get('publico', False)]
        if cargo == Cargo.ALUNO and aluno_id:
            for exame in exames:
                submissao = get_submissoes_exame_by_exame_aluno(exame['id'], aluno_id)
                exame['ja_fez'] = submissao is not None
                exame['estado'] = submissao.get('estado') if submissao else None
                exame['finalizado'] = (submissao.get('estado') == 'finalizado') if submissao else False

        content = build_disciplina_turma_exames_content(
            dt,
            exames,
            cargo.value if cargo else None,
            aluno_id
        )
        return render_base_with_content(content, 200)
    except Exception as e:
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)

def modal_add():
    try:
        turmas = get_turmas()
        disciplinas = get_disciplinas()
        professores = get_contas_by_cargo('professor')
        
        return build_modal_add_disciplina_turma(turmas, disciplinas, professores)
        
    except Exception as e:
        return erro_500(e)

@disciplina_turma_route.route('/<int:item_id>/modal/edit')
def modal_edit(item_id):
    try:
        item = get_disciplina_turma_by_id(item_id)
        
        if not item:
            return erro_html('Registo não encontrado', 200)
        
        turmas = get_turmas()
        disciplinas = get_disciplinas()
        professores = get_contas_by_cargo('professor')
        
        return build_modal_edit_disciplina_turma(item, turmas, disciplinas, professores)
        
    except Exception as e:
        return erro_500(e)

@disciplina_turma_route.route('/<int:item_id>/modal/delete')
def modal_delete(item_id):
    try:
        item = get_disciplina_turma_by_id(item_id)
        
        if not item:
            return erro_html('Registo não encontrado', 200)
        
        return build_modal_delete_disciplina_turma(item)
        
    except Exception as e:
        return erro_500(e)

@disciplina_turma_route.route('/', methods=['POST'])
def criar():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = add_disciplina_turma(
            turma_id=int(dados.get('turma_id')),
            disciplina_id=int(dados.get('disciplina_id')),
            professor_id=int(dados.get('professor_id'))
        )
        
        if resultado['ok']:
            item = resultado['disciplina_turma']
            return render_linha_disciplina_turma(item)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@disciplina_turma_route.route('/<int:item_id>', methods=['PUT'])
def atualizar(item_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = update_disciplina_turma(
            disciplina_turma_id=item_id,
            turma_id=int(dados.get('turma_id')),
            disciplina_id=int(dados.get('disciplina_id')),
            professor_id=int(dados.get('professor_id'))
        )
        
        if resultado['ok']:
            item = resultado['disciplina_turma']
            return render_linha_disciplina_turma(item)
        
        return erro_html('Registo não encontrado', 200)
        
    except Exception as e:
        return erro_500(e)

@disciplina_turma_route.route('/<int:item_id>', methods=['DELETE'])
def deletar(item_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        resultado = delete_disciplina_turma(item_id)
        
        if resultado['ok']:
            return '', 200
        
        return erro_html('Registo não encontrado', 200)       
    except Exception as e:
        return erro_500(e)