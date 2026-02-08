from flask import Flask, render_template, jsonify, request, send_from_directory, session
from database.geral import inicializar_database, set_db_file
import os
import sys
from routes.home import home_route
from routes.login import login
from routes.register import register
from routes.forgot_password import forgot_password_route
from routes.contas import contas_route
from routes.turmas import turmas_route
from routes.disciplinas import disciplinas_route
from routes.disciplina_turma import disciplina_turma_route
from routes.exames import exames_route, exame_route
from routes.questoes import questoes_route
from routes.alunos import alunos_route
from routes.exame_aluno import exame_aluno_route
from routes.gestao import gestao_route
from routes.tipos_questao import tipos_questao_route
from routes.cargos import cargos_route
from routes.resposta import resposta_route
from routes.submissao import submissao_route
from utils.permissions import permissions_route

def startup():
    args = {a.lower() for a in sys.argv[1:]}
    test_mode = any(a in {'-teste', '-test', '-debug'} for a in args)
    extras_mode = any(a in {'-extras', '-extra'} for a in args)

    if test_mode:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        test_db = os.path.join(data_dir, 'database_test.db')
        if os.path.exists(test_db):
            os.remove(test_db)
        set_db_file(test_db)
        inicializar_database(test=True)
        print(f"Teste: Database criada: {test_db}")
    elif extras_mode:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        extras_db = os.path.join(data_dir, 'database_extras.db')
        if os.path.exists(extras_db):
            os.remove(extras_db)
        set_db_file(extras_db)
        inicializar_database(test=False, extras=True)
        print(f"Extras: Database criada: {extras_db}")
    else:
        inicializar_database()
        print(f"Database: database.db")

# Inicializar ANTES de criar Flask
startup()

app = Flask(__name__)
app.secret_key = 'Chave-Que-Serve-Para-Criptografar-Sessao'  # Substitua por uma chave segura em produção

app.register_blueprint(home_route)
app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(forgot_password_route)
app.register_blueprint(contas_route)
app.register_blueprint(turmas_route)
app.register_blueprint(disciplinas_route)
app.register_blueprint(disciplina_turma_route)
app.register_blueprint(exames_route)
app.register_blueprint(exame_route)
app.register_blueprint(questoes_route)
app.register_blueprint(alunos_route)
app.register_blueprint(exame_aluno_route)
app.register_blueprint(gestao_route)
app.register_blueprint(tipos_questao_route)
app.register_blueprint(cargos_route)
app.register_blueprint(resposta_route)
app.register_blueprint(submissao_route)
app.register_blueprint(permissions_route)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)