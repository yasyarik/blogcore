import json
import sqlite3


DATABASE = "/var/www/blog.yas.ooo/data/blog_core.sqlite3"
JOB_ID = "0f38187dd1ac353268bc4b68"


conn = sqlite3.connect(DATABASE)
row = conn.execute("select sources_json from content_jobs where id=?", (JOB_ID,)).fetchone()
if not row:
    raise SystemExit("NOMADeira content job not found")

payload = json.loads(row[0] or "{}")
brief = payload.setdefault("pageBrief", {})
details = brief.setdefault("contentDetails", {})
details["evidenceLedger"] = [
    "DREM, using Statistics Portugal data, reports 13.65 euros per square metre as the observed median for 317 registered new family-dwelling lease agreements in Funchal in Q1 2026. It is not a regulated rate or an asking-price index. A 50 square metre multiplication is illustrative only.",
    "Cowork Funchal listed flex packs before VAT: 12 euros per day, 40 euros per week and 100 euros per month; fixed desk 130 euros per month. Attribute prices to the provider and state the check date.",
    "Horarios do Funchal lists the ordinary 30-day pass at 40 euros municipal and 50 euros intermunicipal. Passe Social Base is a distinct eligibility-dependent product at 30 euros and 40 euros. Use the ordinary pass for safe newcomer planning and tell readers to verify social-tariff eligibility.",
    "The remote-work residence route has two different stages: apply for the residence visa through the competent Portuguese consulate before moving, then apply for the residence permit through AIMA after entry. Never merge the authorities or document lists.",
    "A Portuguese consular remote-work residence-visa checklist lists passport and application materials, travel insurance, criminal-record evidence, accommodation, proof of remote employment or services, tax residence and average monthly income over the previous three months equal to at least four Portuguese minimum monthly wages. Requirements are jurisdiction-specific, so readers must use the checklist of their competent consular post.",
    "Portugal's official 2026 national minimum monthly wage is 920 euros. Four times that amount is 3,680 euros. Present 3,680 euros only as the derived 2026 D8 planning threshold and require a fresh check with the competent consulate before applying.",
    "For the post-entry AIMA remote-work residence permit, the listed documents include a valid passport, the appropriate remote-work residence visa, evidence of remote employment or services, a sworn Portuguese address declaration and evidence of the applicant's legal basis for occupying that address.",
    "For EU, EEA and Swiss nationals staying longer than three months, AIMA says the registration certificate is requested at the municipality within 30 days after the first three months. The official page gives alternative conditions based on work or self-employment, or sufficient resources and health insurance where applicable, or study plus the stated supporting conditions.",
    "AIMA's general residence-permit requirements list health insurance or evidence of SNS coverage and tax registration where applicable. Do not imply that this general page replaces the route-specific or consular checklist.",
    "For internet, coverage and offered service are address-specific; use the MEO address checker rather than an island-wide speed promise.",
    "Use Banana House room prices of 997 to 1,327 euros only as a dated operator-specific coliving range with its listed inclusions, not as an island-wide monthly budget. Build a transparent planning budget from separately sourced categories and label omissions instead of presenting a false total.",
]

existing = {
    str(item.get("id") or ""): item
    for item in brief.get("sourceReferences", [])
    if isinstance(item, dict)
}

existing["drem-funchal-rent-q1-2026"]["supports"] = (
    "DREM, based on Statistics Portugal data, reports 13.65 euros per square metre as the observed median "
    "for 317 registered new family-dwelling lease agreements in Funchal in Q1 2026. This is not a regulated "
    "rate or an asking-price index. A 50 square metre multiplication is illustrative only."
)
existing["hf-fares-2026"]["supports"] = (
    "The operator tariff document lists the ordinary 30-day pass at 40 euros municipal and 50 euros "
    "intermunicipal. Passe Social Base is a separate eligibility-dependent tariff at 30 euros municipal and "
    "40 euros intermunicipal. Newcomers must verify eligibility before budgeting the social tariff."
)
existing["aima-remote-work"]["supports"] = (
    "This is the post-entry residence-permit stage, not the consular visa application. AIMA lists a valid "
    "passport, the appropriate remote-work residence visa, evidence of remote employment or services, a sworn "
    "Portuguese address declaration and evidence of the legal basis for occupying that address."
)

new_sources = [
    {
        "id": "consulate-remote-work-residence-visa",
        "title": "Portuguese Consulate: residence visa for remote work checklist",
        "publisher": "Consulate-General of Portugal / VFS Global",
        "publicUrl": "https://visa.vfsglobal.com/one-pager/portugal/india/english/pdf/dr-goa-checklist-sep-25.pdf",
        "accessedAt": "2026-08-25",
        "supports": "A jurisdiction-specific Portuguese consular checklist separates the residence visa before entry from the later AIMA residence permit. It lists travel insurance, criminal-record evidence, accommodation, remote employment or services, tax residence and average monthly income for the previous three months equal to at least four Portuguese minimum monthly wages. Applicants must check their own competent consular post.",
    },
    {
        "id": "portugal-minimum-wage-2026",
        "title": "Portugal national minimum wage in 2026",
        "publisher": "gov.pt",
        "publicUrl": "https://www.gov.pt/guias/trabalhar-em-portugal",
        "accessedAt": "2026-08-25",
        "supports": "The official government guide states that Portugal's national minimum monthly wage is 920 euros in 2026. Four times 920 euros is 3,680 euros; this derived D8 planning threshold must be rechecked when the wage or consular rules change.",
    },
    {
        "id": "aima-eu-registration",
        "title": "AIMA: registration certificate for EU nationals",
        "publisher": "AIMA",
        "publicUrl": "https://aima.gov.pt/pt/nacionais-ue-e-familiares/nacionais-ue/certificado-de-registo-para-nacionais-ue",
        "accessedAt": "2026-08-25",
        "supports": "For EU, EEA and Swiss nationals staying longer than three months, AIMA says to apply at the municipality within 30 days after the first three months. The page states alternative conditions based on work or self-employment, sufficient resources and health insurance where applicable, or study with the listed conditions.",
    },
    {
        "id": "aima-general-residence-requirements",
        "title": "AIMA: general residence-permit requirements",
        "publisher": "AIMA",
        "publicUrl": "https://aima.gov.pt/pt/viver/autorizacao-de-residencia-regime-e-requisitos-gerais-art-o-77-o-n-o-1",
        "accessedAt": "2026-08-25",
        "supports": "AIMA's general residence-permit page lists health insurance or evidence of SNS coverage and tax registration where applicable, alongside address and other general requirements. It does not replace the route-specific remote-work page or a consular visa checklist.",
    },
]
for source in new_sources:
    existing[source["id"]] = source

brief["sourceReferences"] = list(existing.values())
conn.execute(
    "update content_jobs set sources_json=?, updated_at=datetime('now') where id=?",
    (json.dumps(payload, ensure_ascii=False), JOB_ID),
)
conn.commit()
conn.close()
