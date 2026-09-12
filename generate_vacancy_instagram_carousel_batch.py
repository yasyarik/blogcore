"""Batch-produce one review-only Instagram carousel from an approved YAS vacancy case.

This is intentionally a separate source contour from article carousels.  It
never turns a vacancy tweet into a stack of text screenshots: every slide is
built around a verified job duty, a buildable custom system, its human decision
boundary, and clearly-labelled illustrative economics.
"""
import json, os, time, urllib.parse, urllib.request
from base64 import b64decode, b64encode
from datetime import datetime, timezone
from io import BytesIO

from PIL import Image, ImageOps
from app import (db, now_iso, parse_json_object, _gemini_batch_text_json,
    _official_company_logo_data_uri, _evidence_case_economics, site_logo_reference,
    social_asset_job_dir, social_asset_url)

SITE_ID = 12
SOURCE_POST_ID = int(os.environ.get("VACANCY_X_POST_ID", "159"))
PLAN_SCHEMA = {"type":"object","properties":{"caption":{"type":"string"},"slides":{"type":"array","minItems":7,"maxItems":7,"items":{"type":"object","properties":{"index":{"type":"integer"},"role":{"type":"string"},"headline":{"type":"string","maxLength":64},"subtext":{"type":"string","maxLength":150},"visual":{"type":"string","maxLength":700},"altText":{"type":"string","maxLength":220}},"required":["index","role","headline","subtext","visual","altText"]}}},"required":["caption","slides"]}

