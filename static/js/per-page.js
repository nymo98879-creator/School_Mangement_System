/* ============================================================
   Reusable "Rows per page" pagination-size controller
   ------------------------------------------------------------
   Works with any list view that renders a `.table-container`
   (optionally including an in-card footer with the
   `#perPageSelect` rows-per-page selector and a `#pagination`
   block). The view must accept a `?per_page=` (5 | 10 | 20)
   and `?page=` URL param.

   Behaviour:
     * Reads the chosen page size from #perPageSelect.
     * Resets the active page to 1.
     * Re-fetches and swaps the whole `.table-container` (footer
       included) WITHOUT a full browser refresh.
     * Uses event delegation on `document`, so the listener keeps
       working after the AJAX swap replaces the select element.
     * Preserves `per_page` on every pagination link.
   ============================================================ */
(function () {
    'use strict';

    var ALLOWED = ['5', '10', '20'];

    function currentPerPage() {
        var fromUrl = new URL(window.location.href).searchParams.get('per_page');
        if (ALLOWED.indexOf(fromUrl) !== -1) return fromUrl;
        var sel = document.getElementById('perPageSelect');
        return (sel && ALLOWED.indexOf(sel.value) !== -1) ? sel.value : '10';
    }

    function buildUrl(perPage) {
        var url = new URL(window.location.href);
        url.searchParams.set('per_page', perPage);
        url.searchParams.set('page', '1');
        return url;
    }

    function fixPaginationLinks(perPage) {
        var pag = document.getElementById('pagination');
        if (!pag) return;
        pag.querySelectorAll('a.page-btn').forEach(function (a) {
            try {
                var u = new URL(a.href, window.location.href);
                u.searchParams.set('per_page', perPage);
                a.href = u.pathname + u.search;
            } catch (e) { /* ignore malformed href */ }
        });
    }

    function reinitTooltips() {
        if (!(window.bootstrap && bootstrap.Tooltip)) return;
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            var instance = bootstrap.Tooltip.getInstance(el);
            if (instance) instance.dispose();
        });
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }

    function swapTable(html, perPage) {
        var doc = new DOMParser().parseFromString(html, 'text/html');

        var container = document.querySelector('.table-container');
        var newContainer = doc.querySelector('.table-container');
        if (container && newContainer) container.outerHTML = newContainer.outerHTML;

        // Card grid view (Table/Card toggle) — keep it in sync too, so
        // pagination / rows-per-page work while the card layout is active.
        var cardView = document.getElementById('cardView');
        var newCardView = doc.getElementById('cardView');
        if (cardView && newCardView) cardView.outerHTML = newCardView.outerHTML;

        fixPaginationLinks(perPage);
        reinitTooltips();
        var sel = document.getElementById('perPageSelect');
        if (sel) sel.value = perPage;
        // Re-enhance the freshly inserted native select into the custom widget.
        if (window.CustomSelect) window.CustomSelect.refresh();

        // Let list pages re-apply their filters / counts to the fresh DOM.
        document.dispatchEvent(new CustomEvent('list:refreshed'));
    }

    // Keep pagination links in sync on first paint too.
    fixPaginationLinks(currentPerPage());

    // Event delegation: the select lives inside the swapped .table-container,
    // so bind the change listener on document — it survives every AJAX swap.
    document.addEventListener('change', function (e) {
        var target = e.target;
        if (!target || target.id !== 'perPageSelect') return;
        var perPage = ALLOWED.indexOf(target.value) !== -1 ? target.value : '10';
        var url = buildUrl(perPage);
        history.pushState({}, '', url);

        fetch(url.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function (res) { return res.text(); })
            .then(function (resHtml) { swapTable(resHtml, perPage); })
            .catch(function () { window.location.href = url.toString(); });
    });
})();
