from flask import render_template
from utils.template_builder import FormBuilder

def render_login_partial():
    form = (FormBuilder(action='/login/', method='post')
        .set_ajax(True)
        .set_c_attrs(c_callback='handleLogin', c_type='json')
        .add_email('email', 'Email', required=True, placeholder='you@exemplo.com')
        .add_password('senha', 'Palavra-passe', required=True, placeholder='••••••••')
    )

    form_data = form.build()

    alerts_html = render_template('componentes/alerts.html', alerts=[
        {'id': 'login-erro', 'type': 'danger', 'hidden': True}
    ])

    footer_html = render_template('componentes/auth_footer_links.html', links=[
        {'label': 'Esqueci a senha', 'url': '/forgot-password/'},
        {'label': 'Criar conta', 'url': '/register/'}
    ])

    script = """
$cruCallback('handleLogin', function(response, form) {
    if (response.status === 200 && response.data.ok) {
        const data = response.data;
        sessionStorage.setItem('userId', data.userId);
        sessionStorage.setItem('role', data.role);
        sessionStorage.setItem('email', data.user);
        if (data.alunoId) sessionStorage.setItem('alunoId', data.alunoId);

        if (data.role === 1 || data.role === 'admin') {
            window.location.href = '/gestao';
        } else if (data.role === 2 || data.role === 'professor') {
            window.location.href = '/professores';
        } else if (data.role === 3 || data.role === 'aluno') {
            window.location.href = '/alunos';
        } else {
            window.location.href = '/';
        }
    } else {
        const erro = document.getElementById('login-erro');
        erro.textContent = response.data.erro || 'Erro ao fazer login';
        erro.classList.remove('d-none');
    }
});
"""

    return render_template(
        'componentes/auth_card.html',
        title='Sistema de Avaliação',
        subtitle='Entrar',
        alerts_html=alerts_html,
        form_open=form_data['open'],
        form_campos=form_data['campos'],
        form_close=form_data['close'],
        submit_label='Entrar',
        footer_html=footer_html,
        script=script
    )

def render_login_page():
    return render_template('base.html', content=render_login_partial())
