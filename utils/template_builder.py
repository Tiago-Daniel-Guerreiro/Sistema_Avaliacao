from flask import render_template
from markupsafe import Markup

class TableBuilder:
    def __init__(self, titulo=None):
        self.titulo = titulo
        self.header = None
        self.linhas = []
        self.botao_fora_tabela = None
        self.table_id = None

    def set_header(self, colunas, acoes=False):
        colunas_normalizadas = []
        for col in colunas:
            if isinstance(col, str):
                colunas_normalizadas.append({'titulo': col})
            else:
                colunas_normalizadas.append(col)
        
        self.header = {
            'colunas': colunas_normalizadas,
            'acoes': acoes
        }
        return self

    def set_table_id(self, table_id):
        self.table_id = table_id
        return self

    def add_linha(self, *valores, row_id=None, botoes=None):
        self.linhas.append({
            'id': row_id,
            'colunas': list(valores),
            'botoes': botoes or []
        })
        return self
   
    @staticmethod
    def botao(label, url, classe="btn btn-primary btn-sm", target="#modais-container"):
        return Markup(f'<button type="button" c-get="{url}" c-target="{target}" class="{classe}">{label}</button>')

    @staticmethod
    def botao_editar(url):
        return TableBuilder.botao("Editar", url, "btn btn-primary btn-sm")

    @staticmethod
    def botao_remover(url):
        return TableBuilder.botao("Remover", url, "btn btn-danger btn-sm")

    @staticmethod
    def botoes_crud(rota_base, item_id):
        return [
            TableBuilder.botao_editar(f"{rota_base}/{item_id}/modal/edit"),
            TableBuilder.botao_remover(f"{rota_base}/{item_id}/modal/delete")
        ]

    @staticmethod
    def botao_custom(label, url, classe="btn btn-primary btn-sm", target="#conteudo-principal"):
        return Markup(f'<button type="button" c-append="{url}" c-target="{target}" class="{classe}">{label}</button>')

    @staticmethod
    def formatar_booleano(valor):
        if valor:
            return Markup('<span class="badge bg-success">Sim</span>')
        else:
            return Markup('<span class="badge bg-danger">Não</span>')

    def set_botao_adicionar(self, url, label="Adicionar"):
        self.botao_fora_tabela = self.botao(label, url)
        return self

    def build(self):
        return render_template(
            'componentes/tabela.html',
            titulo=self.titulo,
            botao_fora_tabela=self.botao_fora_tabela,
            header=self.header,
            linhas=self.linhas,
            table_id=self.table_id
        )

    def __str__(self):
        return self.build()

