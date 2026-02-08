from flask import Blueprint, request, jsonify
from database.questao import get_questoes, get_questao_by_id, add_questao, update_questao, delete_questao
from database.resposta import get_respostas_by_questao, delete_resposta, add_resposta
from database.exame import get_exames
from database.tipos_questao import get_tipos_questao, get_tipo_questao_by_id
from database.geral import _limpar_resposta_incompativel, _validar_integridade_respostas, _get_connection
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.questoes import (
    render_page_questoes,
    build_table_questoes,
    build_modal_add_questao,
    build_modal_edit_questao,
    build_modal_delete_questao,
    render_linha_questao
)
from ui.exames import build_exame_questao_row

questoes_route = Blueprint('questoes', __name__, url_prefix='/questoes')

@questoes_route.route('/')
def page_questoes():
    return render_page_questoes(table_questoes())

@questoes_route.route('/table')
def table_questoes():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        questoes = get_questoes()
        
        return build_table_questoes(questoes)
        
    except Exception as e:
        return erro_500(e)

@questoes_route.route('/modal/add')
def modal_add_questao():
    try:
        exame_id = request.args.get('exame_id', type=int)

        exames = get_exames()
        tipos = get_tipos_questao()

        return build_modal_add_questao(exames, tipos, exame_id)

    except Exception as e:
        return erro_500(e)

@questoes_route.route('/exame/<int:exame_id>/modal/add')
def modal_add_questao_exame(exame_id):
    try:
        exames = get_exames()
        tipos = get_tipos_questao()

        return build_modal_add_questao(exames, tipos, exame_id)

    except Exception as e:
        return erro_500(e)

@questoes_route.route('/<int:questao_id>/modal/edit')
def modal_edit_questao(questao_id):
    try:
        questao = get_questao_by_id(questao_id)
        
        if not questao:
            return erro_html('Questão não encontrada', 200)
        
        exames = get_exames()
        tipos = get_tipos_questao()
        
        return build_modal_edit_questao(questao, exames, tipos)
        
    except Exception as e:
        return erro_500(e)

@questoes_route.route('/<int:questao_id>/modal/delete')
def modal_delete_questao(questao_id):
    try:
        questao = get_questao_by_id(questao_id)
        
        if not questao:
            return erro_html('Questão não encontrada', 200)
        
        return build_modal_delete_questao(questao)
        
    except Exception as e:
        return erro_500(e)

@questoes_route.route('/', methods=['POST'])
def criar_questao():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        tipo_questao_id = int(dados.get('tipo_questao_id'))
        
        # Criar a questão
        resultado = add_questao(
            exame_id=int(dados.get('exame_id')),
            numero_questao=int(dados.get('numero_questao', 1)),
            tipo_questao_id=tipo_questao_id,
            texto=dados.get('texto'),
            pontuacao_maxima=float(dados.get('pontuacao_maxima', 1))
        )
        
        if resultado['ok']:
            questao = resultado['questao']
            questao_id = questao['id']
            
            # Validar integridade de respostas (cria resposta se necessário)
            conn = _get_connection()
            cursor = conn.cursor()
            _validar_integridade_respostas(cursor)
            conn.commit()
            conn.close()
            
            # Verificar se foi criada uma resposta
            resposta_id = None
            resposta = get_respostas_by_questao(questao_id)
            if resposta:
                resposta_id = resposta[0]['id']
            
            # Retornar resposta em JSON para o callback
            return jsonify({
                'ok': True,
                'questao': questao,
                'resposta_id': resposta_id,
                'html_row': render_linha_questao(questao),
                'html_row_exame': build_exame_questao_row(questao)
            }), 200
        
        return jsonify({
            'ok': False, 
            'erro': resultado.get("erro", "Erro")
        }), 400
        
    except Exception as e:
        return jsonify({
            'ok': False, 
            'erro': str(e)
        }), 500

@questoes_route.route('/<int:questao_id>', methods=['PUT'])
def atualizar_questao(questao_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        
        # Obter o tipo antigo antes de atualizar
        questao_antiga = get_questao_by_id(questao_id)
        tipo_id_anterior = questao_antiga.get('tipo_questao_id') if questao_antiga else None
        tipo_id_novo = int(dados.get('tipo_questao_id'))
        
        # Atualizar a questão
        resultado = update_questao(
            questao_id=questao_id,
            exame_id=int(dados.get('exame_id')),
            numero_questao=int(dados.get('numero_questao', 1)),
            tipo_questao_id=tipo_id_novo,
            texto=dados.get('texto'),
            pontuacao_maxima=float(dados.get('pontuacao_maxima', 1))
        )
        
        if resultado['ok']:
            # Se o tipo mudou, limpar dados incompatíveis da resposta
            if tipo_id_novo != tipo_id_anterior:
                _limpar_resposta_incompativel(questao_id)
            
            # Validar integridade de respostas (criar/eliminar conforme necessário)
            conn = _get_connection()
            cursor = conn.cursor()
            _validar_integridade_respostas(cursor)
            conn.commit()
            conn.close()
            
            questao = resultado['questao']
            
            return render_linha_questao(questao)
        
        return erro_html('Questão não encontrada', 200)
        
    except Exception as e:
        return erro_500(e)

@questoes_route.route('/<int:questao_id>', methods=['DELETE'])
def deletar_questao(questao_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        # Deletar respostas associadas (a cascata no banco também faz isso)
        respostas_existentes = get_respostas_by_questao(questao_id)
        for resposta in respostas_existentes:
            delete_resposta(resposta['id'])
        
        # Deletar a questão
        resultado = delete_questao(questao_id)
        
        if resultado['ok']:
            return '', 200
        
        return erro_html('Questão não encontrada', 200)       
    except Exception as e:
        return erro_500(e)