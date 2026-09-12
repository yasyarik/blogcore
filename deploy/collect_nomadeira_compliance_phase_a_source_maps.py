#!/usr/bin/env python3
"""Collect bounded primary-source maps for NOMADeira Phase A.

This is deliberately a research-import tool, not a verifier or generator.  A
map records what an official page may support, its recheck deadline and the
claim boundary.  It never changes a claim to VERIFIED, makes a draft or clears
the Tier-B publication block.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

SITE_ID = 18
DB_PATH = Path("data/blog_core.sqlite3")
REVISION = "2026-09-01-phase-a-sources-v3"
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
EXPIRES = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(timespec="seconds")


def ref(id, title, publisher, url, supports):
    return {"id": id, "title": title, "publisher": publisher, "publicUrl": url,
            "supports": supports, "accessedAt": NOW, "freshness": "fortnightly",
            "expiresAt": EXPIRES, "rightsState": "citation_only",
            "sourceClass": "current_law_or_responsible_authority"}


S = {
"madeira-nif-bank-account-order": [
 ref("gov-nif-person", "Request an individual NIF", "gov.pt / AT", "https://www.gov.pt/servicos/pedir-o-numero-de-identificacao-fiscal-para-pessoa-singular?lang=pt", "NIF request scope and authority only; does not establish a bank onboarding sequence."),
 ref("at-nif-nonresident", "NIF for foreign non-residents", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Folhetos_informativos/Documents/Atribuicao_de_NIF_a_cidadaos_estrangeiros_nao_residentes.pdf", "Non-resident NIF procedure and representation-document boundaries only."),
 ref("gov-fiscal-representative", "Appoint a fiscal representative", "gov.pt / AT", "https://www.gov.pt/servicos/nomear-representante-fiscal", "Representative scope and limits; not a guarantee of NIF or bank-account approval.")],
"nif-portugal-through-representative": [
 ref("gov-nif-person", "Request an individual NIF", "gov.pt / AT", "https://www.gov.pt/servicos/pedir-o-numero-de-identificacao-fiscal-para-pessoa-singular?lang=pt", "NIF applicant scope and responsible authority."),
 ref("gov-fiscal-representative", "Appoint a fiscal representative", "gov.pt / AT", "https://www.gov.pt/servicos/nomear-representante-fiscal", "Who may appoint or act as fiscal representative, with non-resident boundaries."),
 ref("at-nif-nonresident", "NIF for foreign non-residents", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Folhetos_informativos/Documents/Atribuicao_de_NIF_a_cidadaos_estrangeiros_nao_residentes.pdf", "Power-of-attorney and translation circumstances in the official procedure.")],
"change-fiscal-address-portugal": [
 ref("at-faq-fiscal-address", "Fiscal address FAQ", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/questoes_frequentes/Pages/faqs-00303.aspx", "Official fiscal-address change scope and confirmation boundary."),
 ref("at-change-address", "Change of address", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Dados_pessoais_familia/Dados_pessoais/Morada/Paginas/default.aspx", "Available address-change channels and confirmation process."),
 ref("at-foreign-address", "Address change for foreign citizens", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Folhetos_informativos/Documents/Alteracao_morada_cidadaos_estrangeiros.pdf", "Foreign-citizen procedural documents and boundaries.")],
"madeira-crue-eu-residence-certificate": [
 ref("gov-crue-current", "EU/EEA/Swiss registration certificate", "gov.pt", "https://www.gov.pt/servicos/pedir-o-certificado-de-registo-para-cidadao-da-ue-eee-suica", "Over-three-month registration-certificate scope, deadline wording and municipality responsibility; recheck current notice."),
 ref("aima-eu-family", "EU nationals and family members", "AIMA", "https://aima.gov.pt/pt/nacionais-ue-e-familiares", "AIMA boundary: the EU citizen registration certificate is municipal, not a generic AIMA process.")],
"eu-citizen-non-eu-family-madeira": [
 ref("aima-eu-family", "Family members of EU nationals", "AIMA", "https://aima.gov.pt/pt/nacionais-ue-e-familiares/familiares-de-nacionais-ue", "Current AIMA route scope for non-EU family members of EU nationals."),
 ref("aima-appointments", "AIMA appointment information", "AIMA", "https://aima.gov.pt/pt/noticias/agendamento", "Official pre-booking evidence categories; appointment availability is not guaranteed."),
 ref("aima-eu-family-general", "EU nationals and family members", "AIMA", "https://aima.gov.pt/pt/nacionais-ue-e-familiares", "Authority boundary for the EU-national and family-member route; it must not override the route-specific AIMA page.")],
"portugal-d7-visa-madeira": [
 ref("gov-own-income-visa", "Residence visa for own-income applicants", "gov.pt", "https://www.gov.pt/servicos/pedir-um-visto-de-residencia-para-fixacao-de-residencia-de-reformados-religiosos-e-pessoas-que-vivem-de-rendimentos-proprios", "Official own-income route scope, consular application and document categories; nickname does not establish eligibility."),
 ref("aima-residence", "Residence information", "AIMA", "https://aima.gov.pt/pt/viver", "Current authority boundary for post-arrival residence information; consult the route-specific page before use.")],
"portugal-d8-visa-remote-employee": [
 ref("dr-remote-visa", "Decree 4/2022, Article 31-A", "Diário da República", "https://files.diariodarepublica.pt/gratuitos/1s/2022/09/19000.pdf", "Remote-work residence-visa evidence, including employee relationship and relative income threshold."),
 ref("aima-remote", "Remote professional activity residence authorisation", "AIMA", "https://aima.gov.pt/pt/trabalhar/autorizacao-de-residencia-para-o-exercicio-de-atividade-profissional-prestada-de-forma-remota-com-visto-de-residencia-para-o-exe", "Post-arrival documents and current channel wording only.")],
"portugal-d8-visa-freelancer": [
 ref("dr-remote-visa", "Decree 4/2022, Article 31-A", "Diário da República", "https://files.diariodarepublica.pt/gratuitos/1s/2022/09/19000.pdf", "Independent remote-work evidence categories and relative income threshold."),
 ref("aima-remote", "Remote professional activity residence authorisation", "AIMA", "https://aima.gov.pt/pt/trabalhar/autorizacao-de-residencia-para-o-exercicio-de-atividade-profissional-prestada-de-forma-remota-com-visto-de-residencia-para-o-exe", "Post-arrival documents and current channel wording only.")],
"portugal-d2-visa-freelancer-entrepreneur": [
 ref("gov-independent-entrepreneur-visa", "Residence visa for independent activity or entrepreneurs", "gov.pt", "https://www.gov.pt/servicos/pedir-visto-de-residencia-para-o-exercicio-de-atividade-profissional-independente-ou-para-imigrantes-empreendedores", "Official route scope and consular application boundary."),
 ref("aima-independent", "Independent professional activity with residence visa", "AIMA", "https://aima.gov.pt/pt/trabalhar/autorizacao-de-residencia-para-exercicio-de-atividade-profissional-independente-com-visto-de-residencia-art-89-o-n-o1", "Post-arrival authority and evidence scope.")],
"aima-after-arrival-portugal": [
 ref("aima-remote", "Remote professional activity residence authorisation", "AIMA", "https://aima.gov.pt/pt/trabalhar/autorizacao-de-residencia-para-o-exercicio-de-atividade-profissional-prestada-de-forma-remota-com-visto-de-residencia-para-o-exe", "Example route-specific post-arrival evidence; not a universal AIMA list."),
 ref("aima-independent", "Independent professional activity with residence visa", "AIMA", "https://aima.gov.pt/pt/trabalhar/autorizacao-de-residencia-para-exercicio-de-atividade-profissional-independente-com-visto-de-residencia-art-89-o-n-o1", "Independent route post-arrival scope; route selection remains applicant-specific."),
 ref("aima-appointments", "AIMA appointment information", "AIMA", "https://aima.gov.pt/pt/noticias/agendamento", "Appointment instructions may change; no booking outcome may be promised.")],
"open-activity-portugal-freelancer": [
 ref("at-start-activity", "Start of activity", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Atividade_profissional/Declaracoes_de_atividade/Inicio_de_atividade/Paginas/default.aspx", "Official conditions and declaration fields."),
 ref("gov-self-employed-ss", "Self-employed Social Security registration", "gov.pt / Segurança Social", "https://www.gov.pt/servicos/trabalhador-independente-inscricao-na-seguranca-social", "Automatic registration scope after relevant Finanças opening only.")],
"recibos-verdes-first-invoice": [
 ref("gov-self-employed-tax", "Self-employed tax obligations", "gov.pt", "https://www.gov.pt/guias/trabalhar-por-conta-propria-guia-para-trabalhadores-independentes/obrigacoes-fiscais-e-pagamentos-impostos-e-contribuicoes", "Official distinction between invoice, invoice-receipt and receipt; not personal tax advice."),
 ref("at-invoice-receipt-guide", "Invoice-receipt user guide", "Autoridade Tributária", "https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Manuais/Documents/Guia_utilizacao_Fatura_Recibo.pdf", "Portal procedure terminology and document-stage distinction.")],
}


def main():
    if not DB_PATH.exists(): raise SystemExit(f"Missing {DB_PATH}")
    updated = []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        for slug, refs in S.items():
            row = conn.execute("select * from content_jobs where site_id=? and slug=?", (SITE_ID, slug)).fetchone()
            if not row: raise SystemExit(f"Missing Phase-A job: {slug}")
            payload = json.loads(row["sources_json"] or "{}")
            cluster = payload.get("complianceCluster") or {}
            existing = cluster.get("sourceMap") if isinstance(cluster.get("sourceMap"), dict) else {}
            if existing.get("revision") == REVISION: continue
            cluster.update({"workflowState": "SOURCES_COLLECTED", "nextState": "CLAIMS_VERIFIED",
                            "sourceMap": {"revision": REVISION, "collectedAt": NOW, "sources": refs},
                            "mediaGeneration": "deferred",
                            "claimProposals": [{"id": f"{slug}-source-{x['id']}", "sourceIds": [x['id']], "scope": x['supports'], "approvalState": "PROPOSED"} for x in refs],
                            "claimIds": [],
                            "evidenceGate": "OPEN: Tier B reviewer must verify each proposed atomic claim against the current primary source."})
            payload["complianceCluster"] = cluster
            payload["generationBlockedUntilSourceReview"] = True
            payload["publicationBlocked"] = True
            conn.execute("update content_jobs set status='SOURCES_COLLECTED', sources_json=?, error=?, scheduled_for=null, updated_at=? where id=?", (json.dumps(payload, ensure_ascii=False), "Primary source map collected; claim verification and Tier B review required.", NOW, row["id"]))
            conn.execute("insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)", (SITE_ID, row["id"], NOW, "INFO", "sources_collected", "Official source map collected; no claim verification, drafting, scheduling or publication was performed."))
            updated.append(slug)
    print(json.dumps({"updated": updated, "count": len(updated), "revision": REVISION}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
