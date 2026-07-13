/* ============================================================
   School Management System — Theme Controller
   ------------------------------------------------------------
   Responsibilities:
   1. Apply the saved / system theme on page load (no FOUC).
   2. Toggle the `.dark` class + Bootstrap `data-bs-theme` on the
      <html> root and persist the choice to localStorage.theme.
   3. EXTRA FEATURE — System-aware auto theme:
      - On first visit (no stored choice) it follows the OS
        `prefers-color-scheme` preference.
      - While the user has not made an explicit choice, it keeps
        listening to OS changes live (e.g. laptop switches to dark
        at night) and updates instantly.
   ============================================================ */
(function () {
    'use strict';

    var root = document.documentElement;
    var STORAGE_KEY = 'theme';
    var media = window.matchMedia('(prefers-color-scheme: dark)');

    /* Apply (or remove) the dark theme on the root element tree. */
    function applyTheme(isDark) {
        root.classList.toggle('dark', isDark);
        root.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
    }

    /* Resolve the theme to use: explicit stored choice wins,
       otherwise fall back to the OS preference. */
    function currentIsDark() {
        var stored = null;
        try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) {}
        if (stored === 'dark') return true;
        if (stored === 'light') return false;
        return media.matches; // no explicit choice -> follow system
    }

    /* Persist a choice ('light' | 'dark'). Passing null clears the
       stored choice so the theme returns to "auto / system". */
    function persist(choice) {
        try {
            if (choice === null) {
                localStorage.removeItem(STORAGE_KEY);
            } else {
                localStorage.setItem(STORAGE_KEY, choice);
            }
        } catch (e) { /* storage unavailable (private mode) */ }
    }

    /* Enable the smooth colour transition layer (after load). */
    function enableTransition() {
        // rAF ensures the class is added on the next frame, so the
        // browser does not animate the initial theme application.
        requestAnimationFrame(function () {
            root.classList.add('theme-transition');
        });
    }

    function init() {
        // 1. Initial paint (runs as early as possible; this script is
        //    also echoed in <head> to avoid a flash before body load).
        applyTheme(currentIsDark());

        // 2. Wire up the toggle button (present in every layout).
        var toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', function () {
                var next = root.classList.contains('dark') ? 'light' : 'dark';
                persist(next);          // explicit user choice
                applyTheme(next === 'dark');
            });
        }

        // 3. EXTRA FEATURE: live OS-preference sync while in auto mode.
        var onChange = function (e) {
            var stored = null;
            try { stored = localStorage.getItem(STORAGE_KEY); } catch (err) {}
            if (!stored) {              // only auto-follow when no explicit choice
                applyTheme(e.matches);
            }
        };
        if (typeof media.addEventListener === 'function') {
            media.addEventListener('change', onChange);
        } else if (typeof media.addListener === 'function') {
            media.addListener(onChange); // legacy Safari
        }

        // 4. Smooth transitions after first paint.
        if (document.readyState === 'complete') {
            enableTransition();
        } else {
            window.addEventListener('load', enableTransition);
            document.addEventListener('DOMContentLoaded', enableTransition);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
