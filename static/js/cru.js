const $cru = (el) => document.querySelector(el)
const $crus = (el) => document.querySelectorAll(el)

const $cruConfig = {
    'prefix_url': '', // '/api/v1',
    'headers': { 'Content-Type': 'application/json' },
    'callbacks': {},
}

const $C = (config = false) => {
    if (config) {
        for (let key of Object.keys(config)) {
            $cruConfig[key] = config[key]
        }
    }
    $cruLoadEvents()
}

const $cruLoadEvents = () => {
    $cruLoadRequests()
    $cruLoadFormIntercept()
    $cruLoadAllContainers()
    $cruLoadElementEvents()

    // Suporte a botões com c-get (AJAX)
    $crus('button[c-get]:not(.loaded)').forEach((btn) => {
        btn.classList.add('loaded');
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const url = btn.getAttribute('c-get');
            const target = btn.getAttribute('c-target');
            if (!url || !target) return;
            const container = document.querySelector(target);
            if (container) {
                container.innerHTML = `<div class="d-flex justify-content-center align-items-center"><div class="spinner-border" role="status"><span class="visually-hidden">Carregando...</span></div></div>`;
            }
            try {
                const resp = await fetch(url, { method: 'GET', headers: { 'X-Cru': '1' } });
                const html = await resp.text();
                if (container) container.innerHTML = html;
                $cruLoadEvents();
            } catch (err) {
                if (container) container.innerHTML = `<div class='text-danger'>Erro ao carregar conteúdo.</div>`;
            }
        });
    });
}

const $cruLoadElementEvents = () => {
    $crus('[c-remove]:not(.loaded)').forEach((el) => {
        el.classList.add('loaded')
        el.addEventListener('click', (e) => {
            const selector = el.getAttribute('c-remove')
            if (selector) selector.split(';').forEach(sel => $crus(sel).forEach(e => e.remove()))
        })
    })
}

const $cruLoadContainer = async (el) => {
    el.classList.add('loaded')
    const container = el.closest('[c-container]') || el
    const url = container.getAttribute('c-container')
    const target = container.getAttribute('c-target') || false
    const type = container.getAttribute('c-type') || 'html'
    const callback = container.getAttribute('c-callback') || false

    const response = await fetch($cruConfig['prefix_url'] + url, {
        method: 'GET',
        headers: { ...$cruConfig['headers'], 'X-Cru': '1' }
    })

    const content = await $cruTypeResponse(type, response)
    const $target = target ? $cru(target) : container

    if (target != 'off') $target.innerHTML = content
    if (callback) $cruConfig['callbacks'][callback](content, $target)
    $cruLoadEvents()
}

const $cruLoadAllContainers = async () => {
    $crus('[c-container]:not(.loaded)').forEach((el) => {
        el.classList.add('loaded')
        $cruLoadContainer(el)
    })

    $crus('[c-reload]:not(.loaded)').forEach((el) => {
        el.classList.add('loaded')
        el.addEventListener('click', (ev) => $cruLoadContainer(el))
    })
}

const cruRequest = async (el, method) => {
    const url = el.getAttribute(`c-${method}`)
    const type = el.getAttribute('c-type') || 'html'
    const reloadContainer = el.getAttribute('c-reload-container') || false
    const removeClosest = el.getAttribute('c-remove-closest') || false
    const selfRemove = el.getAttribute('c-self-remove') || false
    const redirect = el.getAttribute('c-redirect') || false
    const swap = el.getAttribute('c-swap') || false
    const append = el.getAttribute('c-append') || false
    const prepend = el.getAttribute('c-prepend') || false
    const callback = el.getAttribute('c-callback') || false
    const target = el.getAttribute('c-target') || false

    const response = await fetch($cruConfig['prefix_url'] + url, {
        method: method,
        headers: { ...$cruConfig['headers'], 'X-Cru': '1' }
    })

    const content = await $cruTypeResponse(type, response)
    const $target = target ? $cru(target) : false

    if (removeClosest) el.closest(removeClosest).remove()
    if (selfRemove) el.remove()
    if (swap) $cru(swap).outerHTML = content
    if (append) {
        const targetEl = $cru(append)
        if (targetEl) {
            targetEl.querySelectorAll('.tabela-empty').forEach(e => e.remove())
            targetEl.insertAdjacentHTML('beforeend', content)
        }
    }
    if (prepend) {
        const targetEl = $cru(prepend)
        if (targetEl) {
            targetEl.querySelectorAll('.tabela-empty').forEach(e => e.remove())
            targetEl.insertAdjacentHTML('afterbegin', content)
        }
    }
    if (reloadContainer) $cruLoadContainer(el)

    if ($target) $target.innerHTML = content
    if (callback) $cruConfig['callbacks'][callback](content, $target)
    $cruLoadEvents()
    if (redirect) window.location.href = redirect

}

