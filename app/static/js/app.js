/* ==========================================================================
   Split Expenses — Frontend Logic & PWA Install Prompt
   ========================================================================== */

/**
 * Add a new member input field to the create-group form.
 * Called from the "+ Add Member" button on the landing page.
 */
function addMemberField() {
    const container = document.getElementById('members-container');
    if (!container) return;

    const row = document.createElement('div');
    row.className = 'member-input-row';
    row.innerHTML = `
        <input type="text" name="members" class="form-input member-input" placeholder="Member name" required>
        <button type="button" class="remove-member-btn" onclick="removeMemberField(this)" aria-label="Remove member">✕</button>
    `;
    container.appendChild(row);

    const newInput = row.querySelector('input');
    if (newInput) newInput.focus();
}

/**
 * Remove a member input field from the create-group form.
 * Ensures at least 2 member fields always remain.
 */
function removeMemberField(button) {
    const container = document.getElementById('members-container');
    if (!container) return;

    const rows = container.querySelectorAll('.member-input-row');
    if (rows.length <= 2) return;

    button.closest('.member-input-row').remove();
}

/**
 * Toggle PIN visibility in the share info box.
 */
function togglePinVisibility() {
    const pinEl = document.getElementById('share-pin');
    const btn = document.getElementById('toggle-pin-btn');
    if (!pinEl || !btn) return;

    if (pinEl.dataset.visible === 'true') {
        pinEl.textContent = '••••';
        pinEl.dataset.visible = 'false';
        btn.innerHTML = '👁️ Show';
    } else {
        pinEl.textContent = pinEl.dataset.pin || '••••';
        pinEl.dataset.visible = 'true';
        btn.innerHTML = '🙈 Hide';
    }
}

/**
 * Copy share info (group name + PIN) to clipboard as a formatted message.
 */
function copyShareInfo() {
    const groupName = document.getElementById('share-group-name');
    const pinEl = document.getElementById('share-pin');
    const btn = document.getElementById('copy-share-btn');
    if (!groupName || !btn) return;

    const pin = pinEl ? (pinEl.dataset.pin || '') : '';
    const appUrl = window.location.origin;
    const text = `Join my Split Expenses group!\n\nGroup Name: ${groupName.textContent.trim()}\nPIN: ${pin}\n\nOpen: ${appUrl}`;

    navigator.clipboard.writeText(text).then(function () {
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        btn.classList.add('btn-accent');

        setTimeout(function () {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-accent');
        }, 2000);
    }).catch(function () {
        prompt('Copy this share text:', text);
    });
}

/**
 * Toggle all member checkboxes in the "Split Among" section.
 * Linked to the "Select All" master checkbox (scoped per form).
 */
function toggleAllMembers(selectAllCheckbox) {
    if (!selectAllCheckbox) return;
    const form = selectAllCheckbox.closest('form');
    if (!form) return;

    const checkboxes = form.querySelectorAll('.member-checkbox');
    checkboxes.forEach(function (cb) {
        cb.checked = selectAllCheckbox.checked;
    });
}

/**
 * Sync the "Select All" checkbox state when individual checkboxes change.
 */
function syncSelectAll(event) {
    const target = event ? event.target : null;
    if (!target) return;

    const form = target.closest('form');
    if (!form) return;

    const selectAll = form.querySelector('.select-all-checkbox');
    const checkboxes = form.querySelectorAll('.member-checkbox');
    if (!selectAll || checkboxes.length === 0) return;

    const allChecked = Array.from(checkboxes).every(function (cb) {
        return cb.checked;
    });
    selectAll.checked = allChecked;
}

/**
 * Toggle the Add Member inline form on the Group Dashboard.
 */
function toggleAddMemberForm() {
    const panel = document.getElementById('add-member-panel');
    if (!panel) return;

    if (panel.style.display === 'none' || !panel.style.display) {
        panel.style.display = 'block';
        const input = document.getElementById('new-member-name');
        if (input) input.focus();
    } else {
        panel.style.display = 'none';
    }
}

