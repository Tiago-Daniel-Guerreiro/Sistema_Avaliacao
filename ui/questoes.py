from flask import render_template
from markupsafe import Markup
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_questoes(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_questoes(questoes):
    tabela = (TableBuilder(titulo='Lista de Questões')
        .set_header(['Título do Exame', 'Nº Questão', 'Tipo de Questão', 'Pontuação Máxima'], acoes=True)
        .set_table_id('tabela-questoes')
        .set_botao_adicionar('/questoes/modal/add', 'Nova Questão')
    )

    for questao in questoes:
        tipo_badge = Markup(render_template(
            'componentes/badge.html',
            classes='bg-secondary',
            text=questao.get('tipo_nome', '')
        ))
        resposta_id = questao.get('resposta_id')
        botoes = TableBuilder.botoes_crud('/questoes', questao['id'])
        if resposta_id:
            botoes.append(TableBuilder.botao('Editar Respostas', f'/resposta/{resposta_id}/modal/edicao', 'btn btn-sm btn-outline-primary'))

        tabela.add_linha(
            questao.get('exame_titulo', ''),
            questao.get('numero_questao', ''),
            tipo_badge,
            questao.get('pontuacao_maxima', 0),
            row_id=f"questao-{questao['id']}",
            botoes=botoes
        )

    return tabela.build()

def build_modal_add_questao(exames, tipos, exame_id=None):
    exame_opts = [(e['id'], e.get('titulo', '')) for e in exames]
    tipo_opts = [(t['id'], t['nome']) for t in tipos]

    form = (FormBuilder.criar('/questoes/', '#tabela-questoes tbody')
        .add_select('exame_id', 'Exame', value=exame_id, options=exame_opts, required=True)
        .add_number('numero_questao', 'Número da Questão', value=1, required=True)
        .add_select('tipo_questao_id', 'Tipo de Questão', options=tipo_opts, required=True)
        .add_custom(Markup('<div class="mb-3"><label class="form-label">Texto da Questão</label><textarea class="form-control" name="texto" rows="3" required></textarea></div>'))
        .add_number('pontuacao_maxima', 'Pontuação Máxima', value=1, required=True)
    )

    form.set_c_attrs(c_type='json', c_remove_closest="#modal-wrapper", c_callback='handleQuestaoAdd')

    modal = (ModalBuilder()
        .set_titulo('Adicionar Questão')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_questao(questao, exames, tipos):
    exame_opts = [(e['id'], e.get('titulo', '')) for e in exames]
    tipo_opts = [(t['id'], t['nome']) for t in tipos]

    form = (FormBuilder.editar('/questoes', questao['id'], f"#questao-{questao['id']}")
        .add_select('exame_id', 'Exame', value=questao.get('exame_id', ''), options=exame_opts, required=True)
        .add_number('numero_questao', 'Número da Questão', value=questao.get('numero_questao', 1), required=True)
        .add_select('tipo_questao_id', 'Tipo de Questão', value=questao.get('tipo_questao_id', ''), options=tipo_opts, required=True)
        .add_custom(Markup(f'<div class="mb-3"><label class="form-label">Texto da Questão</label><textarea class="form-control" name="texto" rows="3" required>{questao.get("texto", "")}</textarea></div>'))
        .add_number('pontuacao_maxima', 'Pontuação Máxima', value=questao.get('pontuacao_maxima', 1), required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Questão #{questao.get('numero_questao', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_questao(questao):
    form = FormBuilder.deletar('/questoes', questao['id'], f"#questao-{questao['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(f'''
            <p class="alert alert-danger">
                Tem certeza que deseja remover a questão <strong>#{questao.get('numero_questao', '')}</strong>?
            </p>
        ''')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_questao(questao):
    tipo_badge = Markup(render_template(
        'componentes/badge.html',
        classes='bg-secondary',
        text=questao.get('tipo_nome', '')
    ))
    resposta_id = questao.get('resposta_id')
    botoes = TableBuilder.botoes_crud('/questoes', questao['id'])
    if resposta_id:
        botoes.append(TableBuilder.botao('Editar Respostas', f'/resposta/{resposta_id}/modal/edicao', 'btn btn-sm btn-outline-primary'))

    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"questao-{questao['id']}",
            'colunas': [
                questao.get('exame_titulo', ''),
                questao.get('numero_questao', ''),
                tipo_badge,
                questao.get('pontuacao_maxima', 0)
            ],
            'botoes': botoes
        },
        header={'acoes': True, 'colunas': []}
    )