class FormBuilder:
    def __init__(self, action=None, method="post"):
        self.action = action
        self.method = method
        self.ajax = True
        self.c_attrs = {}
        self.campos = []

    def set_action(self, action, method="post"):
        self.action = action
        self.method = method
        return self

    def set_ajax(self, enabled=True):
        # Controla se o formulário recebe a classe c-form (ajax do cru.js).
        self.ajax = enabled
        return self

    def set_c_attrs(self, c_type="html", c_remove_closest=None, c_swap=None, c_append=None, c_remove=None, c_callback=None):
        self.c_attrs = {
            'c-type': c_type,
            'c-remove-closest': c_remove_closest,
            'c-swap': c_swap,
            'c-append': c_append,
            'c-remove': c_remove,
            'c-callback': c_callback
        }
        return self

    def add_campo(self, tipo, name, label=None, value=None, required=False, options=None, **attrs):
        self.campos.append({
            'tipo': tipo,
            'name': name,
            'label': label,
            'value': value,
            'required': required,
            'options': options or [],
            'attrs': attrs
        })
        return self

    def add_text(self, name, label=None, value=None, required=False, **attrs):
        return self.add_campo('text', name, label, value, required, **attrs)

    def add_number(self, name, label=None, value=None, required=False, **attrs):
        return self.add_campo('number', name, label, value, required, **attrs)

    def add_email(self, name, label=None, value=None, required=False, **attrs):
        return self.add_campo('email', name, label, value, required, **attrs)

    def add_password(self, name, label=None, value=None, required=False, **attrs):
        return self.add_campo('password', name, label, value, required, **attrs)

    def add_select(self, name, label=None, value=None, options=None, required=False, **attrs):
        # Converter tuples em dicts com 'value' e 'label'
        if options:
            normalized_opts = []
            for opt in options:
                if isinstance(opt, (tuple, list)):
                    normalized_opts.append({'value': opt[0], 'label': opt[1]})
                elif isinstance(opt, dict):
                    normalized_opts.append(opt)
                else:
                    normalized_opts.append({'value': opt, 'label': str(opt)})
            options = normalized_opts
        
        return self.add_campo('select', name, label, value, required, options=options, **attrs)

    def add_choices_edit(self, name, label=None, value=None, required=False, **attrs):
        return self.add_campo('choices_edit', name, label, value, required, **attrs)

    def add_input_edit(self, name, label=None, value=None, required=False, input_type='text', **attrs):
        attrs['input_type'] = input_type
        return self.add_campo('input_edit', name, label, value, required, **attrs)

    def add_input_list(self, name, label=None, value=None, required=False, input_type='text', mode='simple', opcao_correta=None, opcoes_corretas=None, **attrs):
        attrs['input_type'] = input_type
        attrs['mode'] = mode
        
        # Normalizar value para lista
        if isinstance(value, str):
            try:
                import json
                initial_value = json.loads(value) if value else []
            except:
                initial_value = [value] if value else []
        elif isinstance(value, list):
            initial_value = value
        else:
            initial_value = []
        
        attrs['initial_value'] = initial_value
        
        # Adicionar opções corretas se necessário
        if mode == 'single' and opcao_correta is not None:
            attrs['opcao_correta'] = opcao_correta
        elif mode == 'multiple':
            if isinstance(opcoes_corretas, str):
                try:
                    import json
                    attrs['opcoes_corretas'] = json.loads(opcoes_corretas) if opcoes_corretas else []
                except:
                    attrs['opcoes_corretas'] = [opcoes_corretas] if opcoes_corretas else []
            else:
                attrs['opcoes_corretas'] = opcoes_corretas if isinstance(opcoes_corretas, list) else []
        
        # Usar template único para listas
        tipo = 'input_list'
        
        return self.add_campo(tipo, name, label, value, required, **attrs)

    def add_custom(self, html):
        self.campos.append({'tipo': 'custom', 'html': html})
        return self

    def _build_campos(self):
        html_campos = []
        for campo in self.campos:
            if campo['tipo'] == 'custom':
                html_campos.append(campo['html'])
            else:
                def _normalize_options(options):
                    if not options:
                        return []
                    normalized = []
                    for opt in options:
                        if isinstance(opt, dict):
                            normalized.append(opt)
                        elif isinstance(opt, (tuple, list)):
                            if len(opt) >= 2:
                                normalized.append({'value': opt[0], 'label': opt[1]})
                            elif len(opt) == 1:
                                normalized.append({'value': opt[0], 'label': str(opt[0])})
                        else:
                            normalized.append({'value': opt, 'label': str(opt)})
                    return normalized

                # Preparar variáveis para o template
                template_vars = {
                    'tipo': campo['tipo'],
                    'name': campo['name'],
                    'label': campo['label'],
                    'value': campo['value'],
                    'required': campo['required'],
                    'options': campo.get('options', [])
                }
                template_vars['options'] = _normalize_options(template_vars.get('options', []))
                # Adicionar atributos extras
                if campo.get('attrs'):
                    template_vars.update(campo['attrs'])
                
                # Escolher template
                template_name = f"componentes/input/{campo['tipo']}.html"
                
                html_campos.append(render_template(
                    template_name,
                    **template_vars
                ))
        return Markup('\n'.join(html_campos))

    def _build_attrs(self):
        attrs = [
            f'action="{self.action}"',
            f'method="{self.method}"'
        ]

        if self.ajax:
            attrs.insert(0, 'class="c-form"')
        
        for key, value in self.c_attrs.items():
            if value:
                attrs.append(f'{key}="{value}"')
        
        return ' '.join(attrs)

    def build(self):
        return {
            'attrs': self._build_attrs(),
            'campos': self._build_campos(),
            'open': Markup(f'<form {self._build_attrs()}>'),
            'close': Markup('</form>')
        }

    @classmethod
    def criar(cls, rota_base, append_target):
        return (cls()
            .set_action(f"{rota_base.rstrip('/')}/", "post")
            .set_c_attrs(c_remove_closest="#modal-wrapper", c_append=append_target)
        )

    @classmethod
    def editar(cls, rota_base, item_id, swap_target):
        return (cls()
            .set_action(f"{rota_base}/{item_id}", "put")
            .set_c_attrs(c_remove_closest="#modal-wrapper", c_swap=swap_target)
        )

    @classmethod
    def deletar(cls, rota_base, item_id, remove_target):
        return (cls()
            .set_action(f"{rota_base}/{item_id}", "delete")
            .set_c_attrs(c_remove_closest="#modal-wrapper", c_remove=remove_target)
        )

