"""Data-driven, read-only strategy presentation for any native client calendar."""

from datetime import timedelta
from html import escape


def _list(values):
    return "<ul>" + "".join(f"<li>{escape(str(value))}</li>" for value in values) + "</ul>"


def render_growth_strategy(strategy, start, connected_channels):
    if not isinstance(strategy, dict) or not strategy.get("revision"):
        return ""
    sections = []
    sections.append("<section><h3>Для кого и зачем подписываться</h3>" +
                    "".join(f"<p>{escape(str(strategy.get(key) or ''))}</p>" for key in ("positioning", "priority", "followReason")) + "</section>")
    readiness = ("Есть подключения площадок. Доступ к аналитике, права доставки и оформление профилей нужно проверять отдельно."
                 if connected_channels else "Соцаккаунты ещё не подключены к Blog Core. Публикация через фабрику и автоматический сбор соцметрик не подтверждены.")
    sections.append("<section><h3>Готовность запуска</h3><p class='growth-readiness'>" + escape(readiness) +
                    "</p>" + _list(strategy.get("profileChecks", [])) +
                    "<details><summary>Черновик описания профиля, не опубликован</summary><p style='white-space:pre-line'>" +
                    escape(str(strategy.get("profileDraft") or "")) + "</p></details></section>")
    sections.append("<section><h3>Проверка перед выпуском</h3>" + _list(strategy.get("productionChecks", [])) + "</section>")
    sections.append("<section><h3>Ответы и общение</h3>" + _list(strategy.get("community", [])) + "</section>")
    reviews = []
    for review in strategy.get("reviews", []):
        if not isinstance(review, dict) or review.get("day") not in (7, 14, 21, 30):
            continue
        day = int(review["day"])
        when = (start + timedelta(days=day - 1)).strftime("%d.%m.%Y")
        reviews.append(f"<li><strong>{when} · день {day}</strong><p>{escape(str(review.get('focus') or ''))}</p></li>")
    sections.append("<section><h3>Разбор результатов</h3><p>" + escape(str(strategy.get("reviewOwner") or "")) +
                    "</p><p>Контрольные даты, не автоматически запущенные отчёты. Они пересчитываются при переносе старта.</p><ol class='growth-reviews'>" +
                    "".join(reviews) + "</ol></section>")
    sections.append("<section><h3>Что измерять</h3>" + _list(strategy.get("measurement", [])) + "</section>")
    sections.append("<section><h3>Как менять следующую неделю</h3>" + _list(strategy.get("decisions", [])) + "</section>")
    return ("<details class='growth-plan'><summary>Стратегия роста и проверка запуска"
            "<small>Аудитория · качество · контрольные даты · измерение</small></summary><div class='growth-body'>" +
            "".join(sections) + "</div></details>")


def render_growth_brief(growth):
    if not isinstance(growth, dict) or not growth.get("revision"):
        return ""
    fields = (("audience", "Для кого"), ("audienceNeed", "Задача зрителя"), ("series", "Повторяемая серия / формат"),
              ("hypothesis", "Что проверяем"), ("primarySignal", "Главный сигнал"), ("secondarySignal", "Дополнительно"))
    rows = "".join(f"<p><b>{label}:</b> {escape(str(growth.get(field) or ''))}</p>" for field, label in fields)
    return ("<div class='detail-block wide'><details><summary style='cursor:pointer;font-weight:750'>"
            "Аудитория и проверка результата</summary>" + rows +
            "<p>Это гипотеза, не обещание охвата. Метрики появятся только по фактической публикации; отсутствие данных не равно нулю.</p></details></div>")


GROWTH_CSS = """
.growth-plan{margin:14px 0 22px;border:1px solid var(--line);border-radius:16px;background:var(--card);color:var(--ink)}
.growth-plan>summary{cursor:pointer;padding:15px 20px;font-size:15px;font-weight:750}
.growth-plan>summary small{display:block;padding-top:5px;color:var(--muted);font-size:12px;font-weight:400}
.growth-plan summary:focus-visible{outline:2px solid var(--accent2);outline-offset:3px;border-radius:8px}
.growth-body{padding:0 20px 20px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 28px;font-size:14px;line-height:1.55}
.growth-body section{min-width:0;overflow-wrap:anywhere}.growth-body h3{font:750 16px/1.3 Inter,Arial,sans-serif;margin:18px 0 10px}
.growth-body p{margin:8px 0}.growth-body ul,.growth-body ol{padding-left:20px}.growth-body li{margin-bottom:12px}
.growth-body .growth-readiness{padding:12px;border-left:3px solid var(--accent2);background:var(--paper)}
@media(max-width:700px){.growth-body{grid-template-columns:1fr;padding:0 14px 14px;gap:0;font-size:13px}.growth-plan>summary{padding:12px 14px;font-size:14px}.growth-plan>summary small{font-size:11px}}
"""
