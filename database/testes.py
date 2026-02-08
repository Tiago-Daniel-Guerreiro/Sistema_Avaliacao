import json

def adicionar_dados_teste(cursor):
    cursor.execute("SELECT COUNT(*) as count FROM contas")
    if cursor.fetchone()['count'] > 0:
        return

    cursor.execute("""
        INSERT INTO contas (nome, email, id_cargo, senha) VALUES 
        ('1', '1@1', 1, '1'),
        ('2', '2@2', 2, '2'),
        ('3', '3@3', 3, '3'),
        ('4', '4@4', 3, '4'),
        ('5', '5@5', 3, '5'),
        ('6', '6@6', 3, '6'),
        ('7', '7@7', 3, '7')
    """)

    cursor.execute("""
        INSERT INTO disciplinas (nome, codigo) VALUES 
        ('Matemática', 'MAT'),
        ('Física', 'FIS'),
        ('Português', 'POR'),
        ('Química', 'QUI')
    """)

    cursor.execute("""
        INSERT INTO turmas (ano, identificador) VALUES 
        (12, 'A'),
        (12, 'B'),
        (11, 'A'),
        (11, 'B')
    """)

    cursor.execute("SELECT id FROM contas WHERE email = '2@2'")
    prof_id = cursor.fetchone()['id']
    
    conta_ids = {}
    for i in range(3, 8):
        cursor.execute(f"SELECT id FROM contas WHERE email = '{i}@{i}'")
        conta_ids[i] = cursor.fetchone()['id']

    cursor.execute("SELECT id FROM turmas WHERE ano = 12 AND identificador = 'A'")
    turma_12a = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM turmas WHERE ano = 12 AND identificador = 'B'")
    turma_12b = cursor.fetchone()['id']

    cursor.execute("SELECT id FROM disciplinas WHERE nome = 'Matemática'")
    disc_mat = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM disciplinas WHERE nome = 'Física'")
    disc_fis = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM disciplinas WHERE nome = 'Português'")
    disc_por = cursor.fetchone()['id']

    cursor.execute("""
        INSERT INTO alunos (identificador, turma_id, id_conta) VALUES 
        ('ALU-12A-001', ?, ?),
        ('ALU-12A-002', ?, ?),
        ('ALU-12A-003', ?, ?),
        ('ALU-12B-001', ?, ?),
        ('ALU-12B-002', ?, ?)
    """, (turma_12a, conta_ids[3], turma_12a, conta_ids[4], turma_12a, conta_ids[5], 
          turma_12b, conta_ids[6], turma_12b, conta_ids[7]))

    cursor.execute("""
        INSERT INTO disciplina_turma (turma_id, disciplina_id, professor_id) VALUES 
        (?, ?, ?),
        (?, ?, ?),
        (?, ?, ?)
    """, (turma_12a, disc_mat, prof_id, turma_12a, disc_fis, prof_id, turma_12b, disc_por, prof_id))

    # Obter IDs de disciplina_turma
    cursor.execute("SELECT id FROM disciplina_turma WHERE turma_id = ? AND disciplina_id = ?", (turma_12a, disc_mat))
    dt_mat_12a = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM disciplina_turma WHERE turma_id = ? AND disciplina_id = ?", (turma_12a, disc_fis))
    dt_fis_12a = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM disciplina_turma WHERE turma_id = ? AND disciplina_id = ?", (turma_12b, disc_por))
    dt_por_12b = cursor.fetchone()['id']

    # Criar exames
    cursor.execute("""
        INSERT INTO exames (disciplina_turma_id, titulo, data_hora_inicio, duracao_minutos) VALUES 
        (?, 'Prova de Matemática - Capítulo 1', '2026-02-01T10:00', 60),
        (?, 'Mini-Teste Física', '2026-02-02T09:30', 30),
        (?, 'Exame de Física - Mecânica', '2026-02-10T14:00', 90),
        (?, 'Teste de Português - Gramática', '2026-02-15T11:00', 45)
    """, (dt_mat_12a, dt_fis_12a, dt_fis_12a, dt_por_12b))

    # Obter IDs dos exames
    cursor.execute("SELECT id FROM exames WHERE titulo LIKE '%Matemática%'")
    exame_mat = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM exames WHERE titulo LIKE '%Mini-Teste%'")
    exame_fis_mini = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM exames WHERE titulo LIKE '%Mecânica%'")
    exame_fis_mec = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM exames WHERE titulo LIKE '%Gramática%'")
    exame_por = cursor.fetchone()['id']

    # Obter tipos de questão
    cursor.execute("SELECT id FROM tipos_questao WHERE nome = 'text'")
    tipo_text = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM tipos_questao WHERE nome = 'choices'")
    tipo_choices = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM tipos_questao WHERE nome = 'true_false'")
    tipo_tf = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM tipos_questao WHERE nome = 'true_false_justificado'")
    tipo_tf_just = cursor.fetchone()['id']

    # Criar questões para Matemática (apenas choices e true_false com correção automática)
    cursor.execute("""
        INSERT INTO questoes (texto, tipo_questao_id, exame_id, numero_questao, pontuacao_maxima) VALUES
        ('Quanto é 2 + 2?', ?, ?, 1, 2.5),
        ('O número π é um número racional?', ?, ?, 2, 2.0)
    """, (tipo_choices, exame_mat, 
          tipo_tf, exame_mat))

    # Criar questões para Física (mini-teste)
    cursor.execute("""
        INSERT INTO questoes (texto, tipo_questao_id, exame_id, numero_questao, pontuacao_maxima) VALUES
        ('Qual a unidade de força no SI?', ?, ?, 1, 3.0),
        ('A velocidade é uma grandeza vetorial?', ?, ?, 2, 3.5)
    """, (tipo_choices, exame_fis_mini, 
          tipo_tf, exame_fis_mini))

    # Criar questões para Física (mecânica)
    cursor.execute("""
        INSERT INTO questoes (texto, tipo_questao_id, exame_id, numero_questao, pontuacao_maxima) VALUES
        ('Qual o trabalho realizado por uma força de 50N que desloca um objeto 4m?', ?, ?, 1, 2.5),
        ('A energia mecânica de um sistema isolado é conservada?', ?, ?, 2, 2.0)
    """, (tipo_choices, exame_fis_mec, 
          tipo_tf, exame_fis_mec))

    # Criar questões para Português
    cursor.execute("""
        INSERT INTO questoes (texto, tipo_questao_id, exame_id, numero_questao, pontuacao_maxima) VALUES
        ('Qual a classe gramatical de "rapidamente"?', ?, ?, 1, 3.0)
    """, (tipo_choices, exame_por,))

    # Obter questões criadas
    cursor.execute("SELECT id FROM questoes WHERE exame_id = ? ORDER BY numero_questao", (exame_mat,))
    questoes_mat = [row['id'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM questoes WHERE exame_id = ? ORDER BY numero_questao", (exame_fis_mini,))
    questoes_fis_mini = [row['id'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM questoes WHERE exame_id = ? ORDER BY numero_questao", (exame_fis_mec,))
    questoes_fis_mec = [row['id'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM questoes WHERE exame_id = ? ORDER BY numero_questao", (exame_por,))
    questoes_por = [row['id'] for row in cursor.fetchall()]

    # Obter alunos
    cursor.execute("SELECT id FROM alunos WHERE identificador = 'ALU-12A-001'")
    aluno1 = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM alunos WHERE identificador = 'ALU-12A-002'")
    aluno2 = cursor.fetchone()['id']
    cursor.execute("SELECT id FROM alunos WHERE identificador = 'ALU-12A-003'")
    aluno3 = cursor.fetchone()['id']

    # Criar submissões para Matemática
    cursor.execute("""
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, corrigido_professor) VALUES
        (?, ?, ?, '4', '2026-02-01T10:15', 2.5, 0),
        (?, ?, ?, 'false', '2026-02-01T10:35', 0, 0)
    """, (exame_mat, aluno1, questoes_mat[0], 
          exame_mat, aluno1, questoes_mat[1]))

    cursor.execute("""
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, corrigido_professor) VALUES
        (?, ?, ?, '3', '2026-02-01T10:20', 0, 0),
        (?, ?, ?, 'true', '2026-02-01T10:40', 0, 0)
    """, (exame_mat, aluno2, questoes_mat[0], 
          exame_mat, aluno2, questoes_mat[1]))

    cursor.execute("""
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, corrigido_professor) VALUES
        (?, ?, ?, '4', '2026-02-01T11:05', 2.5, 0),
        (?, ?, ?, 'true', '2026-02-01T11:15', 2.0, 0)
    """, (exame_mat, aluno3, questoes_mat[0], 
          exame_mat, aluno3, questoes_mat[1]))

    # Criar submissões para Física (mini-teste)
    cursor.execute("""
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, corrigido_professor) VALUES
        (?, ?, ?, 'Newton', '2026-02-02T09:40', 3.0, 0),
        (?, ?, ?, 'true', '2026-02-02T09:50', 3.5, 0)
    """, (exame_fis_mini, aluno1, questoes_fis_mini[0], 
          exame_fis_mini, aluno1, questoes_fis_mini[1]))

    cursor.execute("""
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, corrigido_professor) VALUES
        (?, ?, ?, 'Joule', '2026-02-02T09:45', 0, 0)
    """, (exame_fis_mini, aluno2, questoes_fis_mini[0]))

    # Criar submissões para Física (mecânica)
    cursor.execute("""
        INSERT INTO submissoes (exame_id, aluno_id, questao_id, resposta, data_hora_resposta, pontuacao_atribuida, corrigido_professor) VALUES
        (?, ?, ?, '200 J', '2026-02-10T14:30', 2.5, 0),
        (?, ?, ?, 'true', '2026-02-10T14:45', 2.0, 0)
    """, (exame_fis_mec, aluno1, questoes_fis_mec[0], 
          exame_fis_mec, aluno1, questoes_fis_mec[1]))

    # Criar respostas (opções de teste) para questões de escolha múltipla
    cursor.execute("""
        INSERT INTO respostas (questao_id, opcoes, opcao_correta) VALUES 
        (?, ?, ?),
        (?, ?, ?),
        (?, ?, ?),
        (?, ?, ?)
    """, (questoes_mat[0], json.dumps(['2', '3', '4', '5']), '4',
          questoes_mat[1], json.dumps(['true', 'false']), 'false',
          questoes_fis_mini[0], json.dumps(['Joule', 'Newton', 'Watt', 'Pascal']), 'Newton',
          questoes_fis_mini[1], json.dumps(['true', 'false']), 'true'))

    cursor.execute("""
        INSERT INTO respostas (questao_id, opcoes, opcao_correta) VALUES 
        (?, ?, ?),
        (?, ?, ?)
    """, (questoes_fis_mec[0], json.dumps(['100 J', '150 J', '200 J', '250 J']), '200 J',
          questoes_fis_mec[1], json.dumps(['true', 'false']), 'true'))

    cursor.execute("""
        INSERT INTO respostas (questao_id, opcoes, opcao_correta) VALUES 
        (?, ?, ?)
    """, (questoes_por[0], json.dumps(['Adjetivo', 'Advérbio', 'Substantivo', 'Verbo']), 'Advérbio'))

