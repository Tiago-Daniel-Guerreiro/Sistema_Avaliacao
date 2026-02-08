from datetime import datetime
from flask import render_template
from markupsafe import Markup
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_exames(tabela_html):
    return render_template('base.html', content=tabela_html)

def render_base_with_content(content, status=200):
    return render_template('base.html', content=content), status

def build_exame_view_content(exame, questoes, data_fim_fmt, submissoes_rows=None):
    header = Markup(render_template(
        'componentes/header_card.html',
        titulo=exame.get('titulo', 'Sem título'),
        disciplina=exame.get('disciplina_turma_display', ''),
        duracao_minutos=exame.get('duracao_minutos', 0),
        fim_previsto=data_fim_fmt,
        tempo_restante='-',
        label_fim='Data de entrega',
        label_tempo='Estado',
        show_tempo=False,
        descricao=None
    ))

    tabela = (TableBuilder(titulo='Questões')
        .set_header(['Nº', 'Texto', 'Tipo', 'Pontos'], acoes=True)
        .set_botao_adicionar(f'/questoes/exame/{exame["id"]}/modal/add', 'Nova Questão')
    )

    for q in questoes:
        tipo_nome = q.get('tipo_nome') or q.get('tipo_questao') or 'Desconhecido'
        texto = q.get('texto', '')[:100] + ('...' if len(q.get('texto', '')) > 100 else '')

        resposta_id = q.get('resposta_id')
        botoes = [
            TableBuilder.botao("Editar", f'/questoes/{q["id"]}/modal/edit', 'btn btn-sm btn-primary'),
            TableBuilder.botao("Deletar", f'/questoes/{q["id"]}/modal/delete', 'btn btn-sm btn-danger')
        ]
        tipo_info = q.get('tipo_info')
        if resposta_id and tipo_info and ((tipo_info.get('list_options') in [1, True]) or (tipo_info.get('correcao_automatica') in [1, True])):
            botoes.append(TableBuilder.botao("Editar Respostas", f'/resposta/{resposta_id}/modal/edicao', 'btn btn-sm btn-outline-primary'))

        tabela.add_linha(
            Markup(f'<strong>{q.get("numero_questao", "?")}</strong>'),
            texto,
            Markup(f'<small class="badge bg-secondary">{tipo_nome}</small>'),
            Markup(f'<strong>{q.get("pontuacao_maxima", 0)}</strong>'),
            row_id=f"questao-{q['id']}",
            botoes=botoes
        )

    submissoes_html = ''
    if submissoes_rows is not None:
        submissoes_html = build_exame_submissoes_professor(submissoes_rows)

    tabela_html = f'<div id="tabela-questoes-exame">{tabela.build()}</div>'
    html = f'{header}\n{tabela_html}\n{submissoes_html}'
    return html

def build_exame_questao_row(questao):
    tipo_nome = questao.get('tipo_nome') or questao.get('tipo_questao') or 'Desconhecido'
    texto = questao.get('texto', '')[:100] + ('...' if len(questao.get('texto', '')) > 100 else '')

    resposta_id = questao.get('resposta_id')
    botoes = [
        TableBuilder.botao("Editar", f'/questoes/{questao["id"]}/modal/edit', 'btn btn-sm btn-primary'),
        TableBuilder.botao("Deletar", f'/questoes/{questao["id"]}/modal/delete', 'btn btn-sm btn-danger')
    ]
    tipo_info = questao.get('tipo_info')
    if resposta_id and tipo_info and ((tipo_info.get('list_options') in [1, True]) or (tipo_info.get('correcao_automatica') in [1, True])):
        botoes.append(TableBuilder.botao("Editar Respostas", f'/resposta/{resposta_id}/modal/edicao', 'btn btn-sm btn-outline-primary'))

    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"questao-{questao['id']}",
            'colunas': [
                Markup(f'<strong>{questao.get("numero_questao", "?")}</strong>'),
                texto,
                Markup(f'<small class="badge bg-secondary">{tipo_nome}</small>'),
                Markup(f'<strong>{questao.get("pontuacao_maxima", 0)}</strong>')
            ],
            'botoes': botoes
        },
        header={'acoes': True, 'colunas': []}
    )

