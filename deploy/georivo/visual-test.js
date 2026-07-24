async (page) => {
  const jobs = [
    ["f4e22523e9d9c7e1ee5d2dd5", "/embed/squarespace/", "integration_guide"],
    ["1d90690e80ac794d9c12cb66", "/embed/webflow/", "integration_guide"],
    ["93a6ee8a8bc3de39dcea9e42", "/embed/wix/", "integration_guide"],
    ["eb05856221f551c4002015a9", "/embed/wordpress/", "integration_guide"],
    ["0b46c5cdcfd34863acb69063", "/examples/mountain-property-location-story/", "example"],
    ["5e65559c0ea3b174f763d0e9", "/examples/rural-estate-aerial-view/", "example"],
    ["d9717e33eeac0dec1777b2f6", "/examples/urban-condo-neighborhood-story/", "example"],
    ["3948de6801d41b260b595c9e", "/examples/waterfront-villa-property-flyover/", "example"],
    ["5bce045933aa6f2e468388f5", "/guides/3d-property-flyover-vs-drone-video/", "guide"],
    ["bc69e2f2d67f8813a7ff80fa", "/guides/3d-property-flyover-vs-virtual-tour/", "guide"],
    ["bdc2dce5524c72ca1ab41c29", "/guides/how-to-add-a-3d-map-to-a-real-estate-website/", "guide"],
    ["d52b715fb6b19208ebe66501", "/guides/how-to-market-a-property-to-remote-buyers/", "guide"],
    ["3100e68d902a5794155e68bd", "/guides/how-to-show-nearby-amenities-on-a-property-listing/", "guide"],
    ["eacf56c4d450093be5562786", "/guides/real-estate-listing-media-checklist/", "guide"],
    ["eb0b07927411ccb2c38c146b", "/guides/what-is-a-3d-property-flyover/", "guide"],
    ["8d6269b60ac5ba252fe43e7f", "/guides/which-property-listings-need-an-aerial-view/", "guide"],
    ["acab10e7b6b308e8028d5139", "/templates/arrival-guide/", "template"],
    ["aa184ebc51374896bc592584", "/templates/neighborhood-story/", "template"],
    ["9c9d80f8c5ede189f69aae04", "/templates/property-showcase/", "template"],
  ];
  const languages = ["en", "de", "es", "fr", "ru"];
  const results = [];

  async function loadArticleImages() {
    const articleImages = page.locator(".article-hero img,.article-figure img");
    for (let index = 0; index < await articleImages.count(); index += 1) {
      await articleImages.nth(index).scrollIntoViewIfNeeded();
      await articleImages.nth(index).evaluate(async (image) => {
        if (image.naturalWidth > 0) {
          await image.decode().catch(() => {});
          return;
        }
        await new Promise((resolve) => {
          image.addEventListener("load", resolve, { once: true });
          image.addEventListener("error", resolve, { once: true });
          setTimeout(resolve, 10000);
        });
        await image.decode().catch(() => {});
      });
    }
    await page.evaluate(() => scrollTo(0, 0));
  }

  async function inspect(job, language, viewport) {
    const [id, path, type] = job;
    const query = language === "en" ? "" : `?lang=${language}`;
    const url = `https://georivo.com/content-preview/${id}${query}`;
    await page.setViewportSize(viewport);
    const response = await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
    await loadArticleImages();
    await page.waitForTimeout(150);
    const metrics = await page.evaluate(({ expectedType, expectedLanguage }) => {
      const images = [...document.querySelectorAll(".article-hero img,.article-figure img")];
      const metaRobots = document.querySelector('meta[name="robots"]')?.content || "";
      return {
        statusTitle: document.title,
        language: document.documentElement.lang,
        expectedLanguage,
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        header: Boolean(document.querySelector("header.nav")),
        footer: Boolean(document.querySelector("footer")),
        toc: Boolean(document.querySelector(".article-toc")),
        figures: document.querySelectorAll(".article-figure").length,
        faq: document.querySelectorAll(".article-faq details").length,
        recommended: document.querySelectorAll(".recommended-card").length,
        trust: Boolean(document.querySelector(".article-trust")),
        cta: Boolean(document.querySelector('[data-event="seo_cta_click"]')),
        previewNoindex: /noindex/i.test(metaRobots),
        imageCount: images.length,
        brokenImages: images.filter((image) => image.naturalWidth < 1).map((image) => image.src),
        contentNotice: Boolean(document.querySelector(".content-notice")),
        expectedNotice: expectedType === "example" || expectedType === "integration_guide",
      };
    }, { expectedType: type, expectedLanguage: language });
    const errors = [];
    if (!response || response.status() !== 200) errors.push(`HTTP ${response?.status() || "none"}`);
    if (!metrics.statusTitle) errors.push("missing title");
    if (metrics.language !== language) errors.push(`html lang ${metrics.language}`);
    if (metrics.overflow > 2) errors.push(`horizontal overflow ${metrics.overflow}px`);
    if (!metrics.header) errors.push("native header missing");
    if (!metrics.footer) errors.push("native footer missing");
    if (!metrics.toc) errors.push("TOC missing");
    if (metrics.figures !== 3) errors.push(`figures ${metrics.figures}`);
    if (metrics.faq < 5) errors.push(`FAQ ${metrics.faq}`);
    if (metrics.recommended !== 3) errors.push(`Recommended next ${metrics.recommended}`);
    if (!metrics.trust) errors.push("trust block missing");
    if (!metrics.cta) errors.push("CTA analytics missing");
    if (!metrics.previewNoindex) errors.push("preview is indexable");
    if (metrics.imageCount !== 4) errors.push(`article images ${metrics.imageCount}`);
    if (metrics.brokenImages.length) errors.push(`broken images ${metrics.brokenImages.length}`);
    if (metrics.expectedNotice && !metrics.contentNotice) errors.push("required disclosure notice missing");
    return { id, path, type, language, viewport: `${viewport.width}x${viewport.height}`, errors };
  }

  for (const job of jobs) {
    for (const language of languages) {
      results.push(await inspect(job, language, { width: 1440, height: 1000 }));
    }
    results.push(await inspect(job, "en", { width: 390, height: 844 }));
  }

  const representative = [
    jobs.find((job) => job[2] === "guide"),
    jobs.find((job) => job[2] === "template"),
    jobs.find((job) => job[2] === "example"),
    jobs.find((job) => job[2] === "integration_guide"),
  ];
  for (const job of representative) {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(`https://georivo.com/content-preview/${job[0]}`, { waitUntil: "networkidle" });
    await loadArticleImages();
    await page.screenshot({
      path: `output/playwright/georivo/${job[2]}-desktop.png`,
      fullPage: true,
    });
  }
  const failedChecks = results.filter((item) => item.errors.length);
  const failedPages = new Set(failedChecks.map((item) => item.id)).size;
  return JSON.stringify({
    passed: failedChecks.length === 0,
    expectedPages: jobs.length,
    checks: results.length,
    failedPages,
    failedChecks,
  });
}
