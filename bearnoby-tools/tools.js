// Screenshot lightbox and sidebar highlight for the Bearnoby Tools page.
(function () {
    var box = document.getElementById('lightbox');
    var img = document.getElementById('lightbox-img');
    var title = document.getElementById('lightbox-title');
    var text = document.getElementById('lightbox-text');
    var closeBtn = document.getElementById('lightbox-close');

    function close() { box.hidden = true; }

    document.addEventListener('click', function (e) {
        var opener = e.target.closest('[data-lightbox]');
        if (opener) {
            img.src = opener.dataset.lightbox;
            img.alt = opener.dataset.title;
            title.textContent = opener.dataset.title;
            text.textContent = opener.dataset.text;
            box.hidden = false;
            closeBtn.focus();
        } else if (e.target === box || e.target === closeBtn) {
            close();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') close();
    });

    // Highlight the sidebar link for the section currently near the top.
    var links = Array.prototype.slice.call(document.querySelectorAll('#side-nav a'));
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });

    function spy() {
        var current = 0;
        targets.forEach(function (t, i) {
            if (t && t.getBoundingClientRect().top < 160) current = i;
        });
        links.forEach(function (a, i) { a.classList.toggle('on', i === current); });
    }

    window.addEventListener('scroll', spy, { passive: true });
    spy();
})();
