from flask import render_template

def render_page_gestao():
    return render_template('base.html', content=render_gestao_content(), initial_page='gestao')

def render_gestao_content():
    items = [
        {'titulo': 'Contas', 'url': '/contas/table'},
        {'titulo': 'Cargos', 'url': '/cargos/table'},
        {'titulo': 'Disciplinas', 'url': '/disciplinas/table'},
        {'titulo': 'Turmas', 'url': '/turmas/table'},
        {'titulo': 'Disciplinas por Turma', 'url': '/disciplina-turma/table'},
        {'titulo': 'Alunos', 'url': '/alunos/table'},
        {'titulo': 'Tipos de Questão', 'url': '/tipos-questao/table'},
        {'titulo': 'Questões', 'url': '/questoes/table'},
        {'titulo': 'Exames', 'url': '/exames/table'},
        {'titulo': 'Submissões', 'url': '/submissao/table'},
        {'titulo': 'Respostas', 'url': '/resposta/table'}
    ]

    return render_template('componentes/sidebar.html', items=items)
