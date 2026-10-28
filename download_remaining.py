import os
import urllib.request
import ssl

TARGET_DIR = "/run/media/sujan/New Volume/aimlproject/research_papers"
os.makedirs(TARGET_DIR, exist_ok=True)

REMAINING = [
    (
        "Maximal_Marginal_Relevance_MMR.pdf",
        [
            "https://aclanthology.org/X98-1025.pdf",
            "https://www.cs.cmu.edu/~jgc/publication/The_Use_of_MMR_Diversity_Based_Reranking_for_Reordering_Documents_and_Producing_Summaries.pdf"
        ]
    ),
    (
        "Content_Based_TF_IDF_Vector_Space.pdf",
        [
            "https://archive.org/download/ERIC_ED096986/ERIC_ED096986.pdf",
            "https://files.eric.ed.gov/fulltext/ED096986.pdf"
        ]
    )
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8"
}

for filename, urls in REMAINING:
    filepath = os.path.join(TARGET_DIR, filename)
    success = False
    for url in urls:
        print(f"\n[Attempting] {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=45) as resp:
                data = resp.read()
            if data[:4] == b"%PDF":
                with open(filepath, "wb") as f:
                    f.write(data)
                print(f" [SUCCESS] Saved {filename} ({len(data):,} bytes)")
                success = True
                break
            else:
                print(f" [FAILED] Not a PDF: {data[:20]!r}")
        except Exception as e:
            print(f" [ERROR] Failed from {url}: {e}")

    if not success:
        print(f" [FAILED] Could not download {filename}")
