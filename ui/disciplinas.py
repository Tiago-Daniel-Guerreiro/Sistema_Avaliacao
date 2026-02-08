from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_disciplinas(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_disciplinas(disciplinas):
    tabela = (TableBuilder(titulo='Lista de Disciplinas')
        .set_header(['Nome', 'Código'], acoes=True)
        .set_table_id('tabela-disciplinas')
        .set_botao_adicionar('/disciplinas/modal/add', 'Nova Disciplina')
    )

    for disciplina in disciplinas:
        tabela.add_linha(
            disciplina['nome'],
            disciplina['codigo'],
            row_id=f"disciplina-{disciplina['id']}",
            botoes=TableBuilder.botoes_crud('/disciplinas', disciplina['id'])
        )

    return tabela.build()

def build_modal_add_disciplina():
    form = (FormBuilder.criar('/disciplinas/', '#tabela-disciplinas tbody')
        .add_text('nome', 'Nome', required=True)
        .add_text('codigo', 'Código', required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Disciplina')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_disciplina(disciplina):
    form = (FormBuilder.editar('/disciplinas', disciplina['id'], f"#disciplina-{disciplina['id']}")
        .add_text('nome', 'Nome', value=disciplina.get('nome', ''), required=True)
        .add_text('codigo', 'Código', value=disciplina.get('codigo', ''), required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Disciplina: {disciplina.get('nome', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_disciplina(disciplina):
    form = FormBuilder.deletar('/disciplinas', disciplina['id'], f"#disciplina-{disciplina['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(f'''
            <p class="alert alert-danger">
                Tem certeza que deseja remover a disciplina <strong>{disciplina.get('nome', '')}</strong>?
            </p>
        ''')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_disciplina(disciplina):
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"disciplina-{disciplina['id']}",
            'colunas': [disciplina['nome'], disciplina['codigo']],
            'botoes': TableBuilder.botoes_crud('/disciplinas', disciplina['id'])
        },
        header={'acoes': True, 'colunas': []}
    )

def render_cards_grid(items, clickable=False, subtitle_size=None):
    return render_template(
        'componentes/cards-grid.html',
        items=items,
        clickable=clickable,
        subtitle_size=subtitle_size
    )