def api_key():
    return os.environ.get("GEMINI_IMAGE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]

def batch_images(requests, expected=7, size=(1080,1350), aspect_ratio="4:5"):
    model=os.environ.get("GEMINI_IMAGE_MODEL") or "gemini-3.1-flash-image"
    payload={"batch":{"display_name":f"yas-vacancy-carousel-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}","input_config":{"requests":{"requests":requests}}}}
    url="https://generativelanguage.googleapis.com/v1beta/models/"+urllib.parse.quote(model,safe=".-")+":batchGenerateContent"
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"content-type":"application/json","x-goog-api-key":api_key()},method="POST")
    with urllib.request.urlopen(req,timeout=180) as r: batch=json.loads(r.read().decode())
    name=batch["name"]; print(json.dumps({"stage":"imageBatchCreated","batch":name}),flush=True)
    until=time.monotonic()+7200
    while True:
        req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/"+urllib.parse.quote(name,safe="/"),headers={"x-goog-api-key":api_key()})
        with urllib.request.urlopen(req,timeout=120) as r: batch=json.loads(r.read().decode())
        state=str(batch.get("state") or (batch.get("metadata") or {}).get("state") or "")
        print(json.dumps({"stage":"imageBatchStatus","batch":name,"state":state}),flush=True)
        if state in {"BATCH_STATE_SUCCEEDED","JOB_STATE_SUCCEEDED"}: break
        if state in {"BATCH_STATE_FAILED","BATCH_STATE_CANCELLED","JOB_STATE_FAILED","JOB_STATE_CANCELLED"}: raise RuntimeError(str(batch.get("error") or state))
        if time.monotonic()>until: raise TimeoutError(name)
        time.sleep(20)
    raw=((batch.get("response") or {}).get("inlinedResponses") or (batch.get("output") or {}).get("inlinedResponses") or [])
    if isinstance(raw,dict): raw=raw.get("inlinedResponses") or []
    result={}
    for i,row in enumerate(raw):
        key=str((row.get("metadata") or {}).get("key") or i+1)
        parts=((((row.get("response") or {}).get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
        b64=next((x.get("inlineData",{}).get("data") for x in parts if x.get("inlineData",{}).get("data")),None)
        if not b64: raise RuntimeError(f"No image for slide {key}")
        image=ImageOps.fit(Image.open(BytesIO(b64decode(b64))).convert("RGB"),size,method=Image.Resampling.LANCZOS)
        out=BytesIO(); image.save(out,"JPEG",quality=92,optimize=True,progressive=True); result[int(key)]=out.getvalue()
    if len(result)!=expected: raise RuntimeError(f"Expected {expected} images, received {len(result)}")
    return result,name,model

def main():
    with db() as conn:
        row=conn.execute("select * from social_posts where id=? and site_id=? and asset_type like 'evidence_post_%'",(SOURCE_POST_ID,SITE_ID)).fetchone()
        if not row: raise KeyError("approved vacancy X post not found")
        x=parse_json_object(row["content_json"]).get("twitter") or {}; case_id=int(x["evidenceCaseId"])
        case=conn.execute("""select ec.*,jp.title role,jp.source_url,sb.company_name,sb.company_domain,sb.careers_url
            from evidence_cases ec join evidence_job_postings jp on jp.id=ec.job_posting_id join evidence_source_boards sb on sb.id=jp.source_board_id where ec.id=?""",(case_id,)).fetchone()
    if not case: raise KeyError("evidence case missing")
    economics=_evidence_case_economics(dict(case))["postCallout"]
    prompt=f'''Create a seven-slide, native Instagram 4:5 carousel for YAS from one public job advertisement. This is NOT an article carousel and NOT a screenshot of an X post.

VERIFIED CASE
Company: {case['company_name']}
Role: {case['role']}
Exact duty in the ad: {case['evidence_quote']}
Existing X analysis: {row['content_text']}
Illustrative economics: {economics}

CAROUSEL ARC
1 COVER: a strong, concrete hook that names one instantly recognisable operational conflict in 2–6 ordinary words and makes an operations leader swipe. It must not name the company, role, a department, or the process. It must not merely describe the duty. Use a tension a non-specialist can understand in one glance, such as `YOUR SYSTEM CAN'T SEE IT`, `THE WORK STARTS TOO LATE`, or `THE DATA NEVER MEETS` — but write a new case-specific version grounded in the evidence. The support line is the sharp reversal: what looks like a people problem is really a system-design boundary. The visual is the hook: show the conflict as one striking physical/editorial scene before any supporting text is read. Do not use a generic person at a computer, a title card, a logo-led cover, or a literal dashboard.
2 THE VACANCY: explain what the role is actually asked to do.
3 THE HIDDEN LOOP: explain why that task keeps consuming specialist time.
4 THE CUSTOM SYSTEM: name a buildable bespoke system and show at least two concrete actions it performs.
5 HUMAN GATE: make explicit the judgement/approval that remains human.
6 ECONOMICS: repeat the exact illustrative economics with labels that clarify HOURS / MONTH and BASE-PAY CAPACITY / MONTH; never imply measured company results.
7 CLOSE: a concise operator-facing final slide. It must include the exact real YAS logo and the exact domain `yas.ooo`, each once and large enough to read on a phone. The slide may say a short, truthful invitation such as `Build the system around the work.` It is the only YAS-branded slide.

Each slide gets one large headline, one short support line, and a distinct visual scene.  Headlines must be legible at phone size.  The visual must explain the slide; no generic laptop, dashboard, blue neon network, flowchart template, faux UI, or tiny text.  Use an editorial illustrated system with a different composition on every slide. Slide 1 must include the actual company logo naturally, visibly and accurately; no other slide needs a logo. Do not invent claims or numbers. Caption: one brief contextual paragraph plus a save cue, without URL.
Return JSON only.'''
    plans, planning_batch = _gemini_batch_text_json({"carousel":prompt},response_schema=PLAN_SCHEMA,temperature=.3,timeout=7200)
    plan=plans["carousel"]
    slides=plan.get("slides") or []
    if len(slides)!=7: raise ValueError("exactly seven slides required")
    logo_uri=_official_company_logo_data_uri(str(case['company_domain'] or ''),str(case['careers_url'] or case['source_url'] or ''))
    mime,b64=logo_uri.split(';base64,',1)
    # Exact canonical header mark supplied by YAS, rasterised on dark navy so
    # its white geometry survives the SVG-to-PNG conversion for Gemini input.
    yas_logo_path = "/var/www/blog.yas.ooo/assets-yas-header-logo.png"
    if not os.path.isfile(yas_logo_path):
        raise RuntimeError("YAS real logo reference is required for the final carousel slide")
    yas_logo={"mime_type":"image/png","data":b64encode(open(yas_logo_path,"rb").read()).decode("ascii")}
    reqs=[]
    for slide in slides:
        i=int(slide['index'])
        if i==1:
            logo_rule="The attached image is the verified official company logo. Use it once, accurately and visibly as part of this cover."
        elif i==7:
            logo_rule="Use the supplied YAS logo exactly once on this slide, without changing it: preserve its exact shape, proportions, colours and lettering; do not redraw, restyle, crop, reinterpret or generate a second version. Do not add any other YAS mark, logo-like symbol or URL. Render the exact domain `yas.ooo` once, large and sharp."
        else:
            logo_rule="Do not add any logo, wordmark, domain or watermark."
        text=f'''Create a finished 1080x1350 Instagram carousel slide for YAS.
SLIDE {i}/7, {slide['role']}.
PLACE THIS TEXT EXACTLY AND LARGE: {slide['headline']}
SUPPORTING TEXT EXACTLY: {slide['subtext']}
VISUAL SCENE: {slide['visual']}
Use only the two text strings above. The text must be large and legible at phone-feed size. {logo_rule}
Make the custom system and a human decision boundary visually intelligible. Premium, case-specific editorial illustration. No tiny copy, labels, dashboards, generic office stock photo, fake UI or extra statistics.'''
        parts=[{"text":text}]
        if i==1: parts.append({"inlineData":{"mimeType":mime.replace("data:",""),"data":b64}})
        if i==7: parts.append({"inlineData":{"mimeType":yas_logo["mime_type"],"data":yas_logo["data"]}})
        reqs.append({"request":{"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"4:5"}}},"metadata":{"key":str(i)}})
    images,batch,model=batch_images(reqs)
    key=f"vacancy-carousel-{SOURCE_POST_ID}-{datetime.now(timezone.utc):%Y%m%d%H%M%S}"; directory=social_asset_job_dir(SITE_ID,key,"instagram"); directory.mkdir(parents=True,exist_ok=True)
    for s in slides:
        i=int(s['index']); filename=f"slide-{i:02d}.jpg"; (directory/filename).write_bytes(images[i]); s.update({"imageUrl":social_asset_url(SITE_ID,key,"instagram",filename),"imageMimeType":"image/jpeg","imageStatus":"generated"})
    payload={"source":"yas-vacancy-carousel","instagramCarousel":{"caption":plan['caption'],"carouselType":"vacancy_evidence_case","visualSpec":{"aspectRatio":"4:5","recommendedSize":"1080x1350","generator":model,"planningBatch":planning_batch,"imageBatch":batch,"sourceXPostId":SOURCE_POST_ID},"slides":slides,"destinationUrl":""}}
    with db() as conn:
        post_id=conn.execute("insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at) values(?,?,?,?,?,'','DRAFT','instagram_vacancy_carousel','en',2200,?,0,?,?,?)",(SITE_ID,row['job_id'],'instagram',plan['caption'],json.dumps(payload,ensure_ascii=False),len(plan['caption']),json.dumps({"ok":True,"batch":True,"sourceXPostId":SOURCE_POST_ID}),now_iso(),now_iso())).lastrowid
    print(json.dumps({"postId":post_id,"previewUrl":f"/sites/{SITE_ID}/social-posts/{post_id}/instagram-carousel","planning":"batch","imageBatch":batch},ensure_ascii=False))

if __name__=='__main__': main()
