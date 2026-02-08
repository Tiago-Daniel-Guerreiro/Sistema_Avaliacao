from flask import render_template
from markupsafe import Markup
from utils.template_builder import FormBuilder, ModalBuilder, TableBuilder

def render_base_with_content(content, status=200):
    return render_template('base.html', content=content), status

def render_lista_exames(exames):
    content = Markup(render_template('exame_aluno_lista.html', exames=exames))
    return render_template('base.html', content=content)

def build_linha_questao(exame_id, questao, respondeu):
    questao_id = questao['id']

    botao_label = 'Visualizar' if respondeu else 'Responder'
    botao_class = 'btn btn-sm btn-secondary' if respondeu else 'btn btn-sm btn-success'

    botao_html = TableBuilder.botao(
        botao_label,
        f'/exame-aluno/modal/{exame_id}/{questao_id}',
        botao_class
    )

    linha = {
        'id': f'questao-{questao_id}',
        'colunas': [
            questao.get('numero_questao', ''),
            questao.get('tipo_nome', 'Texto'),
            questao.get('pontuacao_maxima', 0)
        ],
        'botoes': [botao_html]
    }

    return render_template('componentes/tabela_linha.html', linha=linha, header={'acoes': True, 'colunas': []})

def build_modal_questao_html(exame_id, questao, resposta_atual, opcoes, input_file, multiplas_respostas=False, read_only=False):
    questao_id = questao.get('id')
    numero_questao = questao.get('numero_questao', '')
    pontuacao = questao.get('pontuacao_maxima', 0)
    texto = questao.get('texto', '')
    titulo_modal = f"{numero_questao}. {texto}" if numero_questao else texto

    form = (FormBuilder(action=f'/exame-aluno/responder/{exame_id}/{questao_id}', method='POST')
        .set_ajax(True)
        .set_c_attrs(c_remove_closest="#modal-wrapper", c_swap=f"#questao-{questao_id}")
    )

    form.add_custom(Markup(render_template(
        'componentes/exame_questao_header.html',
        numero_questao=numero_questao,
        pontuacao=pontuacao,
        texto=texto
    )))

    opcoes_normalizadas = opcoes
    if isinstance(opcoes, str):
        try:
            import json
            opcoes_normalizadas = json.loads(opcoes) if opcoes else []
        except Exception:
            opcoes_normalizadas = [o.strip() for o in opcoes.split('\n') if o.strip()]

    campo_attrs = {
        'disabled': read_only,
        'multiplas_respostas': multiplas_respostas
    }
    if input_file == 'choices':
        campo_attrs['type'] = 'checkbox' if multiplas_respostas else 'radio'

    form.add_campo(
        input_file,
        'resposta',
        'Resposta',
        value=resposta_atual,
        required=True,
        options=opcoes_normalizadas,
        **campo_attrs
    )

    modal = (ModalBuilder(modal_id=f'modal-questao-{questao_id}', show_close_button=False)
        .set_titulo(titulo_modal)
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_submit_button('Guardar Resposta')
    )

    if read_only:
        modal.footer_buttons = []

    return str(modal.build())

def build_exame_header(exame, duracao_min, fim_previsto, tempo_restante_text, label_fim=None, label_tempo=None):
    return Markup(render_template(
        'componentes/header_card.html',
        titulo=exame.get('titulo', 'Exame'),
        disciplina=exame.get('disciplina_turma_display', '-'),
        duracao_minutos=duracao_min,
        fim_previsto=fim_previsto,
        tempo_restante=tempo_restante_text,
        label_fim=label_fim,
        label_tempo=label_tempo,
        descricao=None
    ))

def build_inicio_exame(exame_id):
    return Markup(render_template(
        'componentes/exame_inicio.html',
        action=f'/exame-aluno/iniciar/{exame_id}'
    ))

def build_exame_guard():
    return Markup(render_template('componentes/exame_guard.html'))

def build_tabela_questoes(exame_id, questoes, respostas_existentes):
    try:
        questoes = sorted(questoes, key=lambda q: float(q.get('numero_questao', 0)))
    except Exception:
        pass
    tabela = TableBuilder(titulo='Questões do Exame')
    tabela.set_header(['Nº', 'Tipo', 'Pontuação'], acoes=True)

    for questao in questoes:
        respondeu = questao['id'] in respostas_existentes
        linha_html = build_linha_questao(exame_id, questao, respondeu)
        tabela.linhas.append({'raw': True, 'html': Markup(linha_html)})

    return Markup(tabela.build())

def build_footer_finalizar(exame_id):
    return Markup(render_template(
        'componentes/exame_footer.html',
        action=f'/exame-aluno/finalizar/{exame_id}',
        button_label='Finalizar Exame',
        button_class='btn btn-danger btn-lg',
        is_form=True
    ))

def build_exame_finalizado_content(exame, questoes, sub_itens, respostas_map, total_pontos, total_max, fim_previsto):
    tabela = TableBuilder(titulo='Exame Finalizado - Suas Respostas')
    tabela.set_header(['Questão', 'Tipo', 'Pontuação', 'Sua Resposta', 'Avaliação automática', 'Avaliado pelo professor'], acoes=False)

    for questao in questoes:
        questao_id = questao['id']

        estado_avaliacao = ''
        pontuacao = 0
        pontuacao_auto = '-'
        for sub in sub_itens:
            if sub.get('questao_id') == questao_id:
                pontuacao = sub.get('pontuacao_atribuida', 0) or 0
                pontuacao_auto = pontuacao
                if sub.get('estado') == 'corrigida':
                    estado_avaliacao = 'Sim'
                elif sub.get('estado') == 'respondida':
                    estado_avaliacao = 'Não'
                else:
                    estado_avaliacao = '-'
                break

        avaliacao_badge = Markup(render_template(
            'componentes/badge.html',
            classes='bg-success' if estado_avaliacao == 'Sim' else ('bg-secondary' if estado_avaliacao == 'Não' else 'bg-light text-dark'),
            text=estado_avaliacao
        ))

        tabela.add_linha(
            questao.get('texto', '')[:50] + '...' if len(questao.get('texto', '')) > 50 else questao.get('texto', ''),
            questao.get('tipo_nome', 'Texto'),
            f"{pontuacao} / {questao.get('pontuacao_maxima', 0)}",
            respostas_map.get(questao_id, '(Não respondida)') or Markup(render_template('componentes/text_em.html', text='(Não respondida)')),
            pontuacao_auto,
            avaliacao_badge
        )

    header = Markup(render_template(
        'componentes/header_card.html',
        titulo=exame.get('titulo', 'Exame'),
        disciplina=exame.get('disciplina_turma_display', '-'),
        duracao_minutos=exame.get('duracao_minutos', 60),
        fim_previsto=fim_previsto,
        tempo_restante='Finalizado',
        label_fim='Data de entrega',
        label_tempo='Estado',
        descricao=None
    ))

    resumo = Markup(render_template(
        'componentes/alert.html',
        type='primary',
        text=Markup(f'Nota: <strong>{total_pontos}</strong> / {total_max}')
    ))
    footer = Markup(render_template(
        'componentes/exame_footer.html',
        action='/',
        button_label='Voltar ao Início',
        button_class='btn btn-primary',
        is_form=False
    ))

    alert = Markup(render_template(
        'componentes/alert.html',
        type='info',
        text=Markup('<strong>Exame Finalizado</strong> - Visualização apenas')
    ))

    tabela_html = Markup(tabela.build())
    content = alert + header + resumo + tabela_html + footer
    return Markup(content)
