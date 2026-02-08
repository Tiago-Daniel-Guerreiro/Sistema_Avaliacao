from flask import Blueprint, request, jsonify
from utils.permissions import require_role, require_login, obter_cargo_usuario, obter_id_usuario, obter_aluno_id, Cargo, erro_500, erro_html
from database.disciplina_turma import get_turmas_by_professor, get_disciplinas_by_aluno
from database.aluno import get_aluno_by_conta
from ui.home import (
    render_home_page,
    render_home_cards,
    render_cards_grid_items,
    render_cards_grid_disciplinas,
    render_cards_grid_turmas,
    render_base_with_content
)

home_route = Blueprint('home', __name__)

@home_route.route('/')
def home():
    items = [
        {
            'titulo': 'Aluno',
            'descricao': 'Visualize suas disciplinas e realize as avaliações.',
            'href': '/alunos'
        },
        {
            'titulo': 'Professor',
            'descricao': 'Gerencie suas turmas e disciplinas.',
            'href': '/professores'
        },
        {
            'titulo': 'Administrador',
            'descricao': 'Gerencie usuários e sistema.',
            'href': '/gestao'
        }
    ]
    return render_home_page(items)

@home_route.route('/home')
def home_content():
    items = [
        {
            'titulo': 'Aluno',
            'descricao': 'Visualize suas disciplinas e realize as avaliações.',
            'href': '/alunos'
        },
        {
            'titulo': 'Professor',
            'descricao': 'Gerencie suas turmas e disciplinas.',
            'href': '/professores'
        },
        {
            'titulo': 'Administrador',
            'descricao': 'Gerencie usuários e sistema.',
            'href': '/gestao'
        }
    ]
    return render_home_cards(items)

@home_route.route('/alunos')
@require_role(Cargo.ALUNO)
def alunos_content():
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            conta_id = obter_id_usuario()
            aluno = get_aluno_by_conta(conta_id)
            if not aluno:
                content = '<div class="alert alert-warning">Aluno não encontrado</div>'
                return render_base_with_content(content, 200)
            aluno_id = aluno['id']
            turma_id = aluno.get('turma_id')
        else:
            aluno = get_aluno_by_conta(obter_id_usuario())
            turma_id = aluno.get('turma_id') if aluno else None
        
        if not turma_id:
            content = '<div class="alert alert-warning">Turma não identificada</div>'
            return render_base_with_content(content, 200)
        
        disciplinas = get_disciplinas_by_aluno(turma_id)
        content = render_cards_grid_items(disciplinas)
        return render_base_with_content(content, 200)
        
    except Exception as e:
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)

@home_route.route('/componentes/disciplinas-aluno')
@require_role(Cargo.ALUNO)
def disciplinas_aluno():
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            conta_id = obter_id_usuario()
            aluno = get_aluno_by_conta(conta_id)
            if not aluno:
                return '<div class="alert alert-warning">Aluno não encontrado</div>'
            aluno_id = aluno['id']
            turma_id = aluno.get('turma_id')
        else:
            aluno = get_aluno_by_conta(obter_id_usuario())
            turma_id = aluno.get('turma_id') if aluno else None
        
        if not turma_id:
            return '<div class="alert alert-warning">Turma não identificada</div>'
        
        disciplinas = get_disciplinas_by_aluno(turma_id)
        return render_cards_grid_disciplinas(disciplinas)
        
    except Exception as e:
        return erro_500(e)

@home_route.route('/disciplinas/turma/<int:turma_id>/cards')
@require_role(Cargo.PROFESSOR)
def disciplinas_turma_cards(turma_id):
    try:
        disciplinas = get_disciplinas_by_aluno(turma_id)
        return render_cards_grid_disciplinas(disciplinas)
    except Exception as e:
        return erro_500(e)

@home_route.route('/professores')
@require_role(Cargo.PROFESSOR)
def professores_content():
    try:
        professor_id = obter_id_usuario()
        turmas = get_turmas_by_professor(professor_id)
        
        if not turmas:
            content = '<div class="container py-5"><p class="text-muted text-center">Nenhuma turma atribuída</p></div>'
            return render_base_with_content(content, 200)
        
        content = render_cards_grid_items(turmas)
        return render_base_with_content(content, 200)
        
    except Exception as e:
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)

@home_route.route('/turmas/cards')
@require_role(Cargo.PROFESSOR)
def turmas_cards_professor():
    try:
        professor_id = obter_id_usuario()
        turmas = get_turmas_by_professor(professor_id)
        
        if not turmas:
            return '<div class="alert alert-info">Nenhuma turma atribuída</div>'
        
        return render_cards_grid_turmas(turmas)
        
    except Exception as e:
        return erro_500(e)