def build_table_exames(exames):
    tabela = (TableBuilder(titulo='Lista de Exames')
        .set_header(['Turma - Disciplina', 'Título', 'Data Início', 'Duração (min)', 'Público'], acoes=True)
        .set_table_id('tabela-exames')
        .set_botao_adicionar('/exames/modal/add', 'Novo Exame')
    )

    for exame in exames:
        turma_disc = exame.get('disciplina_turma_display', exame.get('turma_disciplina', ''))
        data_inicio = exame.get('data_hora_inicio', '')[:16] if exame.get('data_hora_inicio') else '-'
        publico = 'Sim' if exame.get('publico', False) else 'Não'

        tabela.add_linha(
            turma_disc,
            exame.get('titulo', ''),
            data_inicio,
            exame.get('duracao_minutos', 0),
            publico,
            row_id=f"exame-{exame['id']}",
            botoes=TableBuilder.botoes_crud('/exames', exame['id'])
        )

    return tabela.build()

def build_modal_add_exame(disciplinas_turma):
    dt_opts = [
        (dt['id'], f"{dt.get('turma_display', '')} - {dt.get('disciplina_codigo', '')}")
        for dt in disciplinas_turma
    ]

    form = (FormBuilder.criar('/exames/', '#tabela-exames tbody')
        .add_select('disciplina_turma_id', 'Turma - Disciplina', options=dt_opts, required=True)
        .add_text('titulo', 'Título', required=True)
        .add_campo('datetime', 'data_hora_inicio', 'Data/Hora Início', required=True)
        .add_number('duracao_minutos', 'Duração (minutos)', value=60, required=True)
        .add_select('publico', 'Público', options=[(1, 'Sim'), (0, 'Não')], value=0, required=True)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Exame')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_exame(exame, disciplinas_turma):
    dt_opts = [
        (dt['id'], f"{dt.get('turma_display', '')} - {dt.get('disciplina_codigo', '')}")
        for dt in disciplinas_turma
    ]

    data_inicio = exame.get('data_hora_inicio', '')
    if data_inicio and len(data_inicio) > 16:
        data_inicio = data_inicio[:16]

    publico_value = 1 if exame.get('publico', False) else 0

    form = (FormBuilder.editar('/exames', exame['id'], f"#exame-{exame['id']}")
        .add_select('disciplina_turma_id', 'Turma - Disciplina', value=exame.get('disciplina_turma_id', ''), options=dt_opts, required=True)
        .add_text('titulo', 'Título', value=exame.get('titulo', ''), required=True)
        .add_campo('datetime', 'data_hora_inicio', 'Data/Hora Início', value=data_inicio, required=True)
        .add_number('duracao_minutos', 'Duração (minutos)', value=exame.get('duracao_minutos', 60), required=True)
        .add_select('publico', 'Público', value=publico_value, options=[(1, 'Sim'), (0, 'Não')], required=True)
    )

    modal = (ModalBuilder()
        .set_titulo(f"Editar Exame: {exame.get('titulo', '')}")
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_exame(exame):
    form = FormBuilder.deletar('/exames', exame['id'], f"#exame-{exame['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(render_template(
            'componentes/alert.html',
            type='danger',
            text=Markup(f'Tem certeza que deseja remover o exame <strong>{exame.get("titulo", "")}</strong>?')
        ))
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_exame(exame):
    turma_disc_display = exame.get('disciplina_turma_display', '')
    data_inicio = exame.get('data_hora_inicio', '')[:16] if exame.get('data_hora_inicio') else '-'
    publico = 'Sim' if exame.get('publico', False) else 'Não'

    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"exame-{exame['id']}",
            'colunas': [
                turma_disc_display,
                exame.get('titulo', ''),
                data_inicio,
                exame.get('duracao_minutos', 0),
                publico
            ],
            'botoes': TableBuilder.botoes_crud('/exames', exame['id'])
        },
        header={'acoes': True, 'colunas': []}
    )

