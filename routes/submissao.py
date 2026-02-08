from flask import Blueprint, request
import json
from database.submissao import (
    get_submissoes, get_submissao_by_id, add_submissao, 
    update_submissao, delete_submissao
)
from database.questao import get_questao_by_id
from database.aluno import get_aluno_by_id, get_alunos
from database.exame import get_exame_by_id, get_exames
from database.questao import get_questoes
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.submissao import (
    render_page_submissao,
    build_table_submissao,
    build_modal_add_submissao,
    build_modal_edit_submissao,
    build_modal_delete_submissao,
    render_linha_submissao
)

submissao_route = Blueprint('submissao', __name__, url_prefix='/submissao')

@submissao_route.route('/')
def page_submissao():
    return render_page_submissao(table_submissao())

@submissao_route.route('/table')
def table_submissao():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        submissoes = get_submissoes()
        
        return build_table_submissao(submissoes)
        
    except Exception as e:
        return erro_500(e)

@submissao_route.route('/modal/add')
def modal_add_submissao():
    try:
        exames = get_exames()
        alunos = get_alunos()
        questoes = get_questoes()
        
        return build_modal_add_submissao(exames, alunos, questoes)
        
    except Exception as e:
        return erro_500(e)

@submissao_route.route('/<int:submissao_id>/modal/edit')
def modal_edit_submissao(submissao_id):
    try:
        submissao = get_submissao_by_id(submissao_id)
        
        if not submissao:
            return erro_html('Submissão não encontrada', 200)
        
        exames = get_exames()
        alunos = get_alunos()
        questoes = get_questoes()
        
        return build_modal_edit_submissao(submissao, exames, alunos, questoes)
        
    except Exception as e:
        return erro_500(e)

@submissao_route.route('/<int:submissao_id>/modal/delete')
def modal_delete_submissao(submissao_id):
    try:
        submissao = get_submissao_by_id(submissao_id)
        
        if not submissao:
            return erro_html('Submissão não encontrada', 200)
        
        return build_modal_delete_submissao(submissao)
        
    except Exception as e:
        return erro_500(e)

@submissao_route.route('/', methods=['POST'])
def criar_submissao():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        
        if not dados or (not dados.get('exame_id') or not dados.get('aluno_id') or not dados.get('questao_id')):
            return erro_html('Exame, Aluno e Questão são campos obrigatórios', 200)
        
        resultado = add_submissao(
            exame_id=int(dados.get('exame_id')),
            aluno_id=int(dados.get('aluno_id')),
            questao_id=int(dados.get('questao_id')),
            resposta=dados.get('resposta', ''),
            data_hora_resposta='2026-02-05 09:00:00',  # Será preenchido pelo sistema
            pontuacao_atribuida=float(dados.get('pontuacao_atribuida', 0))
        )
        
        if resultado['ok']:
            submissao = resultado['submissao']
            
            return render_linha_submissao(submissao)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@submissao_route.route('/<int:submissao_id>', methods=['PUT'])
def atualizar_submissao(submissao_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        
        resultado = update_submissao(
            submissao_id=submissao_id,
            exame_id=int(dados.get('exame_id')),
            aluno_id=int(dados.get('aluno_id')),
            questao_id=int(dados.get('questao_id')),
            resposta=dados.get('resposta', ''),
            pontuacao_atribuida=float(dados.get('pontuacao_atribuida', 0))
        )
        
        if resultado['ok']:
            submissao = resultado['submissao']
            
            return render_linha_submissao(submissao)
        
        return erro_html('Submissão não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)

@submissao_route.route('/<int:submissao_id>', methods=['DELETE'])
def deletar_submissao(submissao_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        resultado = delete_submissao(submissao_id)
        
        if resultado['ok']:
            return '', 200
        
        return erro_html('Submissão não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)
