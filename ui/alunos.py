from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_alunos(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_alunos(alunos):
    tabela = (TableBuilder(titulo='Lista de Alunos')
        .set_header(['Identificador', 'Nome', 'Email', 'Turma'], acoes=True)
        .set_table_id('tabela-alunos')
        .set_botao_adicionar('/alunos/modal/add', 'Novo Aluno')
    )

    for aluno in alunos:
        turma = aluno.get('turma_display', '') or aluno.get('turma', '') or '-'
        tabela.add_linha(
            aluno.get('identificador', ''),
            aluno.get('conta_nome', aluno.get('nome', '')),
            aluno.get('email', aluno.get('conta_email', '')),
            turma,
            row_id=f"aluno-{aluno['id']}",
            botoes=TableBuilder.botoes_crud('/alunos', aluno['id'])
        )

    return tabela.build()

def build_modal_add_aluno(turmas, contas):
    turma_opts = [(t['id'], t.get('turma_display', f"{t['ano']}º {t['identificador']}")) for t in turmas]
    conta_opts = [(c['id'], f"{c['nome']} - {c['email']}") for c in contas if c]

    form = (FormBuilder.criar('/alunos/', '#tabela-alunos tbody')
        .add_text('identificador', 'Identificador do Aluno', required=True, placeholder='Ex: 12345')
        .add_select('conta_id', 'Conta (Nome - Email)', options=conta_opts, required=True)
        .add_select('turma_id', 'Turma', options=turma_opts, required=False)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Aluno')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_aluno(aluno, turmas, contas):
    conta_opts = [(c['id'], f"{c['nome']} - {c['email']}") for c in contas if c]
    turma_opts = [(t['id'], t.get('turma_display', f"{t['ano']}º {t['identificador']}")) for t in turmas]

    form = (FormBuilder.editar('/alunos/', aluno['id'], f"#aluno-{aluno['id']}")
        .add_text('identificador', 'Identificador do Aluno', value=aluno.get('identificador', ''), required=True)
        .add_select('conta_id', 'Conta (Nome - Email)', value=aluno.get('id_conta', ''), options=conta_opts, required=True)
        .add_select('turma_id', 'Turma', value=aluno.get('turma_id', ''), options=turma_opts, required=False)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Aluno: {aluno.get('identificador', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_aluno(aluno):
    form = FormBuilder.deletar('/alunos', aluno['id'], f"#aluno-{aluno['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(f'''
            <p class="alert alert-danger">
                Tem certeza que deseja remover o aluno <strong>{aluno.get('identificador', '')}</strong>?
            </p>
        ''')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_aluno(aluno, turma_display=None):
    turma_nome = turma_display or aluno.get('turma_display') or aluno.get('turma_nome') or aluno.get('turma') or aluno.get('ano') or '-'
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"aluno-{aluno['id']}",
            'colunas': [
                aluno.get('identificador', ''),
                aluno.get('conta_nome', aluno.get('nome', '')),
                aluno.get('email', aluno.get('conta_email', '')),
                turma_nome
            ],
            'botoes': TableBuilder.botoes_crud('/alunos', aluno['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