/* --- PWA Install Prompt --- */
let deferredInstallPrompt = null;

window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredInstallPrompt = e;

    const installBtn = document.getElementById('install-btn');
    if (installBtn) {
        installBtn.style.display = 'flex';
        installBtn.addEventListener('click', function () {
            if (deferredInstallPrompt) {
                deferredInstallPrompt.prompt();
                deferredInstallPrompt.userChoice.then(function (choiceResult) {
                    if (choiceResult.outcome === 'accepted') {
                        installBtn.style.display = 'none';
                    }
                    deferredInstallPrompt = null;
                });
            }
        });
    }
});

window.addEventListener('appinstalled', function () {
    const installBtn = document.getElementById('install-btn');
    if (installBtn) installBtn.style.display = 'none';
    deferredInstallPrompt = null;
});

/* --- Offline Detection --- */
function updateOnlineStatus() {
    const banner = document.getElementById('offline-banner');
    if (!banner) return;

    if (!navigator.onLine) {
        banner.classList.add('visible');
    } else {
        banner.classList.remove('visible');
    }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

/* --- Landing Page Tab Switching --- */
function switchLandingTab(tabName) {
    const createBtn = document.getElementById('tab-btn-create');
    const joinBtn = document.getElementById('tab-btn-join');
    const createContent = document.getElementById('landing-create-content');
    const joinContent = document.getElementById('landing-join-content');

    if (!createBtn || !joinBtn || !createContent || !joinContent) return;

    if (tabName === 'create') {
        createBtn.classList.add('active');
        joinBtn.classList.remove('active');
        createContent.style.display = 'block';
        joinContent.style.display = 'none';
    } else {
        joinBtn.classList.add('active');
        createBtn.classList.remove('active');
        joinContent.style.display = 'block';
        createContent.style.display = 'none';
    }
}

/* --- Switch Entry Type (Expense vs Advance Collection) --- */
function switchExpenseType(type) {
    const expenseTab = document.getElementById('tab-type-expense');
    const advanceTab = document.getElementById('tab-type-advance');
    const hiddenType = document.getElementById('form-entry-type');

    const payerLabel = document.getElementById('payer-label');
    const descLabel = document.getElementById('description-label');
    const descInput = document.getElementById('expense-description');
    const splitLabel = document.getElementById('split-label');
    const submitBtn = document.getElementById('add-expense-submit');
    const categorySelect = document.getElementById('expense-category');

    if (!expenseTab || !advanceTab || !hiddenType) return;

    if (type === 'advance') {
        advanceTab.classList.add('active');
        advanceTab.classList.remove('btn-outline');
        expenseTab.classList.remove('active');
        expenseTab.classList.add('btn-outline');
        hiddenType.value = 'advance';

        if (payerLabel) payerLabel.textContent = 'Collector / Treasurer';
        if (descLabel) descLabel.textContent = 'Description';
        if (descInput) descInput.placeholder = 'e.g., Advance collected from members';
        if (splitLabel) splitLabel.textContent = 'Collected From';
        if (submitBtn) submitBtn.innerHTML = '💵 Add Advance Collection';

        if (categorySelect) {
            for (let i = 0; i < categorySelect.options.length; i++) {
                if (categorySelect.options[i].value === 'Advance / Deposit') {
                    categorySelect.selectedIndex = i;
                    break;
                }
            }
        }
    } else {
        expenseTab.classList.add('active');
        expenseTab.classList.remove('btn-outline');
        advanceTab.classList.remove('active');
        advanceTab.classList.add('btn-outline');
        hiddenType.value = 'expense';

        if (payerLabel) payerLabel.textContent = 'Paid By';
        if (descLabel) descLabel.textContent = 'Description';
        if (descInput) descInput.placeholder = 'e.g., Lunch at hotel';
        if (splitLabel) splitLabel.textContent = 'Split Among';
        if (submitBtn) submitBtn.innerHTML = '💰 Add Expense';

        if (categorySelect) {
            if (categorySelect.value === 'Advance / Deposit') {
                categorySelect.selectedIndex = 0;
            }
        }
    }
}

/**
 * Export Settlement report as PDF / Print preview document.
 */
function exportSettlementPdf() {
    window.print();
}

/**
 * Copy formatted settlement summary text to clipboard for WhatsApp/SMS sharing.
 */
function copySettlementSummary() {
    const btn = document.getElementById('copy-summary-btn');

    const subtitleEl = document.querySelector('.page-subtitle');
    const totalSpent = document.getElementById('total-spent-value');
    const perPerson = document.getElementById('per-person-value');

    let text = `⚖️ *Split Expenses Settlement Report*\n`;
    if (subtitleEl) text += `${subtitleEl.textContent.trim()}\n`;
    text += `\n📊 *Overview*\n`;
    if (totalSpent) text += `• Total Spent: ${totalSpent.textContent.trim()}\n`;
    if (perPerson) text += `• Per Person Share: ${perPerson.textContent.trim()}\n`;

    const cards = document.querySelectorAll('.settlement-transfer-card');
    text += `\n💸 *Who Pays Whom*\n`;
    if (cards.length > 0) {
        cards.forEach(function (card, idx) {
            const debtor = card.querySelector('.debtor-party .party-name');
            const creditor = card.querySelector('.creditor-party .party-name');
            const amount = card.querySelector('.transfer-amount-pill');
            if (debtor && creditor && amount) {
                text += `${idx + 1}. *${debtor.textContent.trim()}* ➔ *${creditor.textContent.trim()}*: ${amount.textContent.trim()}\n`;
            }
        });
    } else {
        text += `Everyone is settled up! No payments needed. ✅\n`;
    }

    const rows = document.querySelectorAll('.balances-data-table tbody tr');
    if (rows.length > 0) {
        text += `\n👤 *Individual Balances*\n`;
        rows.forEach(function (row) {
            const name = row.querySelector('.member-name-text');
            const net = row.querySelector('.net-balance-cell');
            if (name && net) {
                text += `• ${name.textContent.trim()}: ${net.textContent.trim()}\n`;
            }
        });
    }

    text += `\nOpen app: ${window.location.href}`;

    navigator.clipboard.writeText(text).then(function () {
        if (!btn) return;
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        btn.classList.add('btn-accent');

        setTimeout(function () {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-accent');
        }, 2000);
    }).catch(function () {
        prompt('Copy this settlement summary text:', text);
    });
}

/* --- Expense Edit Toggle --- */
function toggleEditExpense(expenseId) {
    const panel = document.getElementById('edit-panel-' + expenseId);
    if (!panel) return;

    if (panel.style.display === 'none' || !panel.style.display) {
        panel.style.display = 'block';
        const descInput = panel.querySelector('input[name="description"]');
        if (descInput) descInput.focus();
    } else {
        panel.style.display = 'none';
    }
}

/* --- Select Member Chip Handler --- */
function selectMemberChip(element) {
    if (!element) return;
    const name = element.dataset.memberName;
    const nameInput = document.getElementById('member-name');
    if (nameInput && name) {
        nameInput.value = name;
        nameInput.focus();
    }

    const chips = document.querySelectorAll('.selectable-member-chip');
    chips.forEach(function (chip) {
        chip.classList.remove('active');
    });

    element.classList.add('active');
}

/* Backward compatibility alias */
function selectMemberName(name, element) {
    selectMemberChip(element);
}

/* --- Init --- */
document.addEventListener('DOMContentLoaded', function () {
    updateOnlineStatus();

    const memberCheckboxes = document.querySelectorAll('.member-checkbox');
    memberCheckboxes.forEach(function (cb) {
        cb.addEventListener('change', syncSelectAll);
    });

    const addExpenseForm = document.getElementById('add-expense-form');
    if (addExpenseForm) {
        addExpenseForm.addEventListener('submit', function (e) {
            const checkboxes = addExpenseForm.querySelectorAll('.member-checkbox');
            const checkedCount = Array.from(checkboxes).filter(function (cb) { return cb.checked; }).length;
            if (checkboxes.length > 0 && checkedCount === 0) {
                e.preventDefault();
                alert('Please select at least one member to share or contribute.');
            }
        });
    }

    // Auto-highlight member chip if user types a matching name manually
    const nameInput = document.getElementById('member-name');
    if (nameInput) {
        nameInput.addEventListener('input', function () {
            const currentVal = nameInput.value.trim().toLowerCase();
            const chips = document.querySelectorAll('.selectable-member-chip');
            chips.forEach(function (chip) {
                const chipName = (chip.dataset.memberName || '').trim().toLowerCase();
                if (chipName === currentVal && currentVal !== '') {
                    chip.classList.add('active');
                } else {
                    chip.classList.remove('active');
                }
            });
        });
    }
});

/* --- BFCache & Back-Button Session Security --- */
window.addEventListener('pageshow', function (event) {
    // Force fresh server validation if restored from browser BFCache
    if (event.persisted) {
        window.location.reload();
    }
});

/* ==========================================================================
   Custom Confirmation Modal Component
   Replaces native browser confirm() dialogs with modern dark glassmorphic UI
   ========================================================================== */

/**
 * Show a promise-based custom modal dialog matching the UI theme.
 * @param {Object} options - { title, message, icon, confirmText, cancelText, confirmClass }
 * @returns {Promise<boolean>}
 */
function showConfirmModal(options) {
    return new Promise(function (resolve) {
        options = options || {};
        const modal = document.getElementById('custom-confirm-modal');
        const iconEl = document.getElementById('modal-icon');
        const titleEl = document.getElementById('modal-title');
        const msgEl = document.getElementById('modal-message');
        const cancelBtn = document.getElementById('modal-cancel-btn');
        const confirmBtn = document.getElementById('modal-confirm-btn');

        if (!modal || !titleEl || !msgEl || !cancelBtn || !confirmBtn) {
            resolve(window.confirm(options.message || 'Are you sure?'));
            return;
        }

        titleEl.textContent = options.title || 'Confirm Action';
        msgEl.textContent = options.message || 'Are you sure you want to proceed?';
        iconEl.textContent = options.icon || '⚠️';

        confirmBtn.textContent = options.confirmText || 'Confirm';
        confirmBtn.className = 'btn ' + (options.confirmClass || 'btn-danger');

        cancelBtn.textContent = options.cancelText || 'Cancel';

        modal.style.display = 'flex';
        // Force reflow for opacity transition
        void modal.offsetWidth;
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');

        function cleanup(result) {
            modal.classList.remove('active');
            setTimeout(function () {
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            }, 200);

            confirmBtn.removeEventListener('click', onConfirm);
            cancelBtn.removeEventListener('click', onCancel);
            modal.removeEventListener('click', onBackdropClick);
            document.removeEventListener('keydown', onKeyDown);

            resolve(result);
        }

        function onConfirm() { cleanup(true); }
        function onCancel() { cleanup(false); }
        function onBackdropClick(e) { if (e.target === modal) cleanup(false); }
        function onKeyDown(e) { if (e.key === 'Escape') cleanup(false); }

        confirmBtn.addEventListener('click', onConfirm);
        cancelBtn.addEventListener('click', onCancel);
        modal.addEventListener('click', onBackdropClick);
        document.addEventListener('keydown', onKeyDown);

        confirmBtn.focus();
    });
}

/**
 * Intercept form submit button click to display custom confirm modal.
 */
function confirmFormSubmit(event, title, message, confirmText, icon, confirmClass) {
    event.preventDefault();
    const btn = event.currentTarget;
    const form = btn.closest('form');
    if (!form) return false;

    showConfirmModal({
        title: title || 'Are you sure?',
        message: message || '',
        confirmText: confirmText || 'Confirm',
        icon: icon || '⚠️',
        confirmClass: confirmClass || 'btn-danger'
    }).then(function (confirmed) {
        if (confirmed) {
            form.submit();
        }
    });

    return false;
}