class ModalBuilder:
    def __init__(self, modal_id=None, dialog_class=None, size="lg", scrollable=True, show_close_button=True):
        self.modal_id = modal_id
        self.dialog_class = dialog_class or ""
        self.size = size  # "sm", "lg", "xl", ou ""
        self.scrollable = scrollable
        self.show_close_button = show_close_button
        
        self.titulo = None
        self.header_html = None
        self.body_html = ""
        self.footer_buttons = []
        self.form = None
        self.scripts = []  # Lista de scripts a executar

    def set_titulo(self, titulo):
        self.titulo = titulo
        return self

    def set_header(self, html):
        self.header_html = html
        return self

    def set_body(self, html):
        self.body_html = html
        return self

    def set_form(self, form_builder):
        self.form = form_builder
        return self

    def add_script(self, script_code):
        self.scripts.append(script_code)
        return self

    def add_button(self, label, classe="btn btn-primary", btn_type="button", **attrs):
        attrs_html = ' '.join(f'{k}="{v}"' for k, v in attrs.items() if v)
        btn = f'<button type="{btn_type}" class="{classe}" {attrs_html}>{label}</button>'
        self.footer_buttons.append(btn)
        return self

    def add_cancel_button(self, label="Cancelar"):
        return self.add_button(label, "btn btn-secondary", **{'data-bs-dismiss': 'modal', 'onclick': 'fecharModal()'})

    def add_submit_button(self, label="Salvar", classe="btn btn-primary"):
        return self.add_button(label, classe, btn_type="submit")

    def _build_header(self):
        if self.header_html:
            return self.header_html
        
        if not self.titulo:
            return ""
        
        close_button = f'<button type="button" class="btn-close" data-bs-dismiss="modal" onclick="fecharModal()"></button>' if self.show_close_button else ''
        
        return f'''
        <div class="modal-header">
            <h5 class="modal-title">{self.titulo}</h5>
            {close_button}
        </div>
        '''

    def _build_footer(self):
        if not self.footer_buttons:
            return ""
        return f'<div class="modal-footer">{" ".join(self.footer_buttons)}</div>'


    def _build_scripts(self):
        if not self.scripts:
            return ""
        
        script_tags = []
        for script_code in self.scripts:
            script_tags.append(f'<script>{script_code}</script>')
        
        return '\n'.join(script_tags)

    def build(self):
        id_attr = f'id="{self.modal_id}"' if self.modal_id else ""
        
        # Construir classes do dialog
        dialog_classes = ["modal-dialog", "modal-dialog-centered"]
        if self.scrollable:
            dialog_classes.append("modal-dialog-scrollable")
        if self.size:
            dialog_classes.append(f"modal-{self.size}")
        if self.dialog_class:
            dialog_classes.append(self.dialog_class)
        
        dialog_classes_str = " ".join(dialog_classes)

        # Construir header
        header_html = self._build_header()
        
        # Construir body (sem form tag ainda)
        body_html = Markup(f'<div class="modal-body">{self.body_html}</div>')
        
        # Construir footer
        footer_html = self._build_footer()

        # Se tem form, envolver tudo (header, body, footer) dentro do form
        if self.form:
            form_data = self.form.build()
            content_inner = Markup(f'''
                {header_html}
                {form_data['open']}
                {body_html}
                {footer_html}
                {form_data['close']}
            ''')
        else:
            content_inner = Markup(f'''
                {header_html}
                {body_html}
                {footer_html}
            ''')

        modal_content = Markup(f'<div class="modal-content">{content_inner}</div>')

        html = Markup(f'''<div id="modal-wrapper">
    <div class="modal" {id_attr} tabindex="-1">
        <div class="{dialog_classes_str}">
            {modal_content}
        </div>
    </div>
</div>''')

        # Adicionar field listeners e scripts customizados
        custom_scripts = self._build_scripts()
        
        return Markup(str(html) + str(custom_scripts))

    def __str__(self):
        return self.build()