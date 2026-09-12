"""Replace only the cover and final slide of vacancy carousel #162 via Gemini Batch."""
import json, os, time, urllib.parse, urllib.request
from base64 import b64decode, b64encode
from io import BytesIO
from PIL import Image, ImageOps
from app import db, parse_json_object, now_iso, _official_company_logo_data_uri, social_asset_job_dir, social_asset_url

SITE_ID = 12
POST_ID = int(os.environ.get("CAROUSEL_POST_ID", "162"))
EDGE_SLIDES = {int(value) for value in os.environ.get("EDGE_SLIDES", "1,7").split(",") if value.strip()}

def key(): return os.environ.get("GEMINI_IMAGE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
def main():
  with db() as c:
    post=c.execute("select * from social_posts where id=? and site_id=?",(POST_ID,SITE_ID)).fetchone()
    if not post: raise KeyError("carousel draft not found")
    payload=parse_json_object(post["content_json"])
    source_post_id=int((payload.get("instagramCarousel", {}).get("visualSpec", {}) or {}).get("sourceXPostId") or 0)
    x=c.execute("select content_json from social_posts where id=?",(source_post_id,)).fetchone()
    if not x: raise KeyError("source vacancy X post not found")
    case_id=int(parse_json_object(x[0])["twitter"]["evidenceCaseId"])
    case=c.execute("""select ec.evidence_quote,jp.title,sb.company_name,sb.company_domain,sb.careers_url,jp.source_url
      from evidence_cases ec join evidence_job_postings jp on jp.id=ec.job_posting_id join evidence_source_boards sb on sb.id=jp.source_board_id where ec.id=?""",(case_id,)).fetchone()
  carousel=payload["instagramCarousel"]; slides=carousel["slides"]
  company_uri=_official_company_logo_data_uri(case[3] or '',case[4] or case[5] or ''); cmime,cb64=company_uri.split(';base64,',1)
  # User-supplied canonical header mark.  It is rasterised from the exact SVG
  # https://yas.ooo/brand/yas-header-logo.svg only because Gemini references
  # require a raster inline image; it is never redrawn or overlaid by us.
  yas_path='/var/www/blog.yas.ooo/assets-yas-header-logo.png'
  yas={"mime_type":"image/png","data":b64encode(open(yas_path,'rb').read()).decode('ascii')}
  cover=slides[0]; final=slides[6]
  # Only these two images are requested; slide copy 2–6 and their image URLs stay untouched.
  cover["headline"]="YOUR LOGS CAN'T SEE IT"; cover["subtext"]="Threat intel cannot become a detection until telemetry coverage is known."
  final["headline"]="BUILD SYSTEMS AROUND REAL WORK"; final["subtext"]="yas.ooo"
  prompts=[
    (1, f'''Create slide 1 of a 7-slide, 1080x1350 Instagram carousel. Match the visual language of slides 2–6 exactly: the same dark-navy base, muted teal accents, editorial illustrated materials, restrained contrast, and clean large type — not a glossy new art direction. It must be a scroll-stopping editorial illustration, not a title card. Show the visual conflict before text: threat-intelligence signals arrive but disappear at a physical telemetry blind spot; a custom coverage-mapping system makes the invisible gap legible, while one security engineer retains the final rule decision. Include exactly ONE anatomically plausible human: one head, two arms, two hands and no duplicated limbs, fingers or body parts. Place exactly this large headline: {cover['headline']}. Place exactly this supporting line: {cover['subtext']}. No other readable text, no dashboards, UI, laptop stock photo, generic office, arrows or tiny labels. The attached image is the verified Notion logo; use it once, clearly and naturally.''',cmime.replace('data:',''),cb64),
    (7, f'''Create one finished 1080x1350 Instagram image in the same dark-navy and muted-teal editorial illustration style as the rest of this carousel. Show a bespoke business system turning scattered operational work into a clear governed flow, with one human retaining approval. Place exactly this headline: {final['headline']}. Place exactly this domain: yas.ooo. Use the supplied YAS logo exactly once, without changing it: preserve its exact shape, proportions, colours and lettering; do not redraw, restyle, crop, reinterpret or generate a second version. Do not add any other YAS mark, logo-like symbol, readable text, number, page marker, fake UI or watermark.''',yas['mime_type'],yas['data'])]
  reqs=[]
  for i,p,m,d in prompts:
    parts=[{"text":p},{"inlineData":{"mimeType":m,"data":d}}]
    reqs.append({"request":{"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"4:5"}}},"metadata":{"key":str(i)}})
  reqs=[row for row in reqs if int((row.get("metadata") or {}).get("key")) in EDGE_SLIDES]
  if not reqs or not EDGE_SLIDES.issubset({1,7}): raise ValueError("EDGE_SLIDES must select slide 1, slide 7, or both")
  model=os.environ.get("GEMINI_IMAGE_MODEL") or "gemini-3.1-flash-image"; data={"batch":{"display_name":"yas-vacancy-carousel-edges","input_config":{"requests":{"requests":reqs}}}}
  u="https://generativelanguage.googleapis.com/v1beta/models/"+urllib.parse.quote(model,safe='.-')+":batchGenerateContent"
  q=urllib.request.Request(u,data=json.dumps(data).encode(),headers={"content-type":"application/json","x-goog-api-key":key()},method="POST")
  with urllib.request.urlopen(q,timeout=180) as r: batch=json.loads(r.read().decode())
  name=batch['name']; print(json.dumps({"batch":name,"slides":[1,7]}),flush=True)
  while True:
    q=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/"+urllib.parse.quote(name,safe='/'),headers={"x-goog-api-key":key()})
    with urllib.request.urlopen(q,timeout=120) as r: batch=json.loads(r.read().decode())
    state=str(batch.get('state') or (batch.get('metadata') or {}).get('state') or ''); print(state,flush=True)
    if state in {'BATCH_STATE_SUCCEEDED','JOB_STATE_SUCCEEDED'}: break
    if state not in {'BATCH_STATE_RUNNING','BATCH_STATE_PENDING','JOB_STATE_RUNNING','JOB_STATE_PENDING'}: raise RuntimeError(state)
    time.sleep(20)
  rows=((batch.get('response') or {}).get('inlinedResponses') or (batch.get('output') or {}).get('inlinedResponses') or []); rows=rows.get('inlinedResponses',[]) if isinstance(rows,dict) else rows
  images={}
  for r in rows:
    i=int((r.get('metadata') or {}).get('key')); parts=((((r.get('response') or {}).get('candidates') or [{}])[0].get('content') or {}).get('parts') or []); d=next((p.get('inlineData',{}).get('data') for p in parts if p.get('inlineData',{}).get('data')),None)
    if not d: raise RuntimeError('missing image')
    im=ImageOps.fit(Image.open(BytesIO(b64decode(d))).convert('RGB'),(1080,1350),method=Image.Resampling.LANCZOS); out=BytesIO(); im.save(out,'JPEG',quality=92,optimize=True); images[i]=out.getvalue()
  if set(images)!=EDGE_SLIDES: raise RuntimeError('batch did not return every requested edge slide')
  asset='vacancy-carousel-162-edges'; directory=social_asset_job_dir(SITE_ID,asset,'instagram'); directory.mkdir(parents=True,exist_ok=True)
  for i in sorted(EDGE_SLIDES):
    fn=f'slide-{i:02d}.jpg'; (directory/fn).write_bytes(images[i]); slides[i-1]['imageUrl']=social_asset_url(SITE_ID,asset,'instagram',fn); slides[i-1]['imageStatus']='generated'
  carousel['visualSpec']['edgeImageBatch']=name; carousel['visualSpec']['edgeSlidesOnly']=sorted(EDGE_SLIDES)
  with db() as c: c.execute("update social_posts set content_json=?,updated_at=? where id=?",(json.dumps(payload,ensure_ascii=False),now_iso(),POST_ID))
  print(json.dumps({"postId":POST_ID,"previewUrl":f"/sites/{SITE_ID}/social-posts/{POST_ID}/instagram-carousel"}))
if __name__=='__main__': main()
