from flask import render_template
from markupsafe import Markup
import json
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def _determinar_campo_tipo(tipo_info, permitir_edit=False):
    if not tipo_info:
        return 'texto'

    input_file = (tipo_info.get('input_file') or '').strip().lower()
    if input_file:
        return input_file

    tipo_nome = tipo_info.get('nome', '').strip().lower()
    nome_map = {
        'texto': 'text',
        'email': 'email',
        'número': 'number',
        'numero': 'number',
        'número (com validação)': 'number',
        'senha': 'password',
        'área de texto': 'textarea',
        'area de texto': 'textarea',
        'dia e hora': 'datetime',
        'hora': 'time',
        'escondido': 'hidden',
        'opções (única resposta)': 'choices',
        'opcoes (unica resposta)': 'choices',
        'opções (múltiplas respostas)': 'choices',
        'opcoes (multiplas respostas)': 'choices',
        'selecionado (única)': 'select',
        'selecionado (unica)': 'select',
        'verdadeiro ou falso': 'true_false',
        'verdadeiro ou falso justificado': 'true_false_justificado'
    }
    return nome_map.get(tipo_nome, tipo_nome)

def render_page_resposta(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_resposta(respostas):
    tabela = (TableBuilder(titulo='Opções de Respostas por Questão')
        .set_header(['Questão', 'Tipo', 'Opções', 'Opção Correta'], acoes=True)
    )

    for resposta in respostas:
        opcoes_display = ', '.join(resposta.get('opcoes', [])) if isinstance(resposta.get('opcoes'), list) else str(resposta.get('opcoes', ''))
        questao_texto = resposta.get('q_texto', '')[:50]
        tipo_nome = resposta.get('tipo_nome', '')
        opcao_correta = resposta.get('opcao_correta', '-')

        tipo_info = resposta.get('tipo_info') or {}
        botoes = []
        if (
            tipo_info.get('list_options') in [1, True]
            or tipo_info.get('correcao_automatica') in [1, True]
            or tipo_info.get('multiplas_respostas') in [1, True]
        ):
            botoes = [
                TableBuilder.botao_editar(f'/resposta/{resposta["id"]}/modal/edicao'),
                TableBuilder.botao_remover(f'/resposta/{resposta["id"]}/modal/delete')
            ]

        tabela.add_linha(
            questao_texto,
            tipo_nome,
            opcoes_display,
            opcao_correta,
            row_id=f"resposta-{resposta['id']}",
            botoes=botoes
        )

    return tabela.build()

def build_modal_edicao_resposta(resposta, questao, tipo_info):
    opcoes = resposta.get('opcoes', [])
    opcao_correta_value = resposta.get('opcao_correta')

    form = (FormBuilder.editar('/resposta', resposta['id'], f"#resposta-{resposta['id']}")
        .add_custom(Markup(f'''
            <div class="mb-3">
                <label class="form-label">Questão</label>
                <textarea class="form-control" name="questao_texto" rows="3" readonly style="background-color: #e9ecef; cursor: not-allowed;">{questao.get('texto', '')}</textarea>
            </div>
        '''))
    )

    campo_tipo = _determinar_campo_tipo(tipo_info, permitir_edit=True)

    attrs = {}
    attrs['initial_value'] = opcoes

    if tipo_info.get('list_options', False):
        if tipo_info.get('multiplas_respostas', False):
            # Permitir múltiplas corretas
            opcoes_corretas = []
            try:
                if isinstance(opcao_correta_value, str):
                    import json as _json
                    opcoes_corretas = _json.loads(opcao_correta_value)
                elif isinstance(opcao_correta_value, list):
                    opcoes_corretas = opcao_correta_value
            except Exception:
                opcoes_corretas = []
            form.add_input_list('opcoes', 'Opções', value=opcoes,
                                mode='multiple', opcoes_corretas=opcoes_corretas, **attrs)
        elif tipo_info.get('correcao_automatica', False):
            form.add_input_list('opcoes', 'Opções', value=opcoes,
                                mode='single', opcao_correta=opcao_correta_value, **attrs)
        else:
            form.add_input_list('opcoes', 'Opções', value=opcoes,
                                mode='simple', **attrs)
    else:
        form.add_campo(campo_tipo, 'opcoes', 'Opções', value=json.dumps(opcoes) if opcoes else None, required=True, **attrs)

    form.set_c_attrs(c_remove_closest="#modal-wrapper")

    modal = (ModalBuilder()
        .set_titulo('Editar Resposta de Teste')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Salvar')
    )

    return modal.build()

def build_modal_delete_resposta(resposta):
    form = FormBuilder.deletar('/resposta', resposta['id'], f"#resposta-{resposta['id']}")
    form.set_c_attrs(c_remove_closest="#modal-wrapper", c_remove=f"#resposta-{resposta['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body('<p class="alert alert-danger">Tem certeza que deseja remover esta resposta de teste?</p>')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_resposta(resposta):
    resposta_display = ', '.join(resposta.get('opcoes', [])) if isinstance(resposta.get('opcoes'), list) else str(resposta.get('opcoes', ''))
    questao_texto = resposta.get('q_texto', '')[:50]

    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"resposta-{resposta['id']}",
            'colunas': [questao_texto, resposta_display],
            'botoes': [
                TableBuilder.botao_editar(f'/resposta/{resposta["id"]}/modal/edicao'),
                TableBuilder.botao_remover(f'/resposta/{resposta["id"]}/modal/delete')
            ]
        },
        header={'acoes': True, 'colunas': []}
    )
