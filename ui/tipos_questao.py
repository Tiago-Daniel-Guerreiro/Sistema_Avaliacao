from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_tipos_questao(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_tipos_questao(tipos):
    tabela = (TableBuilder(titulo='Lista de Tipos de Questão')
        .set_header(['Nome', 'File Name', 'Opções de Lista', 'Correção Automática'], acoes=True)
        .set_table_id('tabela-tipos-questao')
        .set_botao_adicionar('/tipos-questao/modal/add', 'Novo Tipo')
    )

    for tipo in tipos:
        tabela.add_linha(
            tipo['nome'],
            tipo.get('input_file', ''),
            TableBuilder.formatar_booleano(tipo.get('list_options')),
            TableBuilder.formatar_booleano(tipo.get('correcao_automatica')),
            row_id=f"tipo-questao-{tipo['id']}",
            botoes=TableBuilder.botoes_crud('/tipos-questao', tipo['id'])
        )

    return tabela.build()

def build_modal_add_tipo_questao():
    form = (FormBuilder.criar('/tipos-questao/', '#tabela-tipos-questao tbody')
        .add_text('nome', 'Nome', required=True)
        .add_text('input_file', 'File Name', required=True)
        .add_select('list_options', 'Tem Opções de Lista (Múltipla Escolha)?', value='0', options=[('0', 'Não'), ('1', 'Sim')], required=True)
        .add_select('correcao_automatica', 'Ativar Correção Automática?', value='1', options=[('0', 'Não'), ('1', 'Sim')], required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Tipo de Questão')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_tipo_questao(tipo):
    form = (FormBuilder.editar('/tipos-questao', tipo['id'], f"#tipo-questao-{tipo['id']}")
        .add_text('nome', 'Nome', value=tipo.get('nome', ''), required=True)
        .add_text('input_file', 'File Name', value=tipo.get('input_file', ''), required=True)
        .add_select('list_options', 'Tem Opções de Lista (Múltipla Escolha)?', value=str(int(tipo.get('list_options', 0))), options=[('0', 'Não'), ('1', 'Sim')], required=True)
        .add_select('correcao_automatica', 'Ativar Correção Automática?', value=str(int(tipo.get('correcao_automatica', 1))), options=[('0', 'Não'), ('1', 'Sim')], required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Tipo de Questão: {tipo.get('nome', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_tipo_questao(tipo):
    form = FormBuilder.deletar('/tipos-questao', tipo['id'], f"#tipo-questao-{tipo['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(render_template(
            'componentes/alert.html',
            type='danger',
            text=f"Tem certeza que deseja remover o tipo de questão <strong>{tipo.get('nome', '')}</strong>?"
        ))
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_tipo_questao(tipo):
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"tipo-questao-{tipo['id']}",
            'colunas': [
                tipo['nome'],
                tipo.get('input_file', ''),
                TableBuilder.formatar_booleano(tipo.get('list_options')),
                TableBuilder.formatar_booleano(tipo.get('correcao_automatica'))
            ],
            'botoes': TableBuilder.botoes_crud('/tipos-questao', tipo['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
