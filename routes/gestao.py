from flask import Blueprint
from utils.permissions import require_role, Cargo
from ui.gestao import render_page_gestao, render_gestao_content

gestao_route = Blueprint('gestao', __name__, url_prefix='/gestao')

@gestao_route.route('/')
@require_role(Cargo.ADMIN)
def page_gestao():
    return render_page_gestao()

@gestao_route.route('/content')
@require_role(Cargo.ADMIN)
def gestao_content():
    return render_gestao_content()
