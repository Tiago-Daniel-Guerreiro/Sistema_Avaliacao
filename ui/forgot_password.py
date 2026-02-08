from flask import render_template
from utils.template_builder import FormBuilder

def render_forgot_password_partial():
    form = (FormBuilder(action='/forgot-password/', method='post')
        .set_ajax(True)
        .set_c_attrs(c_callback='handleForgotPassword', c_type='json')
        .add_email('email', 'Email', required=True, placeholder='you@exemplo.com')
        .add_select('cargo_id', 'Tipo de Conta', required=True, options=[
            (3, 'Aluno'),
            (2, 'Professor'),
            (1, 'Administrador')
        ])
    )

    form_data = form.build()

    alerts_html = render_template('componentes/alerts.html', alerts=[
        {'id': 'forgot-erro', 'type': 'danger', 'hidden': True},
        {'id': 'forgot-info', 'type': 'info', 'hidden': True}
    ])

    footer_html = render_template('componentes/auth_footer_links.html', links=[
        {'label': 'Voltar ao login', 'url': '/login/'}
    ])

    script = """
$cruCallback('handleForgotPassword', function(response, form) {
    const erroDiv = document.getElementById('forgot-erro');
    const infoDiv = document.getElementById('forgot-info');

    erroDiv.classList.add('d-none');
    infoDiv.classList.add('d-none');

    if (response.data.ok) {
        infoDiv.textContent = response.data.message || 'Instruções enviadas!';
        infoDiv.classList.remove('d-none');
    } else {
        if (response.data.action === 'register') {
            if (confirm(response.data.message)) {
                window.location.href = '/register/';
            }
        } else {
            erroDiv.textContent = response.data.message || response.data.erro || 'Erro ao processar';
            erroDiv.classList.remove('d-none');
        }
    }
});
"""

    return render_template(
        'componentes/auth_card.html',
        title='Sistema de Avaliação',
        subtitle='Recuperar Senha',
        alerts_html=alerts_html,
        form_open=form_data['open'],
        form_campos=form_data['campos'],
        form_close=form_data['close'],
        submit_label='Recuperar Senha',
        footer_html=footer_html,
        script=script
    )

def render_forgot_password_page():
    return render_template('base.html', content=render_forgot_password_partial())
