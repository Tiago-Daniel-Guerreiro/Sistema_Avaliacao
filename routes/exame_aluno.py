from flask import Blueprint, request, jsonify, redirect, session
from markupsafe import Markup
from datetime import datetime, timedelta
import json
import traceback
from database.exame import get_exame_by_id, get_exames
from database.questao import get_questoes_by_exame, get_questao_by_id
from database.resposta import get_respostas_by_questao
from database.tipos_questao import get_tipo_questao_by_id
from database.submissao_exame import (
    get_submissoes_exame_by_exame_aluno, add_submissao_exame,
    update_submissao_exame_fim, get_submissao_exame_by_id,
    add_submissao_questao, get_submissoes_questao_by_submissao
)
from database.submissao import add_submissao
from utils.permissions import erro_500, erro_html, obter_aluno_id
from ui.exame_aluno import (
    render_base_with_content,
    render_lista_exames,
    build_linha_questao,
    build_modal_questao_html,
    build_exame_header,
    build_inicio_exame,
    build_tabela_questoes,
    build_exame_guard,
    build_footer_finalizar,
    build_exame_finalizado_content
)

exame_aluno_route = Blueprint('exame_aluno', __name__, url_prefix='/exame-aluno')

@exame_aluno_route.route('/modal/<int:exame_id>/<int:questao_id>')
def carregar_modal_questao(exame_id, questao_id):
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            return erro_html('Aluno não autenticado', 401)

        modal_requests = session.get('modal_requests', {})
        modal_key = f'{aluno_id}:{exame_id}'
        questoes_abertas = set(modal_requests.get(modal_key, []))
        if questao_id in questoes_abertas:
            return erro_html('Questão já aberta. Não é possível abrir novamente.', 403)
        questoes_abertas.add(questao_id)
        modal_requests[modal_key] = list(questoes_abertas)
        session['modal_requests'] = modal_requests
        
        questao = get_questao_by_id(questao_id)
        if not questao:
            return erro_html('Questão não encontrada', 404)
        
        # Pegar dados da submissão
        submissao_exame = get_submissoes_exame_by_exame_aluno(exame_id, aluno_id)
        respostas_existentes = {}
        if submissao_exame:
            submissoes = get_submissoes_questao_by_submissao(submissao_exame['id'])
            for sub in submissoes:
                respostas_existentes[sub['questao_id']] = sub.get('resposta', '')
        
        # Preparar dados do modal
        tipo_info = get_tipo_questao_by_id(questao.get('tipo_questao_id'))
        input_file = tipo_info.get('input_file', 'text').lower() if tipo_info else 'text'
        multiplas_respostas = bool(tipo_info.get('multiplas_respostas', False)) if tipo_info else False
        respostas = get_respostas_by_questao(questao_id)
        opcoes = respostas[0].get('opcoes', []) if respostas else []
        resposta_atual = respostas_existentes.get(questao_id, '')
        read_only = questao_id in respostas_existentes

        modal_html = build_modal_questao_html(exame_id, questao, resposta_atual, opcoes, input_file, multiplas_respostas, read_only)
        return modal_html
    except Exception as e:
        import traceback
        traceback.print_exc()
        return erro_500(e)

@exame_aluno_route.route('/')
def redirect_exame():
    return redirect('/exame-aluno/lista')

@exame_aluno_route.route('/lista')
def lista_exames():
    try:
        exames = get_exames()
        exames = [e for e in exames if e.get('publico', False)]
        return render_lista_exames(exames)
    except Exception as e:
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)

