from flask import render_template

def render_home_page(items=None):
    if items is None:
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
    content = render_home_cards(items)
    return render_template('base.html', content=content)

def render_home_cards(items):
    return render_template(
        'componentes/cards.html',
        titulo='Bem-vindo ao Sistema de Avaliação',
        items=items
    )

def render_cards_grid_items(items):
    return render_template('componentes/cards-grid.html', items=items)

def render_cards_grid_disciplinas(disciplinas):
    return render_template('componentes/cards-grid.html', disciplinas=disciplinas)

def render_cards_grid_turmas(turmas):
    return render_template('componentes/cards-grid.html', turmas=turmas)

def render_base_with_content(content, status=200):
    return render_template('base.html', content=content), status
