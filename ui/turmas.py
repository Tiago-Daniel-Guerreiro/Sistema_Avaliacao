from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_turmas(tabela_html):
    return render_template('base.html', content=tabela_html)

def render_base_with_content(content, status=200):
    return render_template('base.html', content=content), status

def build_table_turmas(turmas):
    tabela = (TableBuilder(titulo='Lista de Turmas')
        .set_header(['Ano', 'Identificador'], acoes=True)
        .set_table_id('tabela-turmas')
        .set_botao_adicionar('/turmas/modal/add', 'Nova Turma')
    )

    for turma in turmas:
        tabela.add_linha(
            turma.get('ano', ''),
            turma.get('identificador', ''),
            row_id=f"turma-{turma['id']}",
            botoes=TableBuilder.botoes_crud('/turmas', turma['id'])
        )

    return tabela.build()

def build_turma_view_content(turma, disciplinas_turma):
    turma_display = turma.get('turma_display', 'Turma')

    items = []
    for dt in disciplinas_turma:
        items.append({
            'disciplina_nome': dt.get('disciplina_nome', 'Disciplina'),
            'professor_nome': dt.get('professor_nome', 'N/A'),
            'link': f'/disciplina-turma/{dt["id"]}',
            'description': None
        })

    if not disciplinas_turma:
        return render_template(
            'componentes/cards-grid.html',
            titulo=f'Disciplinas - {turma_display}',
            items=[],
            empty_text='Nenhuma disciplina associada'
        )

    return render_template('componentes/cards-grid.html', titulo=f'Disciplinas - {turma_display}', items=items)

def render_cards_turmas(turmas):
    return render_template('componentes/cards-grid.html', turmas=turmas)

def build_modal_add_turma():
    form = (FormBuilder.criar('/turmas/', '#tabela-turmas tbody')
        .add_number('ano', 'Ano', value=1, required=True)
        .add_text('identificador', 'Identificador', required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Turma')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_turma(turma):
    form = (FormBuilder.editar('/turmas', turma['id'], f"#turma-{turma['id']}")
        .add_number('ano', 'Ano', value=turma.get('ano', 1), required=True)
        .add_text('identificador', 'Identificador', value=turma.get('identificador', ''), required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Turma {turma.get('turma_display', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_turma(turma):
    form = FormBuilder.deletar('/turmas', turma['id'], f"#turma-{turma['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(render_template(
            'componentes/alert.html',
            type='danger',
            text=f"Tem certeza que deseja remover a turma <strong>{turma.get('turma_display', '')}</strong>?"
        ))
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_turma(turma):
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"turma-{turma['id']}",
            'colunas': [turma.get('ano', ''), turma.get('identificador', '')],
            'botoes': TableBuilder.botoes_crud('/turmas', turma['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
