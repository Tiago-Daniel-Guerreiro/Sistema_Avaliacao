from flask import render_template
from utils.template_builder import FormBuilder

def render_register_partial():
    form = (FormBuilder(action='/register/', method='post')
        .set_ajax(True)
        .set_c_attrs(c_callback='handleRegister', c_type='json')
        .add_text('nome', 'Nome completo', required=True, placeholder='Seu nome')
        .add_email('email', 'Email', required=True, placeholder='you@exemplo.com')
        .add_password('senha', 'Palavra-passe', required=True, placeholder='••••••••')
    )

    form_data = form.build()

    alerts_html = render_template('componentes/alerts.html', alerts=[
        {'id': 'register-erro', 'type': 'danger', 'hidden': True},
        {'id': 'register-sucesso', 'type': 'success', 'hidden': True}
    ])

    footer_html = render_template('componentes/auth_footer_links.html', links=[
        {'label': 'Já tem conta? Entrar', 'url': '/login/'}
    ])

    script = """
$cruCallback('handleRegister', function(response, form) {
    const erroDiv = document.getElementById('register-erro');
    const sucessoDiv = document.getElementById('register-sucesso');

    erroDiv.classList.add('d-none');
    sucessoDiv.classList.add('d-none');

    if (response.status === 201 && response.data.ok) {
        sucessoDiv.textContent = response.data.mensagem || 'Conta criada com sucesso!';
        sucessoDiv.classList.remove('d-none');

        setTimeout(() => {
            window.location.href = '/login/';
        }, 2000);
    } else {
        erroDiv.textContent = response.data.erro || 'Erro ao criar conta';
        erroDiv.classList.remove('d-none');
    }
});
"""

    return render_template(
        'componentes/auth_card.html',
        title='Sistema de Avaliação',
        subtitle='Criar Conta',
        alerts_html=alerts_html,
        form_open=form_data['open'],
        form_campos=form_data['campos'],
        form_close=form_data['close'],
        submit_label='Criar Conta',
        footer_html=footer_html,
        script=script
    )

def render_register_page():
    return render_template('base.html', content=render_register_partial())
