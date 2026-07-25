(() => {
  const locale = (() => {
    const pathLocale = window.location.pathname.match(/^\/(de|es|fr|ru)(?:\/|$)/);
    return pathLocale ? pathLocale[1] : "en";
  })();
  const blogLabels = {
    en: "Blog",
    de: "Magazin",
    es: "Revista",
    fr: "Journal",
    ru: "Блог",
  };
  const blogPath = locale === "en" ? "/blog/" : `/${locale}/blog/`;
  const moneyCopy = {
    en: {
      loading: "Checking real 3D coverage…",
      supported: "Supported — detailed live 3D is available for this address.",
      partial: "Partially supported — inspect the live preview before publishing.",
      unsupported: "Not supported yet — sufficient local 3D detail is unavailable.",
      error: "The provider could not complete the check. Retry; this is not an unsupported result.",
      checkout: "Opening secure checkout…",
    },
    de: {
      loading: "Echte 3D-Abdeckung wird geprüft…",
      supported: "Unterstützt — detailliertes Live-3D ist verfügbar.",
      partial: "Teilweise unterstützt — prüfen Sie vor der Veröffentlichung die Live-Vorschau.",
      unsupported: "Noch nicht unterstützt — ausreichende lokale 3D-Details fehlen.",
      error: "Der Anbieter konnte die Prüfung nicht abschließen. Bitte erneut versuchen.",
      checkout: "Sicherer Checkout wird geöffnet…",
    },
    es: {
      loading: "Comprobando cobertura 3D real…",
      supported: "Compatible — hay 3D en vivo detallado para esta dirección.",
      partial: "Compatibilidad parcial — revisa la vista previa antes de publicar.",
      unsupported: "Aún no compatible — no hay suficiente detalle 3D local.",
      error: "El proveedor no pudo completar la comprobación. Inténtalo de nuevo.",
      checkout: "Abriendo el pago seguro…",
    },
    fr: {
      loading: "Vérification de la couverture 3D réelle…",
      supported: "Pris en charge — la 3D détaillée en direct est disponible.",
      partial: "Prise en charge partielle — vérifiez l’aperçu avant publication.",
      unsupported: "Pas encore pris en charge — le détail 3D local est insuffisant.",
      error: "Le fournisseur n’a pas terminé la vérification. Réessayez.",
      checkout: "Ouverture du paiement sécurisé…",
    },
    ru: {
      loading: "Проверяем реальное 3D-покрытие…",
      supported: "Поддерживается — для адреса доступно детальное живое 3D.",
      partial: "Частичное покрытие — перед публикацией проверьте живое превью.",
      unsupported: "Пока не поддерживается — достаточной локальной 3D-детализации нет.",
      error: "Провайдер не завершил проверку. Повторите попытку.",
      checkout: "Открываем безопасную оплату…",
    },
  }[locale];
  const hasBlogLink = (root) =>
    Array.from(root.querySelectorAll("a[href]")).some((link) =>
      /^\/(?:[a-z]{2}\/)?blog\/?$/.test(new URL(link.href, window.location.origin).pathname)
    );

  const insertBlogLink = () => {
    const nav = document.querySelector("header nav, nav");
    if (nav && !hasBlogLink(nav)) {
      const link = document.createElement("a");
      link.href = blogPath;
      link.textContent = blogLabels[locale];
      const signIn = nav.querySelector('a[href="/login"]');
      nav.insertBefore(link, signIn || null);
    }

    document.querySelectorAll("footer").forEach((footer) => {
      if (hasBlogLink(footer)) return;
      const pricing = footer.querySelector('a[href="#plans"], a[href="/#plans"]');
      if (!pricing) return;
      const link = document.createElement("a");
      link.href = blogPath;
      link.textContent = blogLabels[locale];
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

  const track = (eventName, contentId, metadata = {}) => {
    window.fetch("/api/analytics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        eventName,
        pageType: "commercial",
        contentId,
        locale,
        metadata: { source_content_id: contentId, ...metadata },
      }),
      keepalive: true,
    }).catch(() => {});
  };

  const wireMoneyChecker = () => {
    const form = document.querySelector("[data-money-checker]");
    if (!form) return;
    const input = form.querySelector('input[name="address"]');
    const button = form.querySelector('button[type="submit"]');
    const result = form.querySelector(".money-checker-result");
    if (!input || !button || !result) return;
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const address = input.value.trim();
      if (!address || button.disabled) return;
      button.disabled = true;
      result.dataset.state = "loading";
      result.textContent = moneyCopy.loading;
      track("address_check_submit", "coverage", { checker_location: "money_page" });
      try {
        const response = await window.fetch("/api/coverage/check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ address }),
        });
        const payload = await response.json();
        if (payload.property?.address) input.value = payload.property.address;
        const state = payload.status === "available"
          ? "supported"
          : payload.status === "partial"
            ? "partial"
            : payload.status === "unavailable" || payload.status === "unsupported_region"
              ? "unsupported"
              : "error";
        result.dataset.state = state;
        result.textContent = moneyCopy[state];
        track("address_check_result", "coverage", {
          checker_location: "money_page",
          coverage_tier: state,
          result_code: payload.status || "technical_error",
        });
      } catch {
        result.dataset.state = "error";
        result.textContent = moneyCopy.error;
        track("address_check_result", "coverage", {
          checker_location: "money_page",
          coverage_tier: "error",
          result_code: "network_error",
        });
      } finally {
        button.disabled = false;
      }
    });
  };

  const wireMoneyCheckout = () => {
    document.querySelectorAll('[data-money-action="checkout"]').forEach((link) => {
      link.addEventListener("click", async (event) => {
        event.preventDefault();
        if (link.dataset.loading === "true") return;
        link.dataset.loading = "true";
        const original = link.innerHTML;
        link.textContent = moneyCopy.checkout;
        try {
          const accountResponse = await window.fetch("/api/account", { cache: "no-store" });
          const account = await accountResponse.json();
          if (!account.signedIn) {
            window.location.assign(`/login?returnTo=${encodeURIComponent("/dashboard?startCheckout=1")}`);
            return;
          }
          if (account.paid) {
            window.location.assign("/dashboard");
            return;
          }
          track("checkout_start", "pricing", { plan_key: "solo" });
          const checkoutResponse = await window.fetch("/api/billing/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ returnTo: "/dashboard?billing=success" }),
          });
          const payload = await checkoutResponse.json();
          if (!checkoutResponse.ok || !payload.url) throw new Error("checkout");
          window.location.assign(payload.url);
        } catch {
          link.innerHTML = original;
          link.dataset.loading = "false";
        }
      });
    });
  };

  const initialize = () => {
    insertBlogLink();
    wireBlogMenu();
    wireMoneyChecker();
    wireMoneyCheckout();
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
