from flask import render_template
from utils.template_builder import TableBuilder, FormBuilder, ModalBuilder

def render_page_submissao(tabela_html):
    return render_template('base.html', content=tabela_html)

def build_table_submissao(submissoes):
    tabela = (TableBuilder(titulo='Submissões de Respostas')
        .set_header(['Exame', 'Aluno', 'Questão', 'Resposta', 'Pontuação', 'Corrigida'], acoes=True)
           .set_table_id('tabela-submissao')
           .set_botao_adicionar('/submissao/modal/add', 'Nova Submissão')
    )

    for submissao in submissoes:
        exame_titulo = submissao.get('exame_titulo', 'N/A')
        aluno_nome = submissao.get('aluno_display', submissao.get('identificador', 'N/A'))
        questao_texto = submissao.get('questao_texto', '')[:40]
        resposta = submissao.get('resposta', '')[:40]
        pontuacao = submissao.get('pontuacao_atribuida', 0)
        corrigida = 'Sim' if submissao.get('corrigido_professor', False) else 'Não'

        tabela.add_linha(
            exame_titulo,
            aluno_nome,
            questao_texto,
            resposta,
            pontuacao,
            corrigida,
            row_id=f"submissao-{submissao['id']}",
            botoes=TableBuilder.botoes_crud('/submissao', submissao['id'])
        )

    return tabela.build()

def build_modal_add_submissao(exames, alunos, questoes):
    exame_opts = [(e['id'], e.get('titulo', '')) for e in exames]
    aluno_opts = [(a['id'], a.get('nome', '')) for a in alunos]
    questao_opts = [(q['id'], q.get('texto', '')[:60]) for q in questoes]

    form = (FormBuilder.criar('/submissao/', '#tabela-submissao tbody')
        .add_select('exame_id', 'Exame', options=exame_opts, required=True)
        .add_select('aluno_id', 'Aluno', options=aluno_opts, required=True)
        .add_select('questao_id', 'Questão', options=questao_opts, required=True)
        .add_text('resposta', 'Resposta', required=True)
        .add_number('pontuacao_atribuida', 'Pontuação', value=0, required=False)
    )

    modal = (ModalBuilder()
        .set_titulo('Adicionar Submissão')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Adicionar')
    )

    return modal.build()

def build_modal_edit_submissao(submissao, exames, alunos, questoes):
    exame_opts = [(e['id'], e.get('titulo', '')) for e in exames]
    aluno_opts = [(a['id'], a.get('nome', '')) for a in alunos]
    questao_opts = [(q['id'], q.get('texto', '')[:60]) for q in questoes]

    form = (FormBuilder.editar('/submissao', submissao['id'], f"#submissao-{submissao['id']}")
        .add_select('exame_id', 'Exame', value=submissao.get('exame_id'), options=exame_opts, required=True)
        .add_select('aluno_id', 'Aluno', value=submissao.get('aluno_id'), options=aluno_opts, required=True)
        .add_select('questao_id', 'Questão', value=submissao.get('questao_id'), options=questao_opts, required=True)
        .add_text('resposta', 'Resposta', value=submissao.get('resposta', ''), required=True)
        .add_number('pontuacao_atribuida', 'Pontuação', value=submissao.get('pontuacao_atribuida', 0), required=False)
    )

    modal = (ModalBuilder()
        .set_titulo('Editar Submissão')
        .set_form(form)
        .set_body(form.build()['campos'])
        .add_cancel_button()
        .add_submit_button('Atualizar')
    )

    return modal.build()

def build_modal_delete_submissao(submissao):
    form = FormBuilder.deletar('/submissao', submissao['id'], f"#submissao-{submissao['id']}")

    modal = (ModalBuilder()
        .set_titulo('Confirmação de Remoção')
        .set_form(form)
        .set_body(f'''
            <p class="alert alert-danger">
                Tem certeza que deseja remover esta submissão?
            </p>
            <p><strong>Resposta:</strong> {submissao.get('resposta', '')}</p>
        ''')
        .add_cancel_button()
        .add_submit_button('Confirmar Remoção', 'btn btn-danger')
    )

    return modal.build()

def render_linha_submissao(submissao):
    return render_template(
        'componentes/tabela_linha.html',
        linha={
            'id': f"submissao-{submissao['id']}",
            'colunas': [
                submissao.get('exame_titulo', 'N/A'),
                submissao.get('aluno_nome', 'N/A'),
                submissao.get('questao_texto', '')[:40],
                submissao.get('resposta', '')[:40],
                submissao.get('pontuacao_atribuida', 0)
            ],
            'botoes': TableBuilder.botoes_crud('/submissao', submissao['id'])
        },
        header={'acoes': True, 'colunas': []}
    )
