(() => {
  const hasBlogLink = (root) =>
    Array.from(root.querySelectorAll("a[href]")).some((link) =>
      /^\/(?:[a-z]{2}\/)?blog\/?$/.test(new URL(link.href, window.location.origin).pathname)
    );

  const insertBlogLink = () => {
    const nav = document.querySelector("header nav, nav");
    if (nav && !hasBlogLink(nav)) {
      const link = document.createElement("a");
      link.href = "/blog/";
      link.textContent = "Blog";
      const signIn = nav.querySelector('a[href="/login"]');
      nav.insertBefore(link, signIn || null);
    }

    document.querySelectorAll("footer").forEach((footer) => {
      if (hasBlogLink(footer)) return;
      const pricing = footer.querySelector('a[href="#plans"], a[href="/#plans"]');
      if (!pricing) return;
      const link = document.createElement("a");
      link.href = "/blog/";
      link.textContent = "Blog";
      pricing.insertAdjacentElement("afterend", link);
    });
  };

  const wireBlogMenu = () => {
    if (!document.body.classList.contains("blog-shell")) return;
    const button = document.querySelector(".menu-button");
    const links = document.querySelector(".nav-links");
    if (!button || !links) return;
    button.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      button.setAttribute("aria-expanded", open ? "true" : "false");
      button.textContent = open ? "Close" : "Menu";
    });
    links.addEventListener("click", (event) => {
      if (!event.target.closest("a")) return;
      links.classList.remove("open");
      button.setAttribute("aria-expanded", "false");
      button.textContent = "Menu";
    });
  };

  const initialize = () => {
    insertBlogLink();
    wireBlogMenu();
    if (!document.body.classList.contains("blog-shell")) {
      let scheduled = false;
      const observer = new MutationObserver(() => {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(() => {
          scheduled = false;
          insertBlogLink();
        });
      });
      observer.observe(document.body, { childList: true, subtree: true });
      window.setTimeout(insertBlogLink, 1000);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
