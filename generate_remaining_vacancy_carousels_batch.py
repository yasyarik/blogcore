"""Create one Gemini planning batch and one image batch for all remaining vacancy carousels."""
import json, os
from base64 import b64encode
from datetime import datetime, timezone
from pathlib import Path

from app import (db, now_iso, parse_json_object, _gemini_batch_text_json,
    _official_company_logo_data_uri, _evidence_case_economics, social_asset_job_dir, social_asset_url)
from generate_vacancy_instagram_carousel_batch import PLAN_SCHEMA, batch_images

SITE_ID=12

def prompt(post, case):
    economics=_evidence_case_economics(dict(case))["postCallout"]
    return f'''Create a seven-slide native Instagram 4:5 carousel for YAS from one public job ad. This is a vacancy-evidence carousel, not an article carousel or a screenshot.

Company: {case['company_name']}
Role: {case['role']}
Exact duty in the ad: {case['evidence_quote']}
Existing X analysis: {post['content_text']}
Illustrative economics: {economics}

ARC: 1) COVER: a new, concrete 2–6-word hook about an instantly recognisable operational conflict, grounded in the evidence; not company/role/department/process name. Its supporting line states that this is a system-design boundary, not merely a people problem. The scene shows the conflict before the text. 2) THE VACANCY: what the role must actually do. 3) THE HIDDEN LOOP: why it consumes specialist time. 4) THE CUSTOM SYSTEM: a buildable bespoke system with at least two actions. 5) HUMAN GATE: judgement/approval retained by a person. 6) ECONOMICS: exact illustrative economics labelled HOURS / MONTH and BASE-PAY CAPACITY / MONTH, never measured company results. 7) CLOSE: concise operator-facing close.

Every slide needs one large headline, one short support line and a distinct, case-specific editorial illustration. Text must be readable on a phone. Do not use generic laptop/office, dashboards, faux UI, blue-neon network, flowchart template or tiny labels. Cover must be visually hook-led, not a title card. Slide 7 is the only YAS-branded slide. Return JSON only.'''

