"""Create one native Pinterest vacancy-evidence Pin draft for every remaining YAS vacancy case."""
import json, uuid
from base64 import b64encode
from pathlib import Path
from app import db, now_iso, parse_json_object, _official_company_logo_data_uri, visual_pin_asset_dir
from generate_vacancy_instagram_carousel_batch import batch_images

SITE_ID=12

def copy_for(case):
    company=str(case['company_name'])
    duty=str(case['evidence_quote']).strip().rstrip('.')
    role=str(case['role'])
    # Keep the factual vacancy task prominent; the supporting line describes only a buildable system, not an outcome claim.
    headline=f"{company.upper()} IS HIRING A HUMAN TO DO THIS"
    solution="A custom system prepares the evidence before specialist review"
    title=f"How {role} work can become a custom operational system"[:100]
    description=(f"A current {company} vacancy includes this operational task: {duty}. "
                 "A bespoke workflow can collect relevant context, prepare a reviewer-ready brief and route exceptions to a specialist. "
                 "It supports human judgement rather than replacing the decision.")[:500]
    return headline,duty,solution,title,description

def main():
  with db() as c:
    posts=c.execute("select * from social_posts where site_id=? and asset_type like 'evidence_post_%' and status='DRAFT' order by id",(SITE_ID,)).fetchall()
    existing=c.execute("select concept_json from visual_pins where site_id=? and mode='vacancy_evidence_pin'",(SITE_ID,)).fetchall()
    used={int(parse_json_object(r[0]).get('sourceXPostId') or 0) for r in existing}
    work=[]
    for post in posts:
      if int(post['id']) in used: continue
      data=parse_json_object(post['content_json']).get('twitter') or {}
      case=c.execute("""select ec.*,jp.title role,jp.source_url,sb.company_name,sb.company_domain,sb.careers_url from evidence_cases ec join evidence_job_postings jp on jp.id=ec.job_posting_id join evidence_source_boards sb on sb.id=jp.source_board_id where ec.id=?""",(int(data['evidenceCaseId']),)).fetchone()
      if case: work.append((post,case))
  if not work: print(json.dumps({'created':0,'reason':'no remaining cases'})); return
  yas={'mimeType':'image/png','data':b64encode(Path('/var/www/blog.yas.ooo/assets-yas-header-logo.png').read_bytes()).decode('ascii')}
  requests=[]; prepared=[]
  for n,(post,case) in enumerate(work,1):
    headline,duty,solution,title,description=copy_for(case)
    uri=_official_company_logo_data_uri(str(case['company_domain'] or ''),str(case['careers_url'] or case['source_url'] or ''))
    mime,company_b64=uri.split(';base64,',1)
    prompt=f'''Create one finished 1000x1500 native Pinterest Pin for YAS. It is a single complete evidence-led idea, not an Instagram slide or technical infographic.
Use the attached {case['company_name']} logo exactly once as the factual source marker and the attached YAS logo exactly once as the small brand marker. Do not redraw, restyle, duplicate or invent either logo.
Place this exact large headline: {headline}
Place this exact duty clearly: {duty}
Place this exact solution line clearly: {solution}
These are the ONLY readable words in the image. Do not add labels, captions, diagram nodes, arrows with text, statistics, fake UI, acronyms or watermark.
Show one immediately readable editorial scene: scattered work material enters a calm, bespoke context-mapping workspace; a specialist receives one clear prepared brief and keeps the decision. Make the system visible through objects and composition, not a flowchart. Use a refined warm editorial Pinterest aesthetic: light mineral or cream field, charcoal, muted teal and one restrained navy accent; tactile paper, subtle depth, generous negative space and confident magazine-like composition. Avoid dark cyberpunk, generic cyber graphics, printer imagery, dashboard screens, stock office scenes and dense technical diagrams.'''
    requests.append({'request':{'contents':[{'role':'user','parts':[{'text':prompt},{'inlineData':{'mimeType':mime.replace('data:',''),'data':company_b64}},{'inlineData':yas}]}],'generationConfig':{'responseModalities':['IMAGE'],'imageConfig':{'aspectRatio':'2:3'}}},'metadata':{'key':str(n)}})
    prepared.append((post,case,headline,duty,solution,title,description,n))
  images,batch,model=batch_images(requests,expected=len(requests),size=(1000,1500),aspect_ratio='2:3')
  with db() as c:
    made=[]
    for post,case,headline,duty,solution,title,description,n in prepared:
      pin_id='vacancy-'+uuid.uuid4().hex[:12]; directory=visual_pin_asset_dir(SITE_ID,pin_id); directory.mkdir(parents=True,exist_ok=True); filename='pin-01.jpg'; (directory/filename).write_bytes(images[n])
      concept={'contour':'vacancy_evidence_pin','sourceXPostId':int(post['id']),'company':case['company_name'],'role':case['role'],'duty':case['evidence_quote'],'headline':headline,'solution':solution,'humanGate':'A specialist retains the approval decision','generator':model,'imageBatch':batch}
      c.execute("insert into visual_pins(id,site_id,mode,concept_json,title,description,alt_text,image_filename,destination_url,status,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,'DRAFT',?,?)",(pin_id,SITE_ID,'vacancy_evidence_pin',json.dumps(concept),title,description,f"Illustration based on a {case['company_name']} vacancy task and a custom operational system.",filename,'https://yas.ooo',now_iso(),now_iso()))
      made.append({'sourceXPostId':int(post['id']),'pinId':pin_id,'previewUrl':f'/sites/{SITE_ID}/visual-pins/{pin_id}/preview'})
  print(json.dumps({'created':len(made),'batch':batch,'pins':made},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
