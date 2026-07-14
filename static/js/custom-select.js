/* ============================================================
   School Management System — Custom Select Component
   ------------------------------------------------------------
   Progressively upgrades every eligible native <select> into a
   clean, modern SaaS-style select widget that matches the unified
   layout identity (12px radius, token borders, single line-art
   chevron, custom floating overlay menu with hover accents).

   Design goals / safety:
   * The original native <select> is KEPT in the DOM (visually
     hidden) so it still submits with forms and stays readable by
     existing scripts (filters, cascade Building->Floor->Room, the
     per-page AJAX controller, etc.).
   * Selecting an option writes the value back to the native select
     and dispatches native `input` + `change` events, so every
     existing listener keeps working unchanged.
   * A MutationObserver keeps the widget in sync when other code
     repopulates options or flips the disabled / invalid state
     (e.g. the cascading location selectors).
   ============================================================ */
(function () {
    'use strict';

    var OPEN = 'open';
    var instances = [];

    function eligible(select) {
        if (!select || select.tagName !== 'SELECT') return false;
        if (select.multiple) return false;
        if (select.size && select.size > 1) return false;
        if (select.dataset.cselect === 'done') return false;
        if (typeof select.dataset.noCustom !== 'undefined') return false;
        if (select.closest('.multi-select')) return false;   // custom multi-select owns its hidden <select>
        if (select.closest('.hidden-select')) return false;
        return true;
    }

    function selectedOption(select) {
        var i = select.selectedIndex;
        return i >= 0 ? select.options[i] : null;
    }

    function closeAll() {
        instances.forEach(function (inst) {
            inst.wrap.classList.remove(OPEN);
            inst.wrap.classList.remove('cselect--up');
            inst.trigger.setAttribute('aria-expanded', 'false');
        });
    }

    function build(select) {
        select.dataset.cselect = 'done';

        var fullWidth = select.classList.contains('form-select') ||
            select.classList.contains('cascade-select') ||
            select.classList.contains('form-control') ||
            select.classList.contains('w-100');

        var wrap = document.createElement('div');
        wrap.className = 'cselect ' + (fullWidth ? 'cselect--block' : 'cselect--inline');
        if (select.id === 'perPageSelect') wrap.classList.add('cselect--sm');

        var trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'cselect-trigger';
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');

        var valueEl = document.createElement('span');
        valueEl.className = 'cselect-value';

        var chevron = document.createElement('span');
        chevron.className = 'cselect-chevron';
        chevron.setAttribute('aria-hidden', 'true');
        chevron.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">' +
            '<path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" ' +
            'stroke-linecap="round" stroke-linejoin="round"/></svg>';

        trigger.appendChild(valueEl);
        trigger.appendChild(chevron);

        var panel = document.createElement('div');
        panel.className = 'cselect-panel';
        panel.setAttribute('role', 'listbox');

        select.parentNode.insertBefore(wrap, select);
        wrap.appendChild(select);
        wrap.appendChild(trigger);
        wrap.appendChild(panel);
        select.classList.add('cselect-native');

        var inst = { select: select, wrap: wrap, trigger: trigger, valueEl: valueEl, panel: panel };
        instances.push(inst);

        function renderOptions() {
            panel.innerHTML = '';
            Array.prototype.forEach.call(select.options, function (opt) {
                var row = document.createElement('div');
                row.className = 'cselect-option';
                row.setAttribute('role', 'option');
                row.dataset.value = opt.value;
                row.textContent = opt.textContent;
                if (opt.disabled) row.classList.add('is-disabled');
                if (opt.selected) row.classList.add('is-selected');
                if (!opt.disabled) {
                    row.addEventListener('click', function () {
                        select.value = opt.value;
                        select.dispatchEvent(new Event('input', { bubbles: true }));
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        syncLabel();
                        markSelected();
                        close();
                    });
                }
                panel.appendChild(row);
            });
            markSelected();
        }

        function markSelected() {
            var current = select.value;
            var rows = panel.querySelectorAll('.cselect-option');
            Array.prototype.forEach.call(rows, function (row) {
                row.classList.toggle('is-selected', row.dataset.value === current);
            });
        }

        function syncLabel() {
            var opt = selectedOption(select);
            var text = opt ? opt.textContent.trim() : '';
            valueEl.textContent = text || (select.dataset.placeholder || 'Select...');
            wrap.classList.toggle('is-placeholder', !opt || opt.value === '');
        }

        function syncState() {
            wrap.classList.toggle('is-disabled', !!select.disabled);
            trigger.disabled = !!select.disabled;
            wrap.classList.toggle('is-invalid', select.classList.contains('is-invalid'));
        }

        function open() {
            if (select.disabled) return;
            closeAll();
            wrap.classList.remove('cselect--up');
            wrap.classList.add(OPEN);
            // Decide direction: if there isn't enough room below the trigger
            // (e.g. the rows-per-page selector at the bottom of the table)
            // and there is more space above, flip the panel upward (dropup).
            var tRect = trigger.getBoundingClientRect();
            var panelH = panel.offsetHeight;
            var spaceBelow = window.innerHeight - tRect.bottom;
            var spaceAbove = tRect.top;
            if (spaceBelow < panelH + 12 && spaceAbove > spaceBelow) {
                wrap.classList.add('cselect--up');
            }
            trigger.setAttribute('aria-expanded', 'true');
            var sel = panel.querySelector('.cselect-option.is-selected');
            if (sel && sel.scrollIntoView) sel.scrollIntoView({ block: 'nearest' });
        }

        function close() {
            wrap.classList.remove(OPEN);
            wrap.classList.remove('cselect--up');
            trigger.setAttribute('aria-expanded', 'false');
        }

        trigger.addEventListener('click', function (e) {
            e.preventDefault();
            if (wrap.classList.contains(OPEN)) close();
            else open();
        });

        // Keep the widget in sync with programmatic changes to the
        // native select (options repopulated, disabled/invalid flips).
        var observer = new MutationObserver(function () {
            renderOptions();
            syncLabel();
            syncState();
        });
        observer.observe(select, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['disabled', 'class']
        });

        // Reflect value changes made by other scripts that dispatch change.
        select.addEventListener('change', function () {
            syncLabel();
            markSelected();
        });

        renderOptions();
        syncLabel();
        syncState();
    }

    function enhanceAll(root) {
        var scope = root || document;
        var selects = scope.querySelectorAll('select');
        Array.prototype.forEach.call(selects, function (s) {
            if (eligible(s)) build(s);
        });
    }

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.cselect')) closeAll();
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAll();
    });

    function init() { enhanceAll(document); }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Allow manual re-scan for dynamically injected selects.
    window.CustomSelect = { refresh: function (root) { enhanceAll(root); } };
})();
