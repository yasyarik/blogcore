#!/usr/bin/env python3
"""Replace the CRUE guide's three body images after visual QA."""
from app import _gemini_image_jpeg, article_asset_job_dir, optimize_article_image_to_webp


JOB_ID = "8b67f5810fa19fd0be505ce7"
PROMPTS = {
    "https-nomadeira.com-images-identity-passport-desk.webp": """Create one 16:9 photorealistic editorial magazine-feature photograph for a serious Madeira relocation guide. A close natural-light tabletop scene: an adult applicant's hands place a closed passport and a face-down identity card beside a neat blank application folder on a warm wooden table. The person is softly out of focus in the background. Show only the physical preparation action. Every document surface must face away, be blank, fully defocused, or too small to read. Absolutely no readable text, letters, numbers, logos, seals, flags, watermarks, screens, signage, labels, UI, illustration, collage, poster, or infographic. Real contemporary photography, believable hands and document geometry, natural daylight, restrained editorial composition.""",
    "https-nomadeira.com-images-evidence-category-folders.webp": """Create one 16:9 photorealistic editorial magazine-feature photograph for a serious Madeira relocation guide. An adult applicant at a sunlit home table separates one relevant evidence bundle from three alternative closed folders. The chosen bundle contains blank paper sheets and a plain unmarked card; the unused folders are distinct solid colours with no labels. The person's hands are caught in the exact action of moving the chosen folder forward. All paper and folder surfaces must be completely blank, turned away, defocused, or too small to read. Absolutely no readable text, letters, numbers, logos, stamps, watermarks, screens, signage, labels, UI, illustration, collage, poster, or infographic. Real contemporary photography, accurate hand anatomy, believable paper physics, bright natural editorial light.""",
    "https-nomadeira.com-images-camara-municipal-entrance.webp": """Create one 16:9 photorealistic editorial magazine-feature photograph for a serious Madeira relocation guide. Inside a bright Portuguese municipal reception area, an adult applicant hands a closed unmarked document folder to a clerk across a simple wooden counter. The physical exchange is the clear focal action; a calm waiting area and stone architectural details remain softly out of focus behind them. Frame out every directory and sign. Every paper, folder and screen must be blank, turned away, fully defocused, or too small to read. Absolutely no readable text, letters, numbers, logos, crests, watermarks, screens, signage, labels, UI, illustration, collage, poster, or infographic. Real contemporary photography, natural human anatomy, believable hands and document exchange, crisp daylight, authored glossy editorial quality.""",
}


def main() -> None:
    target = article_asset_job_dir(18, JOB_ID)
    for filename, prompt in PROMPTS.items():
        raw = _gemini_image_jpeg(prompt, aspect_ratio="16:9")
        path = target / filename
        path.write_bytes(optimize_article_image_to_webp(raw))
        print(filename, path.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
