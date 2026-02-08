from flask import Blueprint, request
from database.aluno import get_alunos, get_aluno_by_id, add_aluno, update_aluno, delete_aluno
from database.turma import get_turmas
from database.contas import get_contas
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.alunos import (
    render_page_alunos,
    build_table_alunos,
    build_modal_add_aluno,
    build_modal_edit_aluno,
    build_modal_delete_aluno,
    render_linha_aluno
)

alunos_route = Blueprint('alunos', __name__, url_prefix='/alunos')

@alunos_route.route('/')
def page_alunos():
    return render_page_alunos(table_alunos())

@alunos_route.route('/table')
def table_alunos():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        alunos = get_alunos()
        return build_table_alunos(alunos)
        
    except Exception as e:
        return erro_500(e)

@alunos_route.route('/modal/add')
def modal_add_aluno():
    try:
        turmas = get_turmas()
        contas = get_contas()
        return build_modal_add_aluno(turmas, contas)
        
    except Exception as e:
        return erro_500(e)

@alunos_route.route('/<int:aluno_id>/modal/edit')
def modal_edit_aluno(aluno_id):
    try:
        aluno = get_aluno_by_id(aluno_id)
        
        if not aluno:
            return erro_html('Aluno não encontrado', 200)
        
        turmas = get_turmas()
        contas = get_contas()
        return build_modal_edit_aluno(aluno, turmas, contas)
        
    except Exception as e:
        return erro_500(e)

@alunos_route.route('/<int:aluno_id>/modal/delete')
def modal_delete_aluno(aluno_id):
    try:
        aluno = get_aluno_by_id(aluno_id)
        
        if not aluno:
            return erro_html('Aluno não encontrado', 200)
        
        return build_modal_delete_aluno(aluno)
        
    except Exception as e:
        return erro_500(e)

@alunos_route.route('/', methods=['POST'])
def criar_aluno():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        if not dados:
            return erro_html('Conta é um campo obrigatório', 200)
        
        if not dados.get('turma_id'):
            return erro_html('Turma é um campo obrigatório', 200)
        
        conta_id = int(dados.get('conta_id'))
        turma_id = int(dados.get('turma_id'))
        
        # Gerar identificador automático se não fornecido
        identificador = dados.get('identificador', f'ALU-{conta_id:03d}')
        
        resultado = add_aluno(
            identificador=identificador,
            turma_id=turma_id,
            conta_id=conta_id
        )
        
        if resultado['ok']:
            aluno = resultado['aluno']
            turma_display = aluno.get('turma_display', '') or aluno.get('identificador', '') or '-'
            return render_linha_aluno(aluno, turma_display)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@alunos_route.route('/<int:aluno_id>', methods=['PUT'])
def atualizar_aluno(aluno_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        conta_id = int(dados.get('conta_id')) if dados.get('conta_id') else None
        turma_id = int(dados.get('turma_id')) if dados.get('turma_id') else None
        
        resultado = update_aluno(
            aluno_id=aluno_id,
            conta_id=conta_id,
            turma_id=turma_id
        )
        
        if resultado['ok']:
            aluno = resultado['aluno']
            turma = aluno.get('turma_display', '') or aluno.get('turma', '') or '-'
            return render_linha_aluno(aluno, turma)
        
        return erro_html('Aluno não encontrado', 200)
        
    except Exception as e:
        return erro_500(e)
