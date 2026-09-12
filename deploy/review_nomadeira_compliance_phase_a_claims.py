#!/usr/bin/env python3
"""Submit source-bounded Phase-A claims to Blog Core's review endpoint.

Claims are intentionally narrow, use only the live official source-map IDs and
leave publication blocked.  The reviewer identity records that this is an
owner-authorized Codex source review, not advice from an external professional.
"""
from __future__ import annotations

import json
import urllib.request

BASE = "http://127.0.0.1:3299"
SITE_ID = 18
REVIEWER = "Codex official-source reviewer (owner-authorized)"

def claim(id, source_id, statement, excerpt, scope, conditions, exceptions):
    return {"id": id, "sourceIds": [source_id], "statement": statement,
            "supportingExcerpt": excerpt, "scope": scope, "conditions": conditions,
            "exceptions": exceptions, "effectiveDateOrYear": "Current official source checked 2026-09-01"}

CLAIMS = {
 "madeira-nif-bank-account-order": [
  claim("nif-order-1","gov-nif-person","An individual Portuguese or foreign person, resident or non-resident, may request a NIF from the Autoridade Tributária e Aduaneira.","The official NIF service says any Portuguese or foreign person, resident or non-resident, may request the taxpayer number.","individual NIF request","Use the authority's current service channel.","This does not establish a bank-account sequence, residence status or tax residence."),
  claim("nif-order-2","gov-fiscal-representative","A non-resident foreign person seeking a NIF may appoint a fiscal representative; the representative may be an individual or legal entity with Portuguese tax residence or registered office.","The official representative service lists non-resident foreign NIF applicants and a representative with Portuguese tax residence or headquarters.","non-resident NIF request","Apply only to the applicant class described by the service.","Appointment does not guarantee NIF or bank-account approval.")],
 "nif-portugal-through-representative": [
  claim("nif-rep-1","gov-fiscal-representative","Foreign people not resident in Portugal who need a NIF are listed as people who may appoint a fiscal representative.","The service lists foreign people not resident in Portugal who need to request a NIF.","foreign non-resident NIF applicant","Check the current service channel.","This is not a universal rule for every foreign person."),
  claim("nif-rep-2","at-nif-nonresident","The official non-resident NIF guidance covers representation documents and circumstances in which a power of attorney or certified translation may be relevant.","The AT non-resident NIF guidance addresses representation and document treatment.","documented non-resident procedure","Use the document form and language requirements applicable to the case.","It is not a universal document checklist or acceptance guarantee.")],
 "change-fiscal-address-portugal": [
  claim("fiscal-address-1","at-change-address","Autoridade Tributária provides official channels for changing an address and a confirmation process.","The AT address service sets out address-change channels and confirmation.","registered fiscal address change","Use the channel and confirmation stated by the authority.","A fiscal-address change does not itself establish immigration residence or tax residence."),
  claim("fiscal-address-2","at-foreign-address","AT provides separate procedural guidance for address changes by foreign citizens.","The AT foreign-citizen address guide covers that procedure.","foreign-citizen address procedure","Check the current document requirements.","It does not replace route-specific immigration evidence.")],
 "madeira-crue-eu-residence-certificate": [
  claim("crue-1","gov-crue-current","The official registration-certificate page states that an EU/EEA/Swiss/Andorran citizen staying in Portugal for more than three months must request the certificate.","The current service page says the certificate should be requested for a stay over three months.","listed EU/EEA/Swiss/Andorran nationals","Recheck the linked AIMA information because the page itself warns it may be outdated.","This does not determine an individual's right of residence."),
  claim("crue-2","gov-crue-current","The same page states a 30-day period after the first three months of entry.","The service page states 'No prazo de 30 dias após decorridos três meses'.","certificate timing described by that service","Confirm the responsible Madeira municipality and current process.","Do not treat this as a promised appointment or outcome.")],
 "eu-citizen-non-eu-family-madeira": [
  claim("eu-family-1","aima-eu-family","AIMA has a dedicated route for family members of EU nationals.","AIMA's route is explicitly titled for family members of EU nationals.","non-EU family member route","Match the applicant's relationship and route to AIMA's current criteria.","A route page alone does not prove eligibility."),
  claim("eu-family-2","aima-appointments","AIMA appointment information lists route-specific evidence for family members of EU nationals.","AIMA appointment information identifies evidence categories for this group.","AIMA appointment preparation","Recheck appointment availability and documents before action.","No appointment or residence card is guaranteed.")],
 "portugal-d7-visa-madeira": [
  claim("own-income-1","gov-own-income-visa","gov.pt describes a residence-visa service for people living from their own income and directs applicants to the competent consular post.","The official service is for retirees, religious workers and people living from their own income and refers to the competent consular post.","third-country own-income route","Use the competent consulate's current instructions.","The informal label D7 does not itself establish eligibility.")],
 "portugal-d8-visa-remote-employee": [
  claim("remote-employee-1","dr-remote-visa","Article 31-A lists a work contract or employer declaration as evidence of a subordinate remote-work relationship for the residence-visa route.","Article 31-A identifies a contract or employer declaration for subordinate work.","subordinate remote professional activity","The route and applicant facts must match the legal provision.","This evidence alone does not secure a visa."),
  claim("remote-employee-2","aima-remote","AIMA lists a valid remote-work residence visa, passport, relationship evidence and address evidence for the post-arrival residence-authorisation stage.","AIMA's remote-work residence page lists those document categories.","post-arrival stage for a valid visa holder","Check the current AIMA channel before applying.","It does not guarantee an appointment or authorisation.")],
 "portugal-d8-visa-freelancer": [
  claim("remote-freelancer-1","dr-remote-visa","Article 31-A distinguishes evidence for independent remote professional activity from subordinate employment evidence.","The legal text separately addresses independent and subordinate professional activity.","independent remote professional activity","Match service-contract evidence to the applicable legal route.","A visa nickname or foreign client alone does not establish eligibility."),
  claim("remote-freelancer-2","aima-remote","AIMA's remote-work page is a post-arrival residence-authorisation source, not a substitute for the consular visa decision.","The AIMA page is explicitly for residence authorisation with a residence visa.","post-arrival remote-work stage","Use the consular and AIMA stages in their respective roles.","Do not present it as a universal remote-worker checklist.")],
 "portugal-d2-visa-freelancer-entrepreneur": [
  claim("independent-visa-1","gov-independent-entrepreneur-visa","gov.pt describes a residence-visa service for non-EU/EEA/Swiss nationals intending independent activity or investment in Portugal.","The service identifies those applicant categories and the competent consular post.","third-country independent activity or investment","Consult the competent consular post for current submission instructions.","This does not determine business viability or visa approval."),
  claim("independent-visa-2","aima-independent","AIMA provides a route-specific post-arrival page for independent professional activity with a residence visa.","The AIMA page title identifies independent activity with residence visa under Article 89.","post-arrival holder of the relevant visa","Check current AIMA requirements and channel.","It is not a substitute for the consular stage.")],
 "aima-after-arrival-portugal": [
  claim("after-arrival-1","aima-remote","AIMA's remote-work post-arrival requirements are route-specific and apply to a holder of the relevant residence visa.","The AIMA page is explicitly for remote activity with a residence visa.","remote-work visa holder","Use the page only if the route matches.","There is no single universal AIMA document list."),
  claim("after-arrival-2","aima-independent","AIMA publishes separate post-arrival requirements for independent professional activity with a residence visa.","The independent-activity AIMA page is distinct from the remote-work page.","independent-activity visa holder","Choose the route-specific source before preparing documents.","Do not merge route requirements.")],
 "open-activity-portugal-freelancer": [
  claim("activity-1","at-start-activity","Autoridade Tributária provides the official conditions and declaration fields for starting habitual independent professional activity.","The AT start-of-activity page covers conditions, channels and declaration fields.","habitual independent professional activity","Use the taxpayer's correct activity and declaration facts.","This is not individual tax advice or a rule for every isolated transaction."),
  claim("activity-2","gov-self-employed-ss","gov.pt states that Social Security registration for a self-employed worker is automatic through the relevant Finanças opening process.","The service states that registration is made automatically by Finanças services.","the service's stated registration scope","Confirm contribution and cross-border implications separately.","It does not resolve every Social Security obligation.")],
 "recibos-verdes-first-invoice": [
  claim("receipt-1","gov-self-employed-tax","gov.pt distinguishes invoice, invoice-receipt and receipt in the self-employed tax guide.","The official self-employed guide distinguishes the three document forms.","official document terminology","Use the document that matches the actual payment stage.","The choice does not settle all tax obligations."),
  claim("receipt-2","at-invoice-receipt-guide","Autoridade Tributária publishes a user guide for the invoice-receipt function in Portal das Finanças.","AT's guide is specifically for Fatura-Recibo use.","Portal das Finanças document procedure","Check current portal fields and rules.","It is not personalised tax advice.")],
}

def main():
    out=[]
    with urllib.request.urlopen(f"{BASE}/api/sites/{SITE_ID}/content-jobs?per_page=200") as response:
        jobs=json.load(response)["jobs"]
    for slug, claims in CLAIMS.items():
        job=next((item for item in jobs if item.get("slug")==slug),None)
        if not job: raise RuntimeError(f"missing {slug}")
        req=urllib.request.Request(f"{BASE}/api/sites/{SITE_ID}/content-jobs/{job['id']}/compliance-claim-review", data=json.dumps({"reviewer": REVIEWER,"claims":claims}).encode(), headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req) as response: out.append(json.load(response))
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
