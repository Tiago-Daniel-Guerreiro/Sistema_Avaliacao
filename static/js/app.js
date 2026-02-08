function addChoiceField(btn) {
    const container = btn.closest('div[id$="-container"]');
    const table = container.querySelector('table tbody');
    const rows = table.querySelectorAll('.choices-edit-item');

    const lastRow = rows[rows.length - 1];
    const lastBtn = lastRow.querySelector('button');
    if (lastBtn) {
        lastBtn.classList.remove('btn-outline-success');
        lastBtn.classList.add('btn-outline-danger');
        lastBtn.classList.add('btn-sm');
        lastBtn.textContent = '-';
        lastBtn.setAttribute('onclick', 'removeChoiceField(this)');
        lastBtn.setAttribute('style', 'width: 40px; height: 38px; padding: 0.25rem 0.4rem;');
    }

    const newRow = document.createElement('tr');
    newRow.className = 'choices-edit-item';
    newRow.innerHTML = `
        <td style="width: 100%;">
            <input type="text" class="form-control" placeholder="Digite uma opção" data-choice-input style="width: 100%;">
        </td>
        <td style="width: 50px; padding-left: 0.5rem;">
            <button type="button" class="btn btn-outline-success btn-sm" style="width: 40px; height: 38px; padding: 0.25rem 0.4rem;" onclick="addChoiceField(this)">+</button>
        </td>
    `;

    table.appendChild(newRow);
    newRow.querySelector('[data-choice-input]').focus();
    updateChoicesHidden(container.id);
}

function removeChoiceField(btn) {
    const row = btn.closest('tr');
    const container = btn.closest('div[id$="-container"]');
    const table = container.querySelector('table tbody');
    const rows = table.querySelectorAll('.choices-edit-item');

    if (rows.length === 1) return;
    row.remove();

    const newRows = table.querySelectorAll('.choices-edit-item');
    if (newRows.length > 0) {
        const newLastRow = newRows[newRows.length - 1];
        const newLastBtn = newLastRow.querySelector('button');

        if (newLastBtn) {
            newLastBtn.classList.remove('btn-outline-danger');
            newLastBtn.classList.add('btn-outline-success');
            newLastBtn.textContent = '+';
            newLastBtn.setAttribute('onclick', 'addChoiceField(this)');
        }
    }

    updateChoicesHidden(container.id);
}

function updateChoicesHidden(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const inputs = container.querySelectorAll('[data-choice-input]');
    const fieldName = containerId.replace('-container', '');
    const hiddenField = document.getElementById(fieldName);

    const choices = Array.from(inputs)
        .map(inp => inp.value.trim())
        .filter(val => val.length > 0);

    if (hiddenField) {
        hiddenField.value = JSON.stringify(choices);
    }

    updateOpcaoCorretaSelect(choices);
}

function updateOpcaoCorretaSelect(choices) {
    const select = document.querySelector('select[name="opcao_correta"]');
    if (!select) return;

    const currentValue = select.value;
    select.innerHTML = '';

    choices.forEach(choice => {
        const option = document.createElement('option');
        option.value = choice;
        option.textContent = choice;
        select.appendChild(option);
    });

    if (currentValue && choices.includes(currentValue)) {
        select.value = currentValue;
    } else if (choices.length > 0) {
        select.value = choices[0];
    }
}

function updateInputListHidden(container) {
    if (!container) return;
    const name = container.id.replace('-container', '');
    const hidden = document.getElementById(name);
    const mode = container.getAttribute('data-list-mode') || 'simple';

    const inputs = container.querySelectorAll('[data-input-value]');
    const values = Array.from(inputs)
        .map(inp => inp.value.trim())
        .filter(val => val.length > 0);

    if (hidden) {
        hidden.value = JSON.stringify(values);
    }

    if (mode === 'single') {
        const selected = container.querySelector('.correct-radio:checked');
        const hiddenCorrect = document.getElementById(name + '_correct_value');
        if (hiddenCorrect) hiddenCorrect.value = selected ? selected.value : '';
    }

    if (mode === 'multiple') {
        const checks = container.querySelectorAll('.correct-check:checked');
        const selectedValues = Array.from(checks).map(c => c.value);
        const hiddenCorrect = document.getElementById(name + '_correct_values');
        if (hiddenCorrect) hiddenCorrect.value = JSON.stringify(selectedValues);
    }
}

function syncCorrectValues(container) {
    if (!container) return;
    const mode = container.getAttribute('data-list-mode') || 'simple';
    const rows = container.querySelectorAll('.input-list-item');

    rows.forEach(row => {
        const input = row.querySelector('[data-input-value]');
        if (!input) return;
        const value = input.value;
        if (mode === 'single') {
            const radio = row.querySelector('.correct-radio');
            if (radio) radio.value = value;
        }
        if (mode === 'multiple') {
            const check = row.querySelector('.correct-check');
            if (check) check.value = value;
        }
    });
}

