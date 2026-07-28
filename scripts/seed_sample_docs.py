import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.getcwd())
import fitz # PyMuPDF
from config.logger import logger


def generate_sample_pdf(filename: str, title: str, content_pages: list):
    output_dir = "./data/uploads"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    doc = fitz.open()
    for idx, text in enumerate(content_pages):
        page = doc.new_page()
        p_title = f"{title} - Page {idx+1}"
        page.insert_text((50, 50), p_title, fontsize=16)
        page.insert_text((50, 90), text, fontsize=11)

    doc.save(file_path)
    doc.close()
    logger.info(f"Generated sample PDF at: {file_path}")
    return file_path


if __name__ == "__main__":
    page1 = (
        "Artificial Intelligence (AI) and Deep Learning architectures have revolutionized automated "
        "document reasoning and semantic retrieval systems. In this work, we propose a multi-stage "
        "hybrid retrieval system combining BM25 keyword matching with dense Qdrant vector embeddings."
    )
    page2 = (
        "Empirical evaluations show a 45% reduction in latency and a 99.2% accuracy in anti-hallucination "
        "verification when applying strict inline page citations. The system uses TensorFlow for automated "
        "document classification across 10 enterprise domains."
    )
    generate_sample_pdf("ai_research_paper.pdf", "Enterprise AI & Hybrid RAG Architectures", [page1, page2])
