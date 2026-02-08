from .tipos_questao import get_tipo_questao_by_input_file
import json
from .contas import add_conta, get_conta_by_email
from .disciplina import add_disciplina
from .turma import add_turma
from .disciplina_turma import add_disciplina_turma
from .aluno import add_aluno
from .exame import add_exame
from .questao import add_questao
from .resposta import add_resposta
from .tipos_questao import add_tipo_questao_or_get, get_tipo_questao_by_nome


def adicionar_dados_extras():
    print("Adicionando tipos de questao extras...")
    tipos_extras = [
        ('text', 'Texto', False, False, False),
        ('email', 'Email', False, False, False),
        ('number', 'Número', False, False, False),
        ('number', 'Número (com validação)', False, True, False),  # Variação com validação
        ('number_multi', 'Número (múltiplas respostas)', True, False, True),
        ('password', 'Senha', False, False, False),
        ('textarea', 'Área de texto', False, False, False),
        ('datetime', 'Dia e hora', False, False, False),
        ('time', 'Hora', False, False, False),
        ('hidden', 'Escondido', False, False, False),
        ('choices', 'Opções (única resposta)', True, True, False),
        ('choices', 'Opções (múltiplas respostas)', True, True, True),
        ('select', 'Selecionado (única)', True, True, False),
        ('true_false', 'Verdadeiro ou Falso', True, True, False),
        ('true_false_justificado', 'Verdadeiro ou Falso justificado', True, False, False),
    ]
    
    tipos_map = {}  # Mapear nome para tipo_questao
    for input_file, nome, list_options, correcao_automatica, multiplas_respostas in tipos_extras:
        resultado = add_tipo_questao_or_get(input_file, nome, list_options, correcao_automatica, multiplas_respostas)
        if resultado['ok']:
            tipos_map[input_file] = resultado['tipo_questao']  # Usar input_file como chave
            print(f"  [OK] Tipo '{nome}' (input_file='{input_file}') adicionado/obtido")
    
    # 2. Usar roles existentes (admin, professor, aluno)
    print("\nUsando roles existentes...")
    # Os roles sao criados por padrao durante inicializacao
    # Admin=1, Professor=2, Aluno=3
    admin_role_id = 1
    professor_role_id = 2
    aluno_role_id = 3
    print(f"  [OK] Role 'Admin': {admin_role_id}")
    print(f"  [OK] Role 'Professor': {professor_role_id}")
    print(f"  [OK] Role 'Aluno': {aluno_role_id}")
    
    # 3. Adicionar contas
    print("\nAdicionando contas...")
    admin_conta = add_conta('Admin Extra', '1@1', admin_role_id, '1')
    admin_conta_id = admin_conta['conta']['id'] if admin_conta['ok'] else None
    print(f"  [OK] Conta Admin: {admin_conta_id}" if admin_conta_id else "  Conta Admin ja existe")
    
    prof_conta = add_conta('Prof. Joao Extra', '2@2', professor_role_id, '2')
    prof_conta_id = prof_conta['conta']['id'] if prof_conta['ok'] else None
    print(f"  [OK] Conta Professor: {prof_conta_id}" if prof_conta_id else "  Conta Professor ja existe")
    
    # Adicionar contas de alunos
    aluno_contas = []
    for i in range(3, 9):
        aluno_result = add_conta(f'Aluno Extra {i}', f'{i}@{i}', aluno_role_id, f'{i}')
        if aluno_result['ok']:
            aluno_contas.append(aluno_result['conta'])
            print(f"  [OK] Conta Aluno {i}: {aluno_result['conta']['id']}")
        else:
            print(f"  Conta Aluno {i} ja existe")
    
    # 4. Adicionar disciplina
    print("\nAdicionando disciplina...")
    disc_result = add_disciplina('Programacao Web Extra', 'WEB101-EXT')
    disc_id = disc_result['disciplina']['id'] if disc_result['ok'] else None
    print(f"  [OK] Disciplina: {disc_id}" if disc_id else "  Disciplina ja existe")
    
    # 5. Adicionar turma
    print("\nAdicionando turma...")
    turma_result = add_turma(9, 'A-Extra')
    turma_id = turma_result['turma']['id'] if turma_result['ok'] else None
    print(f"  [OK] Turma: {turma_id}" if turma_id else "  Turma ja existe")
    
    # 6. Vincular disciplina a turma
    print("\nVinculando disciplina a turma...")
    disciplina_turma_id = None
    if disc_id and turma_id and prof_conta_id:
        dt_result = add_disciplina_turma(disc_id, turma_id, prof_conta_id)
        if dt_result['ok']:
            disciplina_turma_id = dt_result['disciplina_turma']['id']
            print(f"  [OK] Disciplina-Turma vinculada (ID: {disciplina_turma_id})")
        else:
            print(f"  Disciplina-Turma ja vinculada")
    
    # 7. Adicionar alunos
    print("\nAdicionando alunos...")
    aluno_ids = []
    for i, aluno_conta in enumerate(aluno_contas, 3):
        aluno_result = add_aluno(f'ALU-EXT-{i:03d}', turma_id, aluno_conta['id'])
        if aluno_result['ok']:
            aluno_ids.append(aluno_result['aluno']['id'])
            print(f"  [OK] Aluno {i}: {aluno_result['aluno']['id']}")
        else:
            print(f"  Aluno {i} ja existe")
    
    # 8. Adicionar exame
    print("\nAdicionando exame...")
    exame_id = None
    if disciplina_turma_id:
        exame_result = add_exame(disciplina_turma_id, 'Exame Extra de Programacao', '2025-02-15 10:00:00', 120)
        exame_id = exame_result['exame']['id'] if exame_result['ok'] else None
        print(f"  [OK] Exame: {exame_id}" if exame_id else "  Exame ja existe")
    else:
        print(f"  Nao foi possivel criar exame: disciplina_turma_id ausente")
    
    # 9. Adicionar questoes com respostas
    if exame_id:
        print("\nAdicionando questoes e respostas...")
        questoes_config = [
            {
                'tipo_input_file': 'text',
                'texto': 'Qual e a capital de Portugal?',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None
            },
            {
                'tipo_input_file': 'email',
                'texto': 'Qual e seu email de contato?',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None
            },
            {
                'tipo_input_file': 'number',
                'texto': 'Quantos anos tem a empresa? (sem validacao)',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None,
                'nome_especifico': 'Número'
            },
            {
                'tipo_input_file': 'number',
                'texto': 'Qual a sua idade? (com validacao)',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None,
                'nome_especifico': 'Número (com validação)'
            },
            {
                'tipo_input_file': 'number_multi',
                'texto': 'Informe três valores numéricos (múltiplas respostas)',
                'pontuacao': 2.0,
                'opcoes': ['1', '2', '3'],
                'opcao_correta': json.dumps(['1', '2'])
            },
            {
                'tipo_input_file': 'password',
                'texto': 'Qual e sua senha de acesso?',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None
            },
            {
                'tipo_input_file': 'textarea',
                'texto': 'Descreva sua experiencia com programacao web.',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None
            },
            {
                'tipo_input_file': 'datetime',
                'texto': 'Quando voce comecou a programar?',
                'pontuacao': 1.0,
                'opcoes': [],
                'opcao_correta': None
            },
            {
                'tipo_input_file': 'hidden',
                'texto': 'Campo oculto para dados internos',
                'pontuacao': 0.0,
                'opcoes': [],
                'opcao_correta': 'valor-oculto'
            },
            {
                'tipo_input_file': 'choices',
                'texto': 'Qual e a melhor linguagem para web? (unica resposta)',
                'pontuacao': 1.0,
                'opcoes': ['Python', 'JavaScript', 'PHP', 'Ruby'],
                'opcao_correta': 'JavaScript',
                'nome_especifico': 'Opções (única resposta)'
            },
            {
                'tipo_input_file': 'choices',
                'texto': 'Qual das seguintes sao linguagens de backend?',
                'pontuacao': 2.0,
                'opcoes': ['Python', 'JavaScript', 'CSS', 'Java', 'C#'],
                'opcao_correta': json.dumps(['Python', 'JavaScript', 'Java', 'C#']),
                'nome_especifico': 'Opções (múltiplas respostas)'
            },
            {
                'tipo_input_file': 'select',
                'texto': 'Escolha seu nivel de experiencia (unico):',
                'pontuacao': 1.0,
                'opcoes': ['Iniciante', 'Intermediario', 'Avancado'],
                'opcao_correta': 'Intermediario',
                'nome_especifico': 'Selecionado (única)'
            },
            {
                'tipo_input_file': 'true_false',
                'texto': 'Python e uma linguagem de tipagem forte?',
                'pontuacao': 1.0,
                'opcoes': ['Verdadeiro', 'Falso'],
                'opcao_correta': 'Falso'
            },
            {
                'tipo_input_file': 'true_false_justificado',
                'texto': 'HTML e uma linguagem de programacao.',
                'pontuacao': 1.0,
                'opcoes': ['Verdadeiro', 'Falso'],
                'opcao_correta': None
            },
            
        ]
        
        for i, config in enumerate(questoes_config, 1):
            # Obter tipo de questao
            tipo_input_file = config['tipo_input_file']
            
            # Se houver um nome especifico, buscar esse tipo especifico
            if 'nome_especifico' in config:
                tipo_questao = get_tipo_questao_by_nome(config['nome_especifico'])
            else:
                # Se nao, buscar o primeiro tipo com esse input_file
                tipos_candidatos = get_tipo_questao_by_input_file(tipo_input_file)
                tipo_questao = tipos_candidatos[0] if tipos_candidatos else None
            
            if not tipo_questao:
                print(f"  Tipo de questao '{tipo_input_file}' nao encontrado")
                continue
            
            # Adicionar questao
            q_result = add_questao(
                exame_id,
                i,  # numero_questao
                tipo_questao['id'],
                config['texto'],
                config['pontuacao']
            )
            
            if q_result['ok']:
                questao_id = q_result['questao']['id']
                
                # Adicionar resposta
                opcoes_json = json.dumps(config['opcoes']) if config['opcoes'] else json.dumps([])
                opcao_correta_value = config['opcao_correta']
                
                resp_result = add_resposta(questao_id, opcoes_json, opcao_correta_value)
                if resp_result['ok']:
                    nome_tipo = tipo_questao.get('nome', tipo_input_file)
                    print(f"  [OK] Questao {i} ({nome_tipo}): {questao_id}")
    
    print("\n[OK] Dados extras adicionados com sucesso!")
