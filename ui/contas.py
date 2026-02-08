from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_contas(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_contas(contas):
    tabela = (TableBuilder(titulo='Lista de Contas')
        .set_header(['Nome', 'Email', 'Cargo'], acoes=True)
        .set_table_id('tabela-contas')
        .set_botao_adicionar('/contas/modal/add', 'Nova Conta')
    )

    for conta in contas:
        tabela.add_linha(
            conta['nome'],
            conta['email'],
            conta.get('cargo_nome', conta.get('cargo_display', conta.get('nome_cargo', ''))),
            row_id=f"conta-{conta['id']}",
            botoes=TableBuilder.botoes_crud('/contas', conta['id'])
        )

    return tabela.build()

def build_modal_add_conta(roles):
    role_options = [(r['id'], r['nome']) for r in roles]

    form = (FormBuilder.criar('/contas/', '#tabela-contas tbody')
        .add_text('nome', 'Nome', required=True)
        .add_email('email', 'Email', required=True)
        .add_campo('password', 'senha', 'Senha', required=True)
        .add_select('id_cargo', 'Cargo', options=role_options, required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Conta')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_conta(conta, roles):
    role_options = [(r['id'], r['nome']) for r in roles]

    form = (FormBuilder.editar('/contas', conta['id'], f"#conta-{conta['id']}")
        .add_text('nome', 'Nome', value=conta.get('nome', ''), required=True)
        .add_email('email', 'Email', value=conta.get('email', ''), required=True)
        .add_campo('password', 'senha', 'Senha (deixe vazio para manter)', required=False)
        .add_select('id_cargo', 'Cargo', value=conta.get('id_cargo', ''), options=role_options, required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Conta: {conta.get('nome', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_conta(conta):
    form = FormBuilder.deletar('/contas', conta['id'], f"#conta-{conta['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(f'''
            <p class="alert alert-danger">
                Tem certeza que deseja remover a conta <strong>{conta.get('nome', '')}</strong>?
            </p>
        ''')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_conta(conta):
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"conta-{conta['id']}",
            'colunas': [conta['nome'], conta['email'], conta.get('cargo_display', conta.get('cargo_nome', ''))],
            'botoes': TableBuilder.botoes_crud('/contas', conta['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
