#!/usr/bin/env python3
"""Store current primary-source maps for the first NOMADeira compliance pilots.

This collector intentionally creates claim *proposals*, not approved claims or
drafts.  It only advances a protected content job from BLOCKED_EVIDENCE to
SOURCES_COLLECTED after preserving primary-source scope and expiry metadata.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


SITE_ID = 18
DB_PATH = Path("data/blog_core.sqlite3")
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
EXPIRES = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(timespec="seconds")


def source(source_id, title, publisher, url, supports, freshness="monthly"):
    return {
        "id": source_id,
        "title": title,
        "publisher": publisher,
        "publicUrl": url,
        "accessedAt": NOW,
        "freshness": freshness,
        "expiresAt": EXPIRES,
        "supports": supports,
        "rightsState": "citation_only",
        "sourceClass": "current_law_or_responsible_authority",
    }


PILOTS = {
    "nif-portugal-through-representative": {
        "sources": [
            source("gov-nif-person", "Pedir o Número de Identificação Fiscal (NIF) para pessoa singular", "gov.pt / Autoridade Tributária e Aduaneira", "https://www.gov.pt/servicos/pedir-o-numero-de-identificacao-fiscal-para-pessoa-singular?lang=pt", "Who may request a NIF and the service authority; use only for NIF-request scope, not bank or residence eligibility."),
            source("gov-fiscal-representative", "Nomear representante fiscal", "gov.pt / Autoridade Tributária e Aduaneira", "https://www.gov.pt/servicos/nomear-representante-fiscal", "Who may appoint a fiscal representative, who may act as representative, and non-resident timing; do not generalise the rule beyond the listed applicant classes."),
            source("at-nif-nonresident-pdf", "Número de identificação fiscal para cidadãos estrangeiros - não residentes", "Autoridade Tributária e Aduaneira", "https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Folhetos_informativos/Documents/Atribuicao_de_NIF_a_cidadaos_estrangeiros_nao_residentes.pdf", "Representation documents and non-resident procedure boundaries, including circumstances where a power of attorney or certified translation is relevant."),
        ],
        "proposals": [
            {"id": "nif-rep-001", "statement": "A foreign person, resident or non-resident in Portugal, may request a NIF; the responsible authority is Autoridade Tributária e Aduaneira.", "sourceIds": ["gov-nif-person"], "scope": "individual NIF request", "conditions": "Does not apply where a Portuguese citizen already has a NIF through a Citizen Card.", "exceptions": "This statement does not establish immigration, tax-residence, bank-account or representation eligibility.", "riskClass": "tax", "status": "PROPOSED"},
            {"id": "nif-rep-002", "statement": "A non-resident foreign person who wants to request a NIF may appoint a fiscal representative; a representative may be an individual or legal entity with Portuguese tax residence or registered office.", "sourceIds": ["gov-fiscal-representative"], "scope": "non-resident foreign NIF applicants", "conditions": "Use the authority's listed applicant classes and current appointment channel.", "exceptions": "Do not state that representation guarantees NIF issuance or is mandatory for every non-resident situation.", "riskClass": "tax", "status": "PROPOSED"},
            {"id": "nif-rep-003", "statement": "Where the non-resident cannot attend with the representative, the authority's non-resident guidance describes representation evidence such as a power of attorney; foreign-language documents may require certified translation.", "sourceIds": ["at-nif-nonresident-pdf"], "scope": "documented non-resident representation procedure", "conditions": "Apply only to the procedure and document circumstance described by the authority.", "exceptions": "Do not turn this into a universal document list or promise acceptance of a particular power of attorney.", "riskClass": "tax", "status": "PROPOSED"},
        ],
    },
    "portugal-d8-visa-remote-employee": {
        "sources": [
            source("dr-remote-residence-visa", "Decreto Regulamentar n.º 4/2022, Article 31-A", "Diário da República", "https://files.diariodarepublica.pt/gratuitos/1s/2022/09/19000.pdf", "Legal document categories for the remote-work residence-visa application, including subordinate-work evidence, income-period threshold expression and tax-residence document."),
            source("aima-remote-residence", "Autorização de Residência para o Exercício de atividade profissional prestada de forma remota", "AIMA", "https://aima.gov.pt/pt/trabalhar/autorizacao-de-residencia-para-o-exercicio-de-atividade-profissional-prestada-de-forma-remota-com-visto-de-residencia-para-o-exe", "Current post-arrival residence-authorisation document list, application-channel wording and stated validity; channel availability must be checked again immediately before publication."),
            source("acm-remote-work-brochure", "Lei de Estrangeiros: O Que Mudou", "Alto Comissariado para as Migrações", "https://www.acm.gov.pt/documents/10181/0/Brochura-Lei-de-Estrangeiros-O-Que-Mudou.pdf/15b8aa63-9ebe-4efe-846b-0e5273957e5a", "Official explanatory cross-check of different evidence routes for subordinate and independent remote work; it does not replace the law or current AIMA channel."),
        ],
        "proposals": [
            {"id": "d8-employee-001", "statement": "For the remote-work residence-visa route, a subordinate worker must provide either a work contract or an employer statement proving the employment relationship.", "sourceIds": ["dr-remote-residence-visa"], "scope": "subordinate professional activity performed remotely for an entity outside Portugal", "conditions": "The legal route and applicant's facts must match Article 31-A.", "exceptions": "Do not apply the subordinate-worker evidence list to freelancers or claim it alone secures a visa.", "riskClass": "immigration", "status": "PROPOSED"},
            {"id": "d8-employee-002", "statement": "The legal text requires proof of average monthly income from the last three months at least equal to four guaranteed minimum monthly remunerations, plus a document proving tax residence.", "sourceIds": ["dr-remote-residence-visa"], "scope": "remote-work residence-visa application", "conditions": "The monetary reference must be rechecked against the applicable current remuneration before publication.", "exceptions": "Do not convert the relative threshold into an evergreen euro amount or treat it as the only eligibility condition.", "riskClass": "immigration", "status": "PROPOSED"},
            {"id": "d8-employee-003", "statement": "AIMA lists a valid remote-work residence visa, passport, evidence of the employment relationship and residence-address evidence among the post-arrival residence-authorisation documents.", "sourceIds": ["aima-remote-residence"], "scope": "post-arrival residence-authorisation stage for a valid visa holder", "conditions": "AIMA's current appointment or electronic-channel wording must be rechecked on the publication date.", "exceptions": "Do not present an appointment, platform availability or residence authorisation as guaranteed.", "riskClass": "immigration", "status": "PROPOSED"},
        ],
    },
    "open-activity-portugal-freelancer": {
        "sources": [
            source("gov-open-activity", "Abrir atividade nas finanças", "gov.pt / Autoridade Tributária e Aduaneira", "https://www2.gov.pt/pt/servicos/abrir-atividade-nas-financas", "Current opening channels, timing, authentication/documents and stated fees for an individual activity declaration."),
            source("at-start-activity", "Início de atividade", "Autoridade Tributária e Aduaneira", "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Atividade_profissional/Declaracoes_de_atividade/Inicio_de_atividade/Paginas/default.aspx", "Official detailed conditions, channels and declaration fields for habitual independent professional activity."),
            source("gov-self-employed-ss", "Trabalhador independente - inscrição na Segurança Social", "gov.pt / Instituto da Segurança Social", "https://www.gov.pt/servicos/trabalhador-independente-inscricao-na-seguranca-social", "Social Security registration relationship to the Finanças opening process; use only for the service's stated automatic registration scope."),
        ],
        "proposals": [
            {"id": "activity-001", "statement": "A self-employed worker, including one carrying out an extra activity alongside employment, must submit a declaration of commencement of activity to Finanças before starting self-employed activity, no later than the stated start date.", "sourceIds": ["gov-open-activity", "at-start-activity"], "scope": "habitual independent professional or business activity", "conditions": "The precise facts, activity code and tax regime still require the taxpayer's correct declaration.", "exceptions": "Do not apply this proposition to every isolated transaction or imply personalised tax advice.", "riskClass": "tax", "status": "PROPOSED"},
            {"id": "activity-002", "statement": "The authority lists online submission through Portal das Finanças and in-person channels; required authentication or documents differ by channel.", "sourceIds": ["gov-open-activity", "at-start-activity"], "scope": "individual opening-of-activity declaration", "conditions": "Check the channel and documentation chosen by the applicant.", "exceptions": "Do not say that every individual can use every channel or that a channel remains available without a current check.", "riskClass": "tax", "status": "PROPOSED"},
            {"id": "activity-003", "statement": "gov.pt states that a self-employed worker's Social Security registration is made automatically by Finanças services.", "sourceIds": ["gov-self-employed-ss"], "scope": "Social Security registration following the relevant Finanças activity opening", "conditions": "Apply only to the service's stated registration scope.", "exceptions": "Do not imply that every contribution, declaration, exemption or cross-border social-security question is resolved automatically.", "riskClass": "tax", "status": "PROPOSED"},
        ],
    },
}


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Blog Core database not found: {DB_PATH}")
    changed = []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        for slug, research in PILOTS.items():
            row = conn.execute("select id, status, sources_json from content_jobs where site_id=? and slug=?", (SITE_ID, slug)).fetchone()
            if not row:
                raise SystemExit(f"Missing Phase-A job: {slug}")
            payload = json.loads(row["sources_json"] or "{}")
            compliance = payload.get("complianceCluster") or {}
            if compliance.get("workflowState") not in {"CANONICAL_CHECKED", "SOURCES_COLLECTED"}:
                raise SystemExit(f"Unexpected workflow state for {slug}: {compliance.get('workflowState')}")
            current = compliance.get("sourceMap") or {}
            if current.get("revision") == "2026-09-01-pilots-v1":
                continue
            compliance.update({
                "workflowState": "SOURCES_COLLECTED",
                "nextState": "CLAIMS_VERIFIED",
                "sourceMap": {"revision": "2026-09-01-pilots-v1", "collectedAt": NOW, "sources": research["sources"]},
                "claimProposals": research["proposals"],
                "claimIds": [],
                "evidenceGate": "OPEN: claim proposals require human verification of scope, conditions, exceptions and current source status.",
            })
            payload["complianceCluster"] = compliance
            payload["generationBlockedUntilSourceReview"] = True
            payload["publicationBlocked"] = True
            conn.execute("update content_jobs set status=?, sources_json=?, error=?, updated_at=? where id=?", ("SOURCES_COLLECTED", json.dumps(payload, ensure_ascii=False), "Primary source map collected; claim verification and Tier B review required.", NOW, row["id"]))
            conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (SITE_ID, row["id"], NOW, "info", "sources_collected", "Official primary-source map and unverified claim proposals collected; no drafting or publication allowed."))
            changed.append(slug)
    print(json.dumps({"updated": changed, "count": len(changed)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
