/* ============================================================
   Reusable "Rows per page" pagination-size controller
   ------------------------------------------------------------
   Works with any list view that renders:
     - a `.table-container` holding the data table
     - a `#pagination` block (optional)
   and whose view accepts a `?per_page=` (5 | 10 | 20) URL param.

   Behaviour:
     * Reads the chosen page size from #perPageSelect.
     * Resets the active page to 1.
     * Re-fetches the same URL with the new limit and swaps in the
       new table + pagination WITHOUT a full browser refresh.
     * Preserves `per_page` on every pagination link.
   ============================================================ */
(function () {
    'use strict';

    var select = document.getElementById('perPageSelect');
    if (!select) return;

    var ALLOWED = ['5', '10', '20'];

    function currentPerPage() {
        var fromUrl = new URL(window.location.href).searchParams.get('per_page');
        return ALLOWED.indexOf(fromUrl) !== -1 ? fromUrl : (ALLOWED.indexOf(select.value) !== -1 ? select.value : '10');
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

        var pag = document.getElementById('pagination');
        var newPag = doc.getElementById('pagination');
        if (pag && newPag) pag.outerHTML = newPag.outerHTML;

        fixPaginationLinks(perPage);
        reinitTooltips();
        var sel = document.getElementById('perPageSelect');
        if (sel) sel.value = perPage;
    }

    // Keep pagination links in sync on first paint too.
    fixPaginationLinks(currentPerPage());

    select.addEventListener('change', function () {
        var perPage = ALLOWED.indexOf(select.value) !== -1 ? select.value : '10';
        var url = buildUrl(perPage);
        history.pushState({}, '', url);

        fetch(url.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(function (res) { return res.text(); })
            .then(function (html) { swapTable(html, perPage); })
            .catch(function () { window.location.href = url.toString(); });
    });
})();