def build_disciplina_turma_exames_table(exames_rows):
    tabela = (TableBuilder()
        .set_header(['Título', 'Data', 'Duração', 'Estado', 'Ação'], acoes=False)
    )

    for row in exames_rows:
        estado = row.get('estado')
        acao = row.get('acao')

        if estado == 'finalizado':
            estado = Markup('<span class="badge bg-success">Realizada</span>')
            acao = TableBuilder.botao('Visualizar', f'/exames/exame/{row["id"]}/exame-aluno-view', 'btn btn-sm btn-secondary', '#conteudo-principal')
        elif estado in ['em_andamento', 'em_progresso']:
            estado = Markup('<span class="badge bg-info text-dark">Em andamento</span>')
            acao = TableBuilder.botao('Continuar', f'/exames/exame/{row["id"]}/exame-aluno-view', 'btn btn-sm btn-primary', '#conteudo-principal')
        elif row.get('pode_fazer'):
            estado = Markup('<span class="badge bg-primary">Disponível</span>')
            acao = TableBuilder.botao('Realizar', f'/exames/exame/{row["id"]}/exame-aluno-view', 'btn btn-sm btn-success', '#conteudo-principal')
        else:
            estado = Markup('<span class="badge bg-warning text-dark">Em breve</span>')
            acao = Markup('')

        tabela.add_linha(
            row.get('titulo', 'Sem título'),
            row.get('data', '-'),
            row.get('duracao', '-'),
            estado,
            acao
        )

    return tabela.build()

def build_exame_questoes_lista(exame_id, questoes):
    tabela = (TableBuilder()
        .set_header(['Nº', 'Texto', 'Tipo', 'Pontos'], acoes=True)
    )

    for q in questoes:
        tipo_nome = q.get('tipo_nome') or q.get('tipo_questao') or 'Desconhecido'
        texto = q.get('texto', '')[:100] + ('...' if len(q.get('texto', '')) > 100 else '')

        resposta_id = q.get('resposta_id')
        botoes = [
            TableBuilder.botao("Editar", f'/questoes/{q["id"]}/modal/edit', 'btn btn-sm btn-primary'),
            TableBuilder.botao("Deletar", f'/questoes/{q["id"]}/modal/delete', 'btn btn-sm btn-danger')
        ]
        tipo_info = q.get('tipo_info')
        if resposta_id and tipo_info and ((tipo_info.get('list_options') in [1, True]) or (tipo_info.get('correcao_automatica') in [1, True])):
            botoes.append(TableBuilder.botao("Editar Respostas", f'/resposta/{resposta_id}/modal/edicao', 'btn btn-sm btn-outline-primary'))

        tabela.add_linha(
            Markup(f'<strong>{q.get("numero_questao", "?")}</strong>'),
            texto,
            Markup(f'<small class="badge bg-secondary">{tipo_nome}</small>'),
            Markup(f'<strong>{q.get("pontuacao_maxima", 0)}</strong>'),
            row_id=f"questao-{q['id']}",
            botoes=botoes
        )

    return tabela.build()

def build_exame_questoes_professor(exame_id, questoes):
    tabela = (TableBuilder(titulo='Questões do Exame')
        .set_header(['Nº', 'Questão', 'Tipo', 'Pontuação'], acoes=True)
    )

    for q in questoes:
        tipo_nome = q.get('tipo_nome', 'Desconhecido')
        texto = q.get('texto', '')[:100] + ('...' if len(q.get('texto', '')) > 100 else '')

        resposta_id = q.get('resposta_id')
        botoes = [
            TableBuilder.botao("Editar", f'/questoes/{q["id"]}/modal/edit', 'btn btn-sm btn-primary'),
            TableBuilder.botao("Deletar", f'/questoes/{q["id"]}/modal/delete', 'btn btn-sm btn-danger')
        ]
        tipo_info = q.get('tipo_info')
        if resposta_id and tipo_info and ((tipo_info.get('list_options') in [1, True]) or (tipo_info.get('correcao_automatica') in [1, True])):
            botoes.append(TableBuilder.botao("Editar Respostas", f'/resposta/{resposta_id}/modal/edicao', 'btn btn-sm btn-outline-primary'))

        tabela.add_linha(
            Markup(f'<strong>{q.get("numero_questao", "?")}</strong>'),
            texto,
            Markup(f'<small class="badge bg-secondary">{tipo_nome}</small>'),
            Markup(f'<strong>{q.get("pontuacao_maxima", 0)} pts</strong>'),
            row_id=f"questao-{q['id']}",
            botoes=botoes
        )

    return tabela.build()

