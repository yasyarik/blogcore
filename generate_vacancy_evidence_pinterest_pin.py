"""Create a review-only native Pinterest Pin from one verified vacancy case."""
import json, os, uuid
from base64 import b64encode
from pathlib import Path
from app import db, now_iso, parse_json_object, _official_company_logo_data_uri, visual_pin_asset_dir
from generate_vacancy_instagram_carousel_batch import batch_images

SITE_ID=12
SOURCE_POST_ID=int(os.environ.get('VACANCY_X_POST_ID','159'))

def main():
  with db() as c:
    post=c.execute("select * from social_posts where id=? and site_id=?",(SOURCE_POST_ID,SITE_ID)).fetchone()
    x=parse_json_object(post['content_json']).get('twitter') or {}
    case=c.execute("""select ec.*,jp.title role,jp.source_url,sb.company_name,sb.company_domain,sb.careers_url from evidence_cases ec join evidence_job_postings jp on jp.id=ec.job_posting_id join evidence_source_boards sb on sb.id=jp.source_board_id where ec.id=?""",(int(x['evidenceCaseId']),)).fetchone()
  company_uri=_official_company_logo_data_uri(str(case['company_domain'] or ''),str(case['careers_url'] or case['source_url'] or ''))
  cmime,cb64=company_uri.split(';base64,',1)
  yas={'mimeType':'image/png','data':b64encode(Path('/var/www/blog.yas.ooo/assets-yas-header-logo.png').read_bytes()).decode('ascii')}
  headline=f"{case['company_name'].upper()} IS HIRING A HUMAN TO DO THIS"
  duty="Translate threat intelligence into detection rules"
  solution="A custom system maps coverage gaps before analyst review"
  title="How security teams can automate threat-intelligence triage"
  description=f"A current {case['company_name']} security role includes translating threat intelligence into detection work. A bespoke workflow can collect relevant telemetry, identify coverage gaps and assemble a reviewer-ready brief before a specialist decides whether to change a detection rule or escalate."
  prompt=f'''Create one finished 1000x1500 native Pinterest Pin for YAS. It is a single complete evidence-led idea, not an Instagram slide or technical infographic.
Use the attached {case['company_name']} logo exactly once as the factual source marker and the attached YAS logo exactly once as the small brand marker. Do not redraw, restyle, duplicate or invent either logo.
Place this exact large headline: {headline}
Place this exact duty clearly: {duty}
Place this exact solution line clearly: {solution}
These are the ONLY readable words in the image. Do not add labels, captions, diagram nodes, arrows with text, statistics, fake UI, acronyms or watermark.
Show one immediately readable editorial scene: scattered threat-intelligence material enters a calm, custom coverage-mapping workspace; a security specialist reviews one clear prepared brief and keeps the decision. The system is visible through objects and composition, not a flowchart. Use a refined, warm editorial Pinterest aesthetic: light mineral/cream field, charcoal, muted teal and one restrained navy accent; tactile paper, subtle depth, generous negative space and a confident magazine-like composition. Avoid dark cyberpunk, generic cyber graphics, printer imagery, dashboard screens, stock office scenes and dense technical diagrams.'''
  req={'request':{'contents':[{'role':'user','parts':[{'text':prompt},{'inlineData':{'mimeType':cmime.replace('data:',''),'data':cb64}},{'inlineData':yas}]}],'generationConfig':{'responseModalities':['IMAGE'],'imageConfig':{'aspectRatio':'2:3'}}},'metadata':{'key':'1'}}
  images,batch,model=batch_images([req],expected=1,size=(1000,1500),aspect_ratio='2:3')
  pin_id='vacancy-'+uuid.uuid4().hex[:12]; directory=visual_pin_asset_dir(SITE_ID,pin_id); directory.mkdir(parents=True,exist_ok=True); filename='pin-01.jpg'; (directory/filename).write_bytes(images[1])
  concept={'contour':'vacancy_evidence_pin','sourceXPostId':SOURCE_POST_ID,'company':case['company_name'],'role':case['role'],'duty':case['evidence_quote'],'humanGate':'Security specialist approves rule changes or escalation','generator':model,'imageBatch':batch}
  with db() as c:
    c.execute("insert into visual_pins(id,site_id,mode,concept_json,title,description,alt_text,image_filename,destination_url,status,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,'DRAFT',?,?)",(pin_id,SITE_ID,'vacancy_evidence_pin',json.dumps(concept),title,description,'Illustration of a custom system turning scattered threat-intelligence signals into a reviewer-ready security triage brief.',filename,'https://yas.ooo',now_iso(),now_iso()))
  print(json.dumps({'pinId':pin_id,'previewUrl':f'/sites/{SITE_ID}/visual-pins/{pin_id}/preview','batch':batch}))
if __name__=='__main__': main()