def main():
  with db() as c:
    sources=c.execute("select * from social_posts where site_id=? and asset_type like 'evidence_post_%' and status='DRAFT' order by id",(SITE_ID,)).fetchall()
    existing=c.execute("select content_json from social_posts where site_id=? and asset_type='instagram_vacancy_carousel'",(SITE_ID,)).fetchall()
    used={int((parse_json_object(x[0]).get('instagramCarousel',{}).get('visualSpec',{}) or {}).get('sourceXPostId') or 0) for x in existing}
    work=[]
    for post in sources:
      if post['id'] in used: continue
      x=parse_json_object(post['content_json']).get('twitter') or {}
      cid=int(x['evidenceCaseId'])
      case=c.execute("""select ec.*,jp.title role,jp.source_url,sb.company_name,sb.company_domain,sb.careers_url from evidence_cases ec join evidence_job_postings jp on jp.id=ec.job_posting_id join evidence_source_boards sb on sb.id=jp.source_board_id where ec.id=?""",(cid,)).fetchone()
      if case: work.append((post,case))
  if not work: print(json.dumps({'created':0,'reason':'no remaining cases'})); return
  plans,planning_batch=_gemini_batch_text_json({str(p['id']):prompt(p,c) for p,c in work},response_schema=PLAN_SCHEMA,temperature=.3,timeout=7200)
  yas_path=Path('/var/www/blog.yas.ooo/assets-yas-header-logo.png')
  yas={'mime_type':'image/png','data':b64encode(yas_path.read_bytes()).decode('ascii')}
  requests=[]; mapping=[]; n=0
  prepared=[]
  for post,case in work:
    plan=plans[str(post['id'])]; slides=plan.get('slides') or []
    if len(slides)!=7: raise ValueError(f"{post['id']}: invalid slide count")
    logo_uri=_official_company_logo_data_uri(str(case['company_domain'] or ''),str(case['careers_url'] or case['source_url'] or ''))
    mime,b64=logo_uri.split(';base64,',1)
    for slide in slides:
      i=int(slide['index']); n+=1
      if i==1: rule='Use the attached verified official company logo once, accurately and visibly as part of this cover.'; ref={'mimeType':mime.replace('data:',''),'data':b64}
      elif i==7: rule='Use the supplied YAS logo exactly once, without changing it: preserve exact shape, proportions, colours and lettering; do not redraw, restyle, crop, reinterpret or generate a second version. Do not add another YAS mark, logo-like symbol or URL. Render the exact domain yas.ooo once, large and sharp.'; ref={'mimeType':yas['mime_type'],'data':yas['data']}
      else: rule='Do not add a logo, wordmark, domain or watermark.'; ref=None
      text=f'''Create a finished 1080x1350 Instagram carousel slide for YAS. SLIDE {i}/7, {slide['role']}. PLACE THIS TEXT EXACTLY AND LARGE: {slide['headline']} SUPPORTING TEXT EXACTLY: {slide['subtext']} VISUAL SCENE: {slide['visual']} Use only the two text strings above. Text must be legible at phone-feed size. {rule} Premium case-specific editorial illustration. No tiny copy, labels, dashboards, generic office stock photo, fake UI or extra statistics.'''
      parts=[{'text':text}]+([{'inlineData':ref}] if ref else [])
      requests.append({'request':{'contents':[{'role':'user','parts':parts}],'generationConfig':{'responseModalities':['IMAGE'],'imageConfig':{'aspectRatio':'4:5'}}},'metadata':{'key':str(n)}})
      mapping.append((post,case,plan,slide,n))
    prepared.append((post,case,plan))
  images,image_batch,model=batch_images(requests,expected=len(requests))
  now=datetime.now(timezone.utc)
  grouped={}
  for post,case,plan,slide,key in mapping:
    grouped.setdefault(post['id'],[]).append((slide,images[key]))
  with db() as c:
    made=[]
    for post,case,plan in prepared:
      asset_key=f"vacancy-carousel-{post['id']}-{now:%Y%m%d%H%M%S}"; directory=social_asset_job_dir(SITE_ID,asset_key,'instagram'); directory.mkdir(parents=True,exist_ok=True)
      slides=[]
      for slide,data in sorted(grouped[post['id']],key=lambda x:int(x[0]['index'])):
        name=f"slide-{int(slide['index']):02d}.jpg"; (directory/name).write_bytes(data); slide=dict(slide); slide.update({'imageUrl':social_asset_url(SITE_ID,asset_key,'instagram',name),'imageMimeType':'image/jpeg','imageStatus':'generated'}); slides.append(slide)
      payload={'source':'yas-vacancy-carousel','instagramCarousel':{'caption':plan['caption'],'carouselType':'vacancy_evidence_case','visualSpec':{'aspectRatio':'4:5','recommendedSize':'1080x1350','generator':model,'planningBatch':planning_batch,'imageBatch':image_batch,'sourceXPostId':post['id']},'slides':slides,'destinationUrl':''}}
      pid=c.execute("insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at) values(?,?,?,?,?,'','DRAFT','instagram_vacancy_carousel','en',2200,?,0,?,?,?)",(SITE_ID,post['job_id'],'instagram',plan['caption'],json.dumps(payload,ensure_ascii=False),len(plan['caption']),json.dumps({'ok':True,'batch':True,'sourceXPostId':post['id']}),now_iso(),now_iso())).lastrowid
      made.append({'sourceXPostId':post['id'],'postId':pid,'previewUrl':f'/sites/{SITE_ID}/social-posts/{pid}/instagram-carousel'})
  print(json.dumps({'created':len(made),'planningBatch':planning_batch,'imageBatch':image_batch,'posts':made},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
