from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder


def render_page_cargos(tabela_html):
    return render_template('base.html', content=tabela_html)


def ui_table_cargos(cargos):
    tabela = (TableBuilder(titulo='Lista de Cargos')
        .set_header(['Nome'], acoes=True)
        .set_table_id('tabela-cargos')
        .set_botao_adicionar('/cargos/modal/add', 'Novo Cargo')
    )

    for c in cargos:
        tabela.add_linha(
            c['nome'],
            row_id=f"cargo-{c['id']}",
            botoes=TableBuilder.botoes_crud('/cargos', c['id'])
        )

    return tabela.build()


def ui_modal_add_cargo():
    form = (FormBuilder.criar('/cargos/', '#tabela-cargos tbody')
        .add_text('nome', 'Nome', required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Cargo')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()


def ui_modal_edit_cargo(cargo):
    form = (FormBuilder.editar('/cargos', cargo['id'], f"#cargo-{cargo['id']}")
        .add_text('nome', 'Nome', value=cargo.get('nome', ''), required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Cargo: {cargo.get('nome', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()


def ui_modal_delete_cargo(cargo):
    form = FormBuilder.deletar('/cargos', cargo['id'], f"#cargo-{cargo['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(render_template(
            'componentes/alert.html',
            type='danger',
            text=f"Tem certeza que deseja remover o cargo <strong>{cargo.get('nome', '')}</strong>?\br\nEssa ação pode afetar todo o sistema, <strong>ESTA AÇÃO NÃO PODE SER REVERTIDA</strong> sem reiniciar a db, ou usar comandos sql diretamente."
        ))
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()


def ui_row_cargo(cargo):
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"cargo-{cargo['id']}",
            'colunas': [cargo['nome']],
            'botoes': TableBuilder.botoes_crud('/cargos', cargo['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