function addListItem(btn) {
    const row = btn.closest('tr');
    const container = btn.closest('div[id$="-container"]');
    const tbody = row.closest('tbody');
    const newRow = row.cloneNode(true);

    const input = newRow.querySelector('[data-input-value]');
    if (input) input.value = '';

    const radio = newRow.querySelector('.correct-radio');
    if (radio) {
        radio.checked = false;
        radio.value = '';
    }
    const check = newRow.querySelector('.correct-check');
    if (check) {
        check.checked = false;
        check.value = '';
    }

    btn.classList.remove('btn-outline-success');
    btn.classList.add('btn-outline-danger');
    btn.textContent = '-';
    btn.setAttribute('onclick', 'removeListItem(this)');

    tbody.appendChild(newRow);
    syncCorrectValues(container);
    updateInputListHidden(container);
}

function removeListItem(btn) {
    const row = btn.closest('tr');
    const container = btn.closest('div[id$="-container"]');
    const tbody = row.closest('tbody');
    const rows = tbody.querySelectorAll('.input-list-item');

    if (rows.length === 1) return;
    row.remove();

    const remaining = tbody.querySelectorAll('.input-list-item');
    const lastRow = remaining[remaining.length - 1];
    const lastBtn = lastRow.querySelector('button');
    if (lastBtn) {
        lastBtn.classList.remove('btn-outline-danger');
        lastBtn.classList.add('btn-outline-success');
        lastBtn.textContent = '+';
        lastBtn.setAttribute('onclick', 'addListItem(this)');
    }

    syncCorrectValues(container);
    updateInputListHidden(container);
}

function fecharModal() {
    const modaisContainer = document.getElementById('modais-container');
    if (modaisContainer) {
        modaisContainer.classList.remove('active');
        modaisContainer.innerHTML = '';
    }
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    // Garante que o scroll sempre volta
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
}

function mostrarModalSeExistir() {
    const modaisContainer = document.getElementById('modais-container');
    if (!modaisContainer) return;
    const modalEl = modaisContainer.querySelector('.modal');
    if (!modalEl) {
        modaisContainer.classList.remove('active');
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        // Garante que o scroll sempre volta
        document.body.classList.remove('modal-open');
        return;
    }

    modaisContainer.classList.add('active');

    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const instance = bootstrap.Modal.getOrCreateInstance(modalEl);
        instance.show();
    } else {
        modalEl.classList.add('show');
        modalEl.style.display = 'block';
        document.body.classList.add('modal-open');
    }

    if (!document.querySelector('.modal-backdrop')) {
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
    }
}

function logout() {
    if (confirm('Tem a certeza que deseja sair?')) {
        fetch('/logout', { method: 'POST' })
            .then(() => {
                sessionStorage.clear();
                window.location.href = '/login';
            })
            .catch(err => console.error('Erro ao fazer logout:', err));
    }
}

document.addEventListener('input', function (e) {
    if (e.target.getAttribute('data-choice-input') !== null) {
        const container = e.target.closest('div[id$="-container"]');
        if (container) {
            updateChoicesHidden(container.id);
        }
    }
    if (e.target.getAttribute('data-input-value') !== null) {
        const container = e.target.closest('div[id$="-container"]');
        syncCorrectValues(container);
        updateInputListHidden(container);
    }
});

document.addEventListener('change', function (e) {
    if (e.target.classList.contains('correct-radio') || e.target.classList.contains('correct-check')) {
        const container = e.target.closest('div[id$="-container"]');
        updateInputListHidden(container);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const modaisContainer = document.getElementById('modais-container');
    if (!modaisContainer) return;

    const observer = new MutationObserver(() => {
        if (modaisContainer.innerHTML.trim() !== '') {
            mostrarModalSeExistir();
        } else {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }
    });

    observer.observe(modaisContainer, { childList: true, subtree: true });
});

$cruCallback('handleQuestaoAdd', function (response) {
    if (response.status === 200 && response.data && response.data.ok) {
        const tabelaQuestoes = document.querySelector('#tabela-questoes tbody');
        if (tabelaQuestoes && response.data.html_row) {
            tabelaQuestoes.insertAdjacentHTML('beforeend', response.data.html_row);
        }

        const tabelaExame = document.querySelector('#tabela-questoes-exame tbody');
        if (tabelaExame && response.data.html_row_exame) {
            tabelaExame.insertAdjacentHTML('beforeend', response.data.html_row_exame);
        }

        if (response.data.resposta_id) {
            setTimeout(() => {
                fetch(`/resposta/${response.data.resposta_id}/modal/edicao`)
                    .then(r => r.text())
                    .then(html => {
                        const container = document.getElementById('modais-container');
                        if (container) {
                            container.innerHTML = html;
                            container.classList.add('active');
                        }
                        if (typeof $cruLoadEvents === 'function') $cruLoadEvents();
                    });
            }, 150);
        }
    }
});

$cruCallback('handleRespostaAdd', function (response) {
    if (response.status === 200 && response.data.ok && response.data.modal_url) {
        fecharModal();
        setTimeout(() => {
            fetch(response.data.modal_url)
                .then(r => r.text())
                .then(html => {
                    const container = document.getElementById('modais-container');
                    if (container) {
                        container.innerHTML = html;
                        container.classList.add('active');
                    }
                    if (typeof $cruLoadEvents === 'function') $cruLoadEvents();
                });
        }, 150);
    }
});
