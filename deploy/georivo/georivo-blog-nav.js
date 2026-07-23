(() => {
  const insertBlogLink = () => {
    const nav = document.querySelector("header nav, nav");
    if (nav && !nav.querySelector('a[href="/blog/"]')) {
      const link = document.createElement("a");
      link.href = "/blog/";
      link.textContent = "Blog";
      const signIn = nav.querySelector('a[href="/login"]');
      nav.insertBefore(link, signIn || null);
    }

    document.querySelectorAll("footer").forEach((footer) => {
      if (footer.querySelector('a[href="/blog/"]')) return;
      const pricing = footer.querySelector('a[href="#plans"], a[href="/#plans"]');
      if (!pricing) return;
      const link = document.createElement("a");
      link.href = "/blog/";
      link.textContent = "Blog";
      pricing.insertAdjacentElement("afterend", link);
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", insertBlogLink, { once: true });
  } else {
    insertBlogLink();
  }
})();
