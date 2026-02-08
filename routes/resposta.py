from flask import Blueprint, request
import json
from database.resposta import get_respostas, get_resposta_by_id, get_respostas_by_questao, add_resposta, update_resposta, delete_resposta
from database.questao import get_questao_by_id, get_questoes, get_questoes_by_exame
from database.tipos_questao import get_tipos_questao, get_tipo_questao_by_id
from utils.template_builder import TableBuilder
from utils.permissions import obter_cargo_usuario, Cargo, obter_div_acesso_negado, get_request_data, erro_500, erro_html
from ui.resposta import (
    render_page_resposta,
    build_table_resposta,
    build_modal_edicao_resposta,
    build_modal_delete_resposta,
    render_linha_resposta
)

resposta_route = Blueprint('resposta', __name__, url_prefix='/resposta')


@resposta_route.route('/tipo-questao/<int:questao_id>')
def tipo_questao(questao_id):
    try:
        questao = get_questao_by_id(questao_id)
        
        if not questao:
            return {'ok': False, 'erro': 'Questão não encontrada'}, 404
        
        # Pegar o tipo de questão da DB
        tipo_id = questao.get('tipo_questao_id')
        tipo_info = get_tipo_questao_by_id(tipo_id) if tipo_id else None
        
        if not tipo_info:
            return {'ok': False, 'erro': 'Tipo de questão não encontrado'}, 404
        
        return {
            'ok': True,
            'tipo_nome': tipo_info.get('nome'),
            'edit': bool(tipo_info.get('edit', False))
        }, 200
        
    except Exception as e:
        return {'ok': False, 'erro': str(e)}, 500


@resposta_route.route('/')
def page_resposta():
    return render_page_resposta(table_resposta())

@resposta_route.route('/table')
def table_resposta():
    try:
        cargo = obter_cargo_usuario()
        
        if cargo == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        respostas = get_respostas()
        
        return build_table_resposta(respostas)
        
    except Exception as e:
        return erro_500(e)

@resposta_route.route('/<int:resposta_id>/modal/edicao')
def modal_edicao_resposta(resposta_id):
    try:
        resposta = get_resposta_by_id(resposta_id)
        
        if not resposta:
            return erro_html('Resposta não encontrada', 200)
        
        questao = get_questao_by_id(resposta.get('questao_id'))
        tipo_id = questao.get('tipo_questao_id')
        tipo_info = get_tipo_questao_by_id(tipo_id)
        
        if not tipo_info:
            return erro_html('Tipo de questão não encontrado', 200)
        
        return build_modal_edicao_resposta(resposta, questao, tipo_info)
        
    except Exception as e:
        return erro_500(e)

@resposta_route.route('/<int:resposta_id>/modal/delete')
def modal_delete_resposta(resposta_id):
    try:
        resposta = get_resposta_by_id(resposta_id)
        
        if not resposta:
            return erro_html('Resposta não encontrada', 200)
        
        return build_modal_delete_resposta(resposta)
        
    except Exception as e:
        return erro_500(e)

@resposta_route.route('/', methods=['POST'])
def criar_resposta():
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        questao_id = int(dados.get('questao_id'))
        questao = get_questao_by_id(questao_id)
        
        if not questao:
            return {'ok': False, 'erro': 'Questão não encontrada'}, 404
        
        # Criar resposta vazia
        resultado = add_resposta(questao_id=questao_id, opcoes=[])
        
        if resultado['ok']:
            resposta = resultado['resposta']
            # Retornar JSON com URL do modal de edição
            return {
                'ok': True,
                'resposta_id': resposta['id'],
                'modal_url': f'/resposta/{resposta["id"]}/modal/edicao'
            }, 200
        
        return {'ok': False, 'erro': resultado.get("erro", "Erro")}, 400
        
    except Exception as e:
        return {'ok': False, 'erro': str(e)}, 500

@resposta_route.route('/<int:resposta_id>', methods=['PUT'])
def atualizar_resposta(resposta_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        dados = get_request_data()
        resposta = get_resposta_by_id(resposta_id)
        
        if not resposta:
            return {'ok': False, 'erro': 'Resposta não encontrada'}, 404
        
        # Preparar opções - preservar existentes se não forem enviadas
        opcoes = resposta.get('opcoes', [])  # Usar opções existentes como padrão
        if 'opcoes' in dados:
            opcoes_str = dados.get('opcoes', '[]')
            try:
                if isinstance(opcoes_str, str):
                    opcoes = json.loads(opcoes_str) if opcoes_str else opcoes
                else:
                    opcoes = opcoes_str
            except:
                opcoes = resposta.get('opcoes', [])
        
        # Pegar opção correta se existir
        opcao_correta = dados.get('opcao_correta', '')
        
        # Atualizar resposta
        resultado = update_resposta(
            resposta_id=resposta_id,
            opcoes=opcoes if opcoes else [],
            opcao_correta=opcao_correta if opcao_correta else None
        )
        
        if resultado['ok']:
            resposta = resultado['resposta']
            
            return render_linha_resposta(resposta)
        
        return erro_html('Erro ao atualizar resposta', 200)
        
    except Exception as e:
        return {'ok': False, 'erro': str(e)}, 500

@resposta_route.route('/<int:resposta_id>', methods=['DELETE'])
def deletar_resposta(resposta_id):
    try:
        if obter_cargo_usuario() == Cargo.ALUNO:
            return obter_div_acesso_negado()
        
        resultado = delete_resposta(resposta_id)
        
        if resultado['ok']:
            return {'ok': True}, 200
        
        return {'ok': False, 'erro': 'Resposta não encontrada'}, 200
        
    except Exception as e:
        return erro_500(e)