def build_exame_submissoes_professor(submissoes_rows):
    tabela = (TableBuilder(titulo='Submissões do Exame')
        .set_header(['Aluno', 'Data Submissão', 'Nota Automática', 'Nota Final', 'Status'], acoes=True)
    )

    for row in submissoes_rows:
        status = Markup(render_template(
            'componentes/badge.html',
            classes='bg-success' if row.get('status') == 'professor' else 'bg-secondary',
            text='Professor' if row.get('status') == 'professor' else 'Automático'
        ))
        tabela.add_linha(
            row.get('aluno_nome', 'Desconhecido'),
            row.get('data_sub', '-'),
            Markup(f'<strong>{row.get("nota_automatica", "-")}</strong>'),
            Markup(f'<strong>{row.get("nota", "-")}</strong>'),
            status,
            row_id=f"submissao-{row['id']}",
            botoes=[
                TableBuilder.botao("Ver Detalhes", f'/exames/submissao/{row["id"]}/view', 'btn btn-sm btn-secondary')
            ]
        )

    return tabela.build()

def build_exame_questoes_aluno(exame_id, questoes):
    tabela = (TableBuilder(titulo='Questões')
        .set_header(['Nº', 'Questão', 'Tipo', 'Pontuação'], acoes=True)
    )

    for idx, q in enumerate(questoes):
        tipo_nome = q.get('tipo_nome', 'Desconhecido')
        texto = q.get('texto', '')[:100] + ('...' if len(q.get('texto', '')) > 100 else '')

        tabela.add_linha(
            Markup(f'<strong>{q.get("numero_questao", idx+1)}</strong>'),
            texto,
            Markup(f'<small class="badge bg-secondary">{tipo_nome}</small>'),
            Markup(f'<strong>{q.get("pontuacao_maxima", 0)} pts</strong>'),
            row_id=f"questao-{q['id']}",
            botoes=[
                TableBuilder.botao("Responder", f'/exames/exame/{exame_id}/questoes/{q["id"]}/view', 'btn btn-sm btn-success')
            ]
        )

    return tabela.build()

def build_submissao_view(submissao, questoes):
    tabela = (TableBuilder(titulo='Detalhes da Submissão')
        .set_header(['Questão', 'Resposta', 'Pontuação', 'Estado'], acoes=False)
    )

    for q in questoes:
        linha_html = build_submissao_questao_row(q)
        tabela.linhas.append({'raw': True, 'html': Markup(linha_html)})

    modal = (ModalBuilder()
        .set_titulo(f"Submissão #{submissao.get('id', '')}")
        .set_body(tabela.build())
        .add_cancel_button('Fechar')
    )

    return modal.build()

def build_submissao_questao_row(q):
    estado_texto = 'Professor' if q.get('estado') == 'corrigida' else 'Automático'
    estado_badge = Markup(render_template(
        'componentes/badge.html',
        classes='bg-success' if q.get('estado') == 'corrigida' else 'bg-secondary',
        text=estado_texto
    ))

    form = (FormBuilder(action=f"/exames/submissao-questao/{q.get('id')}/pontuacao", method="put")
        .set_ajax(True)
        .set_c_attrs(c_type="html", c_swap=f"#sub-questao-{q.get('id')}")
        .add_custom(Markup(
            f"""
            <div class=\"d-flex align-items-center gap-2\">
                <input type=\"number\" class=\"form-control form-control-sm\" name=\"pontuacao_atribuida\" value=\"{q.get('pontuacao_atribuida', 0)}\" min=\"0\" step=\"0.5\" style=\"max-width: 120px;\">
                <button type=\"submit\" class=\"btn btn-sm btn-primary\">Salvar</button>
            </div>
            """
        ))
    )
    form_data = form.build()
    form = Markup(f"{form_data['open']}{form_data['campos']}{form_data['close']}")

    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"sub-questao-{q.get('id')}",
            'colunas': [
                q.get('texto', ''),
                q.get('resposta', ''),
                form,
                estado_badge
            ],
            'botoes': []
        },
        header={'acoes': False, 'colunas': []}
    )
