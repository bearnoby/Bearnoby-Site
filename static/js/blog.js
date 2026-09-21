(function () {
    var feed = document.getElementById("blog-feed");
    var filterBar = document.getElementById("tag-filter-bar");

    // ── Tag Filtering Logic ──
    if (feed) {
        var posts = Array.prototype.slice.call(feed.querySelectorAll(".post-card"));

        function applyFilter(tag) {
            posts.forEach(function (post) {
                var tags = (post.dataset.tags || "").split(",");
                var show = !tag || tags.indexOf(tag) !== -1;
                post.classList.toggle("hidden", !show);
            });

            if (filterBar) {
                filterBar.querySelectorAll(".tag-chip").forEach(function (chip) {
                    chip.classList.toggle("active", chip.dataset.tag === tag);
                });
            }
        }

        if (filterBar) {
            filterBar.addEventListener("click", function (e) {
                var chip = e.target.closest(".tag-chip");
                if (!chip) return;
                applyFilter(chip.dataset.tag || "");
            });
        }

        feed.addEventListener("click", function (e) {
            var chip = e.target.closest(".post-tags .tag-chip");
            if (chip) {
                applyFilter(chip.dataset.tag || "");
                return;
            }

            var shareBtn = e.target.closest(".share-btn");
            if (shareBtn) {
                var permalink = shareBtn.dataset.permalink;
                var url = location.origin + location.pathname + "#" + permalink;
                copyToClipboard(url).finally(function () {
                    var original = shareBtn.dataset.label || shareBtn.textContent;
                    shareBtn.dataset.label = original;
                    shareBtn.textContent = "Copied!";
                    shareBtn.classList.add("copied");
                    setTimeout(function () {
                        shareBtn.textContent = original;
                        shareBtn.classList.remove("copied");
                    }, 1500);
                });
            }
        });
    }

    function copyViaTextarea(text) {
        var textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand("copy");
        } catch (err) {
            /* no-op */
        }
        document.body.removeChild(textarea);
    }

    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text).catch(function () {
                copyViaTextarea(text);
            });
        }
        copyViaTextarea(text);
        return Promise.resolve();
    }

    if (location.hash) {
        var target = document.getElementById(location.hash.slice(1));
        if (target) {
            requestAnimationFrame(function () {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        }
    }
})();
