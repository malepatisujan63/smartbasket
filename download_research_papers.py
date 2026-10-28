import os
import sys
import urllib.request
import ssl

TARGET_DIR = "/run/media/sujan/New Volume/aimlproject/research_papers"
os.makedirs(TARGET_DIR, exist_ok=True)

# List of papers: (Feature Name, primary_urls)
PAPERS = [
    (
        "Neural_Collaborative_Filtering_NCF.pdf",
        [
            "https://arxiv.org/pdf/1708.05031",
            "https://arxiv.org/pdf/1708.05031.pdf",
            "https://web.archive.org/web/20220619084803/https://arxiv.org/pdf/1708.05031.pdf"
        ]
    ),
    (
        "Matrix_Factorization_SVD.pdf",
        [
            "https://datajobs.com/data-science-repo/Recommender-Systems-[Netflix].pdf",
            "https://www.inf.unibz.it/~ricci/ISR/papers/ieeecomputer.pdf",
            "https://web.stanford.edu/class/cs246/slides/06-rec_sys.pdf"
        ]
    ),
    (
        "Content_Based_TF_IDF_Vector_Space.pdf",
        [
            "https://courses.ischool.berkeley.edu/i256/f06/papers/salton75.pdf",
            "https://ir.nist.gov/historical/salton75.pdf",
            "https://web.archive.org/web/20210414161741/https://courses.ischool.berkeley.edu/i256/f06/papers/salton75.pdf"
        ]
    ),
    (
        "CatBoost_Categorical_Gradient_Boosting.pdf",
        [
            "https://arxiv.org/pdf/1706.09516",
            "https://proceedings.neurips.cc/paper/2018/file/14491b756b3a51daac41c24863285549-Paper.pdf"
        ]
    ),
    (
        "Contextual_Bandits_LinUCB.pdf",
        [
            "https://arxiv.org/pdf/1003.0146",
            "https://arxiv.org/pdf/1003.0146.pdf"
        ]
    ),
    (
        "Maximal_Marginal_Relevance_MMR.pdf",
        [
            "https://www.cs.cmu.edu/~jgc/publication/PublicationPDF/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf",
            "https://web.archive.org/web/20220120183344/https://www.cs.cmu.edu/~jgc/publication/PublicationPDF/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf"
        ]
    ),
    (
        "Two_Stage_Recommendation_Funnel_YouTube.pdf",
        [
            "https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45530.pdf",
            "https://web.archive.org/web/20220119154743/https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45530.pdf"
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

print(f"Downloading {len(PAPERS)} research papers into {TARGET_DIR}...")

for filename, urls in PAPERS:
    filepath = os.path.join(TARGET_DIR, filename)
    success = False
    
    for url in urls:
        print(f"\n[Attempting] {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = resp.read()
                
            # Verify PDF magic bytes
            if data[:4] == b"%PDF":
                with open(filepath, "wb") as f:
                    f.write(data)
                print(f" [SUCCESS] Saved {filename} ({len(data):,} bytes)")
                success = True
                break
            else:
                print(f" [FAILED] Downloaded content is not a PDF (got header: {data[:15]!r})")
        except Exception as e:
            print(f" [ERROR] Failed from {url}: {e}")
            
    if not success:
        print(f" [WARNING] Could not download {filename} from any primary/mirror source.")

print("\nFinished download process.")
