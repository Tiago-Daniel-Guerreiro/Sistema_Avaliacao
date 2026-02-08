from flask import Blueprint, request, redirect, render_template
from database.exame import get_exames, get_exame_by_id, add_exame, update_exame, delete_exame, get_exames_by_disciplina_turma
from database.disciplina_turma import get_disciplina_turmas
from database.questao import get_questoes_by_exame, get_questao_by_id
from database.tipos_questao import get_tipo_questao_by_id, get_tipos_questao
from database.submissao_exame import get_submissoes_exame_by_exame, get_submissoes_exame_by_exame_aluno, get_submissoes_questao_by_submissao, get_submissao_exame_by_id, update_pontuacao_questao, get_submissao_questao_by_id
from database.aluno import get_aluno_by_id
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from datetime import datetime, timedelta
from ui.exames import (
    render_page_exames,
    render_base_with_content,
    build_exame_view_content,
    build_table_exames,
    build_modal_add_exame,
    build_modal_edit_exame,
    build_modal_delete_exame,
    render_linha_exame,
    build_disciplina_turma_exames_table,
    build_exame_questoes_lista,
    build_exame_questoes_professor,
    build_exame_submissoes_professor,
    build_exame_questoes_aluno,
    build_submissao_view,
    build_submissao_questao_row
)

exames_route = Blueprint('exames', __name__, url_prefix='/exames')
exame_route = Blueprint('exame', __name__, url_prefix='/exame')

@exame_route.route('/<int:exame_id>/')
def exame_view(exame_id):
    cargo = obter_cargo_usuario()
    if cargo in [Cargo.PROFESSOR, Cargo.ADMIN]:
        return redirect(f'/exames/{exame_id}')
    return redirect(f'/exame-aluno/visualizar/{exame_id}')

@exame_route.route('/<int:exame_id>/start')
def exame_start(exame_id):
    cargo = obter_cargo_usuario()
    if cargo in [Cargo.PROFESSOR, Cargo.ADMIN]:
        return redirect(f'/exames/{exame_id}')
    return redirect(f'/exame-aluno/visualizar/{exame_id}')

@exame_route.route('/<int:exame_id>')
def exame_view_no_slash(exame_id):
    return redirect(f'/exame/{exame_id}/')

@exames_route.route('/')
def page_exames():
    return render_page_exames(table_exames())

@exames_route.route('/<int:exame_id>')
def page_exame_view(exame_id):
    try:
        cargo = obter_cargo_usuario()
        exame = get_exame_by_id(exame_id)
        if not exame:
            content, status = erro_html('Exame não encontrado', 200)
            return render_base_with_content(content, status)
        
        # Preparar dados para header_card
        data_inicio = exame.get('data_hora_inicio', '')
        try:
            dt_inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
            
            if dt_inicio and exame.get('duracao_minutos'):
                dt_fim = dt_inicio + timedelta(minutes=exame['duracao_minutos'])
                data_fim_fmt = dt_fim.strftime('%d/%m/%Y %H:%M')
            else:
                data_fim_fmt = '-'
        except:
            data_fim_fmt = '-'
        
        # Preparar tabela de questões com TableBuilder
        questoes = get_questoes_by_exame(exame_id)
        questoes.sort(key=lambda q: float(q.get('numero_questao', 0)))
        
        submissoes_rows = None
        if cargo in [Cargo.PROFESSOR, Cargo.ADMIN]:
            submissoes = get_submissoes_exame_by_exame(exame_id)
            submissoes_rows = []
            for sub in submissoes:
                aluno = get_aluno_by_id(sub.get('aluno_id', 0))
                aluno_nome = aluno.get('nome', 'Desconhecido') if aluno else 'Desconhecido'
                data_sub = sub.get('data_hora_fim') or sub.get('data_hora_inicio') or '-'
                if data_sub != '-':
                    try:
                        data_sub = datetime.fromisoformat(data_sub).strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        pass
                nota = sub.get('nota_final', '-')
                status = 'professor' if sub.get('nota_final') is not None else 'automatico'
                sub_questoes = get_submissoes_questao_by_submissao(sub['id'])
                nota_automatica = sum((q.get('pontuacao_atribuida') or 0) for q in sub_questoes) if sub_questoes else 0

                submissoes_rows.append({
                    'id': sub['id'],
                    'aluno_nome': aluno_nome,
                    'data_sub': data_sub,
                    'nota_automatica': nota_automatica,
                    'nota': nota,
                    'status': status
                })

        html = build_exame_view_content(exame, questoes, data_fim_fmt, submissoes_rows)
        return render_base_with_content(html, 200)
    except Exception as e:
        content, status = erro_html(f'Erro ao carregar exame: {str(e)}', 500)
        return render_base_with_content(content, status)

@exames_route.route('/table')
def table_exames():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        exames = get_exames()
        
        return build_table_exames(exames)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/modal/add')
def modal_add_exame():
    try:
        disciplinas_turma = get_disciplina_turmas()
        return build_modal_add_exame(disciplinas_turma)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/<int:exame_id>/modal/edit')
def modal_edit_exame(exame_id):
    try:
        exame = get_exame_by_id(exame_id)
        
        if not exame:
            return erro_html('Exame não encontrado', 200)
        
        disciplinas_turma = get_disciplina_turmas()
        
        return build_modal_edit_exame(exame, disciplinas_turma)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/<int:exame_id>/modal/delete')
def modal_delete_exame(exame_id):
    try:
        exame = get_exame_by_id(exame_id)
        
        if not exame:
            return erro_html('Exame não encontrado', 200)
        
        return build_modal_delete_exame(exame)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/', methods=['POST'])
def criar_exame():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = add_exame(
            disciplina_turma_id=int(dados.get('disciplina_turma_id') or 0),
            titulo=dados.get('titulo'),
            data_hora_inicio=dados.get('data_hora_inicio'),
            duracao_minutos=int(dados.get('duracao_minutos', 60)),
            publico=int(dados.get('publico', 0) or 0)
        )
        
        if resultado['ok']:
            exame = resultado['exame']
            
            return render_linha_exame(exame)
        
        return erro_html(resultado.get('erro', 'Erro'), 200)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/<int:exame_id>', methods=['PUT'])
def atualizar_exame(exame_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resultado = update_exame(
            exame_id=exame_id,
            titulo=dados.get('titulo'),
            disciplina_turma_id=int(dados.get('disciplina_turma_id') or 0),
            data_hora_inicio=dados.get('data_hora_inicio'),
            duracao_minutos=int(dados.get('duracao_minutos', 60)),
            publico=int(dados.get('publico', 0) or 0)
        )
        
        if resultado['ok']:
            exame = resultado['exame']
            
            return render_linha_exame(exame)
        
        return erro_html('Exame não encontrado', 200)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/<int:exame_id>', methods=['DELETE'])
def deletar_exame(exame_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        resultado = delete_exame(exame_id)
        
        if resultado['ok']:
            return '', 200
        
        return erro_html('Exame não encontrado', 200)
        
    except Exception as e:
        return erro_500(e)

@exames_route.route('/disciplina-turma/<int:disciplina_turma_id>/exames-table')
def disciplina_turma_exames_table(disciplina_turma_id):
    try:
        exames = get_exames_by_disciplina_turma(disciplina_turma_id)
        exames = [e for e in exames if e.get('publico', False)]
        
        if not exames:
            return '<p class="text-muted text-center py-4">Nenhuma avaliação disponível</p>'
        
        aluno_id = request.args.get('aluno_id', 0, type=int)
        
        now = datetime.now()
        rows = []
        for exame in exames:
            data_inicio = exame.get('data_hora_inicio', '')
            try:
                dt = datetime.fromisoformat(data_inicio) if data_inicio else None
                data_formatada = dt.strftime('%d/%m/%Y %H:%M') if dt else '-'
                pode_fazer = dt <= now if dt else False
            except Exception:
                data_formatada = '-'
                pode_fazer = False
            
            exame_id = exame['id']
            estado_submissao = None
            if aluno_id:
                submissao = get_submissoes_exame_by_exame_aluno(exame_id, aluno_id)
                estado_submissao = submissao.get('estado') if submissao else None

            rows.append({
                'id': exame_id,
                'titulo': exame.get('titulo', 'Sem título'),
                'data': data_formatada,
                'duracao': exame.get('duracao_minutos', '-'),
                'estado': estado_submissao,
                'pode_fazer': pode_fazer
            })

        return build_disciplina_turma_exames_table(rows)
    except Exception as e:
        return erro_html(f'Erro ao carregar exames: {str(e)}', 500)

@exames_route.route('/exame/<int:exame_id>/questoes-lista')
def exame_questoes_lista(exame_id):
    try:
        questoes = get_questoes_by_exame(exame_id)
        
        if not questoes:
            return '<p class="text-muted text-center py-4">Sem questões cadastradas</p>'
        
        questoes.sort(key=lambda q: float(q.get('numero_questao', 0)))
        
        return build_exame_questoes_lista(exame_id, questoes)
    except Exception as e:
        return erro_html(f'Erro ao carregar questões: {str(e)}', 500)

@exames_route.route('/exame/<int:exame_id>/questoes-professor')
def exame_questoes_professor(exame_id):
    try:
        questoes = get_questoes_by_exame(exame_id)
        if not questoes:
            return render_template('componentes/alert.html', type='info', text='Nenhuma questão adicionada ainda')
        
        questoes.sort(key=lambda q: float(q.get('numero_questao', 0)))
        
        for q in questoes:
            tipo = get_tipo_questao_by_id(q.get('tipo_questao_id', 0))
            q['tipo_nome'] = tipo.get('nome', 'Desconhecido') if tipo else 'Desconhecido'

        return build_exame_questoes_professor(exame_id, questoes)
    except Exception as e:
        return erro_500(e)

@exames_route.route('/exame/<int:exame_id>/submissoes-professor')
def exame_submissoes_professor(exame_id):
    try:
        submissoes = get_submissoes_exame_by_exame(exame_id)
        if not submissoes:
            return render_template('componentes/alert.html', type='info', text='Nenhuma submissão ainda')
        
        rows = []
        for sub in submissoes:
            aluno = get_aluno_by_id(sub.get('aluno_id', 0))
            aluno_nome = aluno.get('nome', 'Desconhecido') if aluno else 'Desconhecido'
            data_sub = sub.get('data_submissao', '-')
            nota = sub.get('nota_final', '-')
            corrigida = sub.get('nota_final') is not None

            rows.append({
                'id': sub['id'],
                'aluno_nome': aluno_nome,
                'data_sub': data_sub,
                'nota': nota,
                'corrigida': corrigida
            })

        return build_exame_submissoes_professor(rows)
    except Exception as e:
        return erro_500(e)

@exames_route.route('/exame/<int:exame_id>/questoes-aluno')
def exame_questoes_aluno(exame_id):
    try:
        questoes = get_questoes_by_exame(exame_id)
        if not questoes:
            return render_template('componentes/alert.html', type='info', text='Nenhuma questão disponível')
        
        questoes.sort(key=lambda q: float(q.get('numero_questao', 0)))
        
        for q in questoes:
            tipo = get_tipo_questao_by_id(q.get('tipo_questao_id', 0))
            q['tipo_nome'] = tipo.get('nome', 'Desconhecido') if tipo else 'Desconhecido'

        return build_exame_questoes_aluno(exame_id, questoes)
    except Exception as e:
        return erro_500(e)

@exames_route.route('/submissao/<int:submissao_id>/view')
@exames_route.route('/submissao/<int:submissao_id>/view/')
def view_submissao_exame(submissao_id):
    try:
        submissao = get_submissao_exame_by_id(submissao_id)
        if not submissao:
            return erro_html('Submissão não encontrada', 200)

        questoes = get_submissoes_questao_by_submissao(submissao_id)
        return build_submissao_view(submissao, questoes)
    except Exception as e:
        return erro_500(e)

@exames_route.route('/submissao-questao/<int:submissao_questao_id>/pontuacao', methods=['PUT'])
def atualizar_pontuacao_submissao_questao(submissao_questao_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()

        dados = get_request_data()
        pontuacao = float(dados.get('pontuacao_atribuida', 0))

        resultado = update_pontuacao_questao(submissao_questao_id, pontuacao)
        if not resultado.get('ok'):
            return erro_html(resultado.get('erro', 'Erro ao atualizar pontuação'), 200)

        questao = get_submissao_questao_by_id(submissao_questao_id)
        if not questao:
            return erro_html('Submissão da questão não encontrada', 200)

        return build_submissao_questao_row(questao)
    except Exception as e:
        return erro_500(e)