"""Recover completed YAS visual briefs and materialize their image-backed X previews."""
import json, os, urllib.request
from base64 import b64decode
from io import BytesIO
from PIL import Image, ImageOps

from app import db, now_iso, social_asset_job_dir, social_asset_url, site_logo_reference, _x_weighted_length
from prepare_yas_x_drafts_batch import batch_images, render_prompt

SITE_ID = 12
BATCH = "batches/c7xu4m01i9ukifp260uztfqiyx1uycpoasjz"
IMAGE_BATCH = "batches/qb892qspupghu8miy9u6ax76qe3ly22qbabx"

def fetch_plans():
    key = os.environ["GEMINI_API_KEY"]
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/{BATCH}", headers={"x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.load(response)
    raw = (data.get("response") or {}).get("inlinedResponses") or []
    entries = raw.get("inlinedResponses", []) if isinstance(raw, dict) else raw
    plans = {}
    for item in entries:
        item_key = str((item.get("metadata") or {}).get("key") or "")
        if item.get("error") or not item_key:
            continue
        text = (((item.get("response") or {}).get("candidates") or [{}])[0].get("content") or {}).get("parts", [{}])[0].get("text")
        try:
            plan = json.loads(text)
        except (TypeError, json.JSONDecodeError):
            continue
        if all(str(plan.get(field) or "").strip() for field in ("hookText", "visualBrief", "altText")):
            plans[item_key] = plan
    return plans

def rows_for(plans):
    with db() as conn:
        rows = conn.execute("""select wi.*, cj.title as article_title, cj.description as article_description
          from social_work_items wi join content_jobs cj on cj.id=wi.source_job_id and cj.site_id=wi.site_id
          where wi.site_id=? and wi.channel='twitter' and wi.published_post_id is null
          order by wi.created_at,wi.id""", (SITE_ID,)).fetchall()
    return [row for row in rows if str(row["id"]) in plans]

def fetch_images():
    key = os.environ["GEMINI_API_KEY"]
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/{IMAGE_BATCH}", headers={"x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.load(response)
    raw = (data.get("response") or {}).get("inlinedResponses") or []
    entries = raw.get("inlinedResponses", []) if isinstance(raw, dict) else raw
    images = {}
    for item in entries:
        item_key = str((item.get("metadata") or {}).get("key") or "")
        parts = (((item.get("response") or {}).get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
        encoded = next((part.get("inlineData", {}).get("data") for part in parts if part.get("inlineData", {}).get("data")), "")
        if not item_key or not encoded:
            continue
        image = ImageOps.fit(Image.open(BytesIO(b64decode(encoded))).convert("RGB"), (1200, 675), method=Image.Resampling.LANCZOS)
        output = BytesIO(); image.save(output, format="JPEG", quality=91, optimize=True, progressive=True)
        images[item_key] = output.getvalue()
    return images

def main():
    plans = fetch_plans(); rows = rows_for(plans)
    if not rows: print("no recoverable rows"); return
    reference = site_logo_reference(SITE_ID)
    images = fetch_images()
    missing = [str(row["id"]) for row in rows if str(row["id"]) not in images]
    if missing: raise RuntimeError(f"completed image batch omitted: {', '.join(missing)}")
    image_batch, model = IMAGE_BATCH, "gemini-3.1-flash-image"
    created=[]
    with db() as conn:
        for row in rows:
            item_key=str(row["id"]); asset_key=f"x-work-{item_key}"; directory=social_asset_job_dir(SITE_ID,asset_key,"twitter")
            directory.mkdir(parents=True,exist_ok=True); filename="image-01.jpg"; (directory/filename).write_bytes(images[item_key])
            thread_items=[part.strip() for part in str(row["body"] or "").split("\n\n") if part.strip()] if row["task_type"]=="x_thread" else [str(row["body"] or "").strip()]
            if not thread_items or any(_x_weighted_length(part)>280 for part in thread_items): raise RuntimeError(f"invalid X length {item_key}")
            media=social_asset_url(SITE_ID,asset_key,"twitter",filename)
            payload={"source":"yas-x-batch-recovery","twitter":{"format":"thread" if len(thread_items)>1 else "post","threadItems":thread_items,"mediaUrls":[media],"mediaMimeType":"image/jpeg","visualHook":plans[item_key]["hookText"],"visualBrief":plans[item_key]["visualBrief"],"altText":plans[item_key]["altText"],"planningBatch":BATCH,"imageBatch":image_batch,"generator":model}}
            validation={"ok":True,"batch":True,"posts":[{"charCount":_x_weighted_length(part),"maxChars":280} for part in thread_items]}
            post_id=conn.execute("""insert into social_posts(site_id,job_id,channel,content_text,content_json,remote_url,status,asset_type,language,max_chars,char_count,include_link,validation_json,created_at,updated_at)
              values(?,?,?,?,?,'','DRAFT','x_batch_visual','en',280,?,0,?,?,?)""",(SITE_ID,row["source_job_id"],"twitter",row["body"],json.dumps(payload,ensure_ascii=False),max(post["charCount"] for post in validation["posts"]),json.dumps(validation),now_iso(),now_iso())).lastrowid
            conn.execute("update social_work_items set published_post_id=?,updated_at=? where id=?",(post_id,now_iso(),row["id"]))
            created.append(post_id)
    print(json.dumps({"created":created,"imageBatch":image_batch},ensure_ascii=False),flush=True)

if __name__ == "__main__": main()
