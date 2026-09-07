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

    const selectAll = form.querySelector('#select-all-members');
    const checkboxes = form.querySelectorAll('.member-checkbox');
    if (!selectAll || checkboxes.length === 0) return;

    const allChecked = Array.from(checkboxes).every(function (cb) {
        return cb.checked;
    });
    selectAll.checked = allChecked;
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

