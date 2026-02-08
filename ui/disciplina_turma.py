from datetime import datetime
from flask import render_template
from markupsafe import Markup
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_disciplina_turma(tabela_html):
    return render_template('base.html', content=tabela_html)

def render_base_with_content(content, status=200):
    return render_template('base.html', content=content), status

def build_table_disciplina_turma(items):
    tabela = (TableBuilder(titulo='Disciplinas por Turma')
        .set_header(['Turma - Disciplina', 'Professor'], acoes=True)
        .set_table_id('tabela-disciplina-turma')
        .set_botao_adicionar('/disciplina-turma/modal/add', 'Nova Associação')
    )

    for item in items:
        turma = item.get('turma_display', item.get('turma', ''))
        codigo = item.get('disciplina_codigo', item.get('codigo', ''))
        coluna1 = f"{turma} - {codigo}"

        tabela.add_linha(
            coluna1,
            item.get('professor_nome', ''),
            row_id=f"disciplina-turma-{item['id']}",
            botoes=TableBuilder.botoes_crud('/disciplina-turma', item['id'])
        )

    return tabela.build()

def build_disciplina_turma_exames_content(dt, exames, cargo, aluno_id):
    disciplina_nome = dt.get('disciplina_nome', 'Disciplina')
    turma_display = dt.get('turma_display', 'Turma')

    tabela = (TableBuilder(titulo=f'{disciplina_nome} - {turma_display}')
        .set_header(['Título', 'Data/Hora Início', 'Público' if cargo == 'professor' else 'Finalizado'], acoes=True)
    )

    if cargo == 'professor':
        tabela.set_botao_adicionar(f'/exames/modal/add?disciplina_turma_id={dt["id"]}', 'Adicionar Exame')

    now = datetime.now()
    for exame in exames:
        titulo = exame.get('titulo', 'Sem título')
        data_inicio_str = exame.get('data_hora_inicio', '')

        try:
            data_inicio = datetime.fromisoformat(data_inicio_str) if data_inicio_str else None
            data_formatada = data_inicio.strftime('%d/%m/%Y %H:%M') if data_inicio else '-'
            pode_fazer = data_inicio <= now if data_inicio else False
        except Exception:
            data_formatada = '-'
            pode_fazer = False

        finalizado = 'Sim' if exame.get('finalizado', False) or exame.get('estado') == 'finalizado' else 'Não'
        publico = 'Sim' if exame.get('publico', False) else 'Não'
        exame_id = exame['id']

        botoes = []
        if cargo == 'professor':
            botoes = [Markup(f'<a href="/exame/{exame_id}/" class="btn btn-primary btn-sm">Editar</a>')]
        elif cargo == 'aluno' and aluno_id:
            if exame.get('ja_fez'):
                botoes = [Markup(f'<a href="/exame/{exame_id}/" class="btn btn-secondary btn-sm">Visualizar</a>')]
            elif pode_fazer:
                botoes = [Markup(f'<a href="/exame/{exame_id}/start" class="btn btn-success btn-sm">Iniciar</a>')]
            else:
                botoes = [Markup('<span class="badge bg-warning text-dark">Em breve</span>')]

        tabela.add_linha(
            titulo,
            data_formatada,
            publico if cargo == 'professor' else finalizado,
            row_id=f"exame-{exame_id}",
            botoes=botoes
        )

    if not exames:
        return f'''
        <div class="container py-4">
            <h1>{disciplina_nome} - {turma_display}</h1>
            <div class="alert alert-info mt-3">Nenhum exame disponível</div>
        </div>
        '''

    return tabela.build()

def build_modal_add_disciplina_turma(turmas, disciplinas, professores):
    turma_opts = [(t['id'], t.get('turma_display', f"{t['ano']}º {t['identificador']}")) for t in turmas]
    disc_opts = [(d['id'], f"{d['nome']} ({d['codigo']})") for d in disciplinas]
    prof_opts = [(p['id'], p['nome']) for p in professores]

    form = (FormBuilder.criar('/disciplina-turma/', '#tabela-disciplina-turma tbody')
        .add_select('turma_id', 'Turma', options=turma_opts, required=True)
        .add_select('disciplina_id', 'Disciplina', options=disc_opts, required=True)
        .add_select('professor_id', 'Professor', options=prof_opts, required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Disciplina à Turma')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_disciplina_turma(item, turmas, disciplinas, professores):
    turma_opts = [(t['id'], t.get('turma_display', f"{t['ano']}º {t['identificador']}")) for t in turmas]
    disc_opts = [(d['id'], f"{d['nome']} ({d['codigo']})") for d in disciplinas]
    prof_opts = [(p['id'], p['nome']) for p in professores]

    form = (FormBuilder.editar('/disciplina-turma', item['id'], f"#disciplina-turma-{item['id']}")
        .add_select('turma_id', 'Turma', value=item.get('turma_id', ''), options=turma_opts, required=True)
        .add_select('disciplina_id', 'Disciplina', value=item.get('disciplina_id', ''), options=disc_opts, required=True)
        .add_select('professor_id', 'Professor', value=item.get('professor_id', ''), options=prof_opts, required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Editar Disciplina-Turma')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_disciplina_turma(item):
    form = FormBuilder.deletar('/disciplina-turma', item['id'], f"#disciplina-turma-{item['id']}")

    turma = item.get('turma_display', item.get('turma', ''))
    codigo = item.get('disciplina_codigo', item.get('codigo', ''))
    display_text = f"{turma} - {codigo}"

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(f'''
            <p class="alert alert-danger">
                Tem certeza que deseja remover a associação <strong>{display_text}</strong>?
            </p>
        ''')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_disciplina_turma(item):
    turma = item.get('turma_display', item.get('turma', ''))
    codigo = item.get('disciplina_codigo', item.get('codigo', ''))
    coluna1 = f"{turma} - {codigo}"

    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"disciplina-turma-{item['id']}",
            'colunas': [coluna1, item.get('professor_nome', '')],
            'botoes': TableBuilder.botoes_crud('/disciplina-turma', item['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