const $cruLoadRequests = () => {
    ['delete', 'put', 'get', 'post'].forEach(method => {
        $crus(`[c-${method}]:not(.loaded)`).forEach((el) => {
            el.classList.add('loaded')
            el.addEventListener('click', () => cruRequest(el, method.toUpperCase()))
        })
    })
}

const $cruLoadFormIntercept = () => {
    $crus('.c-form:not(.loaded)').forEach((form) => {
        form.classList.add('loaded')
        form.addEventListener('submit', async (e) => {
            e.preventDefault()
            if (!form.checkValidity()) {
                form.reportValidity()
                return
            }
            const url = form.getAttribute('action')
            const method = form.getAttribute('method').toUpperCase() || 'POST'
            const type = form.getAttribute('c-type') || 'html'
            const append = form.getAttribute('c-append') || false
            const prepend = form.getAttribute('c-prepend') || false
            const redirect = form.getAttribute('c-redirect') || false
            const reset = form.getAttribute('c-reset') || false
            const swap = form.getAttribute('c-swap') || false
            const target = form.getAttribute('c-target') || false
            const reloadContainer = form.getAttribute('c-reload-container') || false
            const removeClosest = form.getAttribute('c-remove-closest') || false
            const remove = form.getAttribute('c-remove') || false
            const callback = form.getAttribute('c-callback') || false
            const isRead = $cruIsRead(method)

            const data = {};
            const formData = new FormData(e.target);
            for (const [key, value] of formData.entries()) {
                if (data[key] !== undefined) {
                    if (!Array.isArray(data[key])) {
                        data[key] = [data[key]];
                    }
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }

            const url_formatted = cruFormatURL(url, isRead, data)

            const response = await fetch(url_formatted, {
                method: method,
                headers: { ...$cruConfig['headers'], 'X-Cru': '1' },
                body: isRead ? null : JSON.stringify(data)
            })
            const content = await $cruTypeResponse(type, response)

            if (swap && $cru(swap)) $cru(swap).outerHTML = content
            if (append) {
                const targetEl = $cru(append)
                if (targetEl) {
                    targetEl.querySelectorAll('.tabela-empty').forEach(e => e.remove())
                    targetEl.insertAdjacentHTML('beforeend', content)
                }
            }
            if (prepend) {
                const targetEl = $cru(prepend)
                if (targetEl) {
                    targetEl.querySelectorAll('.tabela-empty').forEach(e => e.remove())
                    targetEl.insertAdjacentHTML('afterbegin', content)
                }
            }
            if (target && $cru(target)) $cru(target).innerHTML = content
            if (reset) form.reset()
            if (reloadContainer) $cruLoadContainer(form)
            if (remove) {
                remove.split(';').forEach(sel => {
                    const el = $cru(sel)
                    if (el) el.remove()
                })
            }
            if (removeClosest) {
                const elToRemove = form.closest(removeClosest)
                if (elToRemove) {
                    elToRemove.remove()
                    // Fechar modal se estava em um
                    if (typeof fecharModal === 'function') {
                        fecharModal()
                    }
                }
            }
            if (callback && typeof $cruConfig['callbacks'][callback] === 'function') {
                $cruConfig['callbacks'][callback]({ status: response.status, data: content }, form)
            }
            $cruLoadEvents()
            if (redirect) window.location.href = redirect
        })
    })
}

const cruFormatURL = (url, isRead, data) => {
    let url_format = $cruConfig['prefix_url'] + url
    if (isRead) {
        try {
            url_format = new URL(url)
        } catch (e) {
            try { url_format = new URL(window.location.origin + url) }
            catch (e) { throw ("Wrong URL: ", url) }
        } finally {
            url_format.search = new URLSearchParams(data).toString();
            url_format = url_format.href
        }
    }
    return url_format
}

const $cruCallback = (name, callback) => {
    $cruConfig['callbacks'][name] = callback
}

const $cruIsRead = (method) => ['GET', 'HEAD'].includes(method)

const $cruTypeResponse = async (type, response) => {
    return type == 'html' ? await response.text() : await response.json()
}

$C()