@exame_aluno_route.route('/visualizar/<int:exame_id>')
def visualizar_exame(exame_id):
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            content, status = erro_html('Aluno não autenticado', 401)
            return render_base_with_content(content, status)
        
        exame = get_exame_by_id(exame_id)
        if not exame:
            content, status = erro_html('Exame não encontrado', 200)
            return render_base_with_content(content, status)
        
        # Verificar se já existe submissão
        submissao_exame = get_submissoes_exame_by_exame_aluno(exame_id, aluno_id)
        
        questoes = get_questoes_by_exame(exame_id)
        
        # Calcular informações de tempo
        duracao_min = exame.get('duracao_minutos', 60)
        data_inicio_exame = exame.get('data_hora_inicio', '')
        dt_inicio_exame = datetime.fromisoformat(data_inicio_exame) if data_inicio_exame else None
        
        # Verificar estado da submissão
        if submissao_exame:
            estado = submissao_exame.get('estado', 'em_andamento')
            
            if estado == 'finalizado':
                return visualizar_exame_finalizado(exame_id, aluno_id)
            
            # Submissão em andamento
            data_inicio_str = submissao_exame.get('data_hora_inicio', '')
            if data_inicio_str:
                data_inicio = datetime.fromisoformat(data_inicio_str)
                data_fim_prevista = data_inicio + timedelta(minutes=duracao_min)
                tempo_restante_sec = int((data_fim_prevista - datetime.now()).total_seconds())
                tempo_restante_min = max(0, tempo_restante_sec // 60)
                tempo_restante_text = f"{tempo_restante_min} minutos"
                fim_previsto = data_fim_prevista.strftime('%H:%M:%S')
                if tempo_restante_sec <= 0:
                    update_submissao_exame_fim(submissao_exame['id'])
                    return redirect(f'/exame-aluno/visualizar/{exame_id}')
            else:
                tempo_restante_text = f"{duracao_min} minutos"
                fim_previsto = "-"
        else:
            # Novo exame
            tempo_restante_text = f"{duracao_min} minutos"
            fim_previsto = "-"
        
        # Bloquear início antecipado
        guard_html = build_exame_guard()
        if not submissao_exame and dt_inicio_exame and datetime.now() < dt_inicio_exame:
            data_fim_prevista = dt_inicio_exame + timedelta(minutes=duracao_min)
            fim_previsto = data_fim_prevista.strftime('%d/%m/%Y %H:%M')
            tempo_restante_text = 'Aguardando início'
            header = build_exame_header(exame, duracao_min, fim_previsto, tempo_restante_text)
            aviso = '<div class="alert alert-info">O exame ainda não foi iniciado. Aguarde o horário de início.</div>'
            content = header + guard_html + Markup(aviso)
            return render_base_with_content(content, 200)

        header = build_exame_header(exame, duracao_min, fim_previsto, tempo_restante_text)

        # Se não iniciou ainda, mostrar botão de início
        if not submissao_exame:
            inicio_html = build_inicio_exame(exame_id)
            content = header + guard_html + inicio_html
            return render_base_with_content(content, 200)
        
        # Construir tabela de questões
        # Pegar respostas já submetidas
        respostas_existentes = {}
        if submissao_exame:
            submissoes = get_submissoes_questao_by_submissao(submissao_exame['id'])
            for sub in submissoes:
                respostas_existentes[sub['questao_id']] = sub.get('resposta', '')

        tabela_html = build_tabela_questoes(exame_id, questoes, respostas_existentes)
        footer = build_footer_finalizar(exame_id)

        content = header + guard_html + tabela_html + footer

        return render_base_with_content(content, 200)
    except Exception as e:
        traceback.print_exc()
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)

@exame_aluno_route.route('/iniciar/<int:exame_id>', methods=['POST'])
def iniciar_exame(exame_id):
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            return erro_html('Aluno não autenticado', 401)
        
        resultado = add_submissao_exame(exame_id, aluno_id)
        
        if resultado['ok']:
            return redirect(f'/exame-aluno/visualizar/{exame_id}')
        
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

@exame_aluno_route.route('/responder/<int:exame_id>/<int:questao_id>', methods=['POST'])
def responder_questao(exame_id, questao_id):
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            return erro_html('Aluno não autenticado', 401)

        payload = request.get_json(silent=True) if request.is_json else None
        if payload is None:
            resposta_list = request.form.getlist('resposta')
            resposta = resposta_list if len(resposta_list) > 1 else request.form.get('resposta', '')
            justificacao = request.form.get('justificacao', '')
        else:
            resposta = payload.get('resposta', '')
            justificacao = payload.get('justificacao', '')

        if resposta == 'true':
            resposta = 'Verdadeiro'
        elif resposta == 'false':
            resposta = 'Falso'

        if justificacao and resposta == 'Falso':
            resposta = justificacao

        resposta_para_salvar = resposta
        if isinstance(resposta, list):
            resposta_para_salvar = json.dumps(resposta)
        
        # Pegar a submissão de exame do aluno
        submissao_exame = get_submissoes_exame_by_exame_aluno(exame_id, aluno_id)
        
        if not submissao_exame:
            return erro_html('Erro: Submissão não encontrada', 400)

        submissoes_existentes = get_submissoes_questao_by_submissao(submissao_exame['id'])
        if any(sub.get('questao_id') == questao_id for sub in submissoes_existentes):
            return '<div class="alert alert-warning">Questão já respondida. Não é possível alterar.</div>', 403

        # Bloquear se exame já finalizado
        if submissao_exame.get('estado') == 'finalizado':
            return '<div class="alert alert-warning">Exame finalizado. Não é possível responder.</div>', 403

        # Bloquear se tempo expirou
        data_inicio_str = submissao_exame.get('data_hora_inicio', '')
        if data_inicio_str:
            data_inicio = datetime.fromisoformat(data_inicio_str)
            exame_info = get_exame_by_id(exame_id)
            duracao_min = exame_info.get('duracao_minutos', 0) if exame_info else 0
            data_fim_prevista = data_inicio + timedelta(minutes=duracao_min)
            if datetime.now() > data_fim_prevista:
                update_submissao_exame_fim(submissao_exame['id'])
                return '<div class="alert alert-warning">Tempo do exame terminou.</div>', 403
        
        # Verificar se correção automática é ativada
        questao = get_questao_by_id(questao_id)
        if not questao:
            return erro_html('Questão não encontrada', 404)

        tipo_info = get_tipo_questao_by_id(questao.get('tipo_questao_id'))
        correcao_automatica = tipo_info.get('correcao_automatica', True) if tipo_info else True
        
        pontuacao = 0
        if correcao_automatica:
            respostas_db = get_respostas_by_questao(questao_id)
            if respostas_db:
                resposta_correta = respostas_db[0].get('opcao_correta')
                try:
                    if isinstance(resposta, list):
                        if isinstance(resposta_correta, str):
                            resposta_correta = json.loads(resposta_correta)
                        if isinstance(resposta_correta, list) and sorted(resposta) == sorted(resposta_correta):
                            pontuacao = questao.get('pontuacao_maxima', 1)
                    else:
                        if resposta == resposta_correta:
                            pontuacao = questao.get('pontuacao_maxima', 1)
                except Exception:
                    if resposta == resposta_correta:
                        pontuacao = questao.get('pontuacao_maxima', 1)
        
        # Usar a função de submissão de questão que trata atualizações
        resultado = add_submissao_questao(submissao_exame['id'], questao_id, resposta_para_salvar, pontuacao=pontuacao)
        
        if not resultado['ok']:
            return erro_html(resultado.get('erro', 'Erro desconhecido'), 400)
        
        if request.is_json:
            return build_linha_questao(exame_id, questao, True)

        return redirect(f'/exame-aluno/visualizar/{exame_id}')
    except Exception as e:
        import traceback
        traceback.print_exc()
        return erro_500(e)

@exame_aluno_route.route('/finalizar/<int:exame_id>', methods=['POST'])
def finalizar_exame(exame_id):
    try:
        aluno_id = obter_aluno_id()
        if not aluno_id:
            return erro_html('Aluno não autenticado', 401)
        
        # Pegar submissão de exame
        submissao_exame = get_submissoes_exame_by_exame_aluno(exame_id, aluno_id)
        
        if not submissao_exame:
            return jsonify({'ok': False, 'erro': 'Submissão não encontrada'}), 404
        
        resultado = update_submissao_exame_fim(submissao_exame['id'])
        
        if resultado['ok']:
            return redirect(f'/exame-aluno/visualizar/{exame_id}')
        
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

def visualizar_exame_finalizado(exame_id, aluno_id):
    try:
        exame = get_exame_by_id(exame_id)
        if not exame:
            content, status = erro_html('Exame não encontrado', 200)
            return render_base_with_content(content, status)
        questoes = get_questoes_by_exame(exame_id)
        
        # Pegar submissão do exame
        submissao_exame = get_submissoes_exame_by_exame_aluno(exame_id, aluno_id)
        
        # Mapear respostas
        respostas_map = {}
        if submissao_exame:
            submissoes = get_submissoes_questao_by_submissao(submissao_exame['id'])
            respostas_map = {sub['questao_id']: sub.get('resposta', '') for sub in submissoes}
        
        total_pontos = 0
        total_max = 0
        sub_itens = get_submissoes_questao_by_submissao(submissao_exame['id']) if submissao_exame else []
        
        for questao in questoes:
            questao_id = questao['id']
            total_max += questao.get('pontuacao_maxima', 0) or 0
            for sub in sub_itens:
                if sub.get('questao_id') == questao_id:
                    total_pontos += sub.get('pontuacao_atribuida', 0) or 0
                    break
        
        fim_previsto = '-'
        if submissao_exame:
            data_inicio_str = submissao_exame.get('data_hora_inicio', '')
            data_fim_str = submissao_exame.get('data_hora_fim', '')
            if data_fim_str:
                fim_previsto = datetime.fromisoformat(data_fim_str).strftime('%d/%m/%Y %H:%M')
            elif data_inicio_str:
                data_inicio = datetime.fromisoformat(data_inicio_str)
                data_fim_prevista = data_inicio + timedelta(minutes=exame.get('duracao_minutos', 60))
                fim_previsto = data_fim_prevista.strftime('%d/%m/%Y %H:%M')

        content = build_exame_finalizado_content(
            exame,
            questoes,
            sub_itens,
            respostas_map,
            total_pontos,
            total_max,
            fim_previsto
        )
        return render_base_with_content(content, 200)
    except Exception as e:
        content, status = erro_html(f'Erro: {str(e)}', 500)
        return render_base_with_content(content, status)
