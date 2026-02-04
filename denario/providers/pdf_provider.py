"""PDF Provider for fetching manuscripts from arXiv and ADS."""

import os
import requests
import re
import tarfile
import shutil
import fitz  # PyMuPDF
from typing import Optional, List, Dict
from pathlib import Path

class PDFProvider:
    """
    Provider for fetching and processing PDF manuscripts and source files.
    """
    
    def __init__(self, work_dir: str = "/tmp/denario_pdfs"):
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)
        
    def fetch_paper(self, identifier: str, source: str = "arxiv") -> Dict[str, str]:
        """
        Fetch a paper (PDF and source if available) given an identifier.
        
        Args:
            identifier: The paper ID (e.g., "1602.03837" for arXiv).
            source: Source repository ("arxiv" or "ads").
            
        Returns:
            Dictionary with paths to 'pdf' and 'source_dir' (if extracted).
        """
        if source.lower() == "arxiv":
            return self._fetch_from_arxiv(identifier)
        elif source.lower() == "ads":
            # ADS fetching often redirects to arXiv or publisher. 
            # For now, we assume we can resolve ADS bibcode to arXiv if possible, 
            # or use ADS link directly if implemented.
            # This is a placeholder for direct ADS PDF fetching logic.
            raise NotImplementedError("Direct ADS PDF fetching not yet implemented. Use arXiv ID.")
        else:
            raise ValueError(f"Unknown source: {source}")

    def _fetch_from_arxiv(self, arxiv_id: str) -> Dict[str, str]:
        """
        Download PDF and source files from arXiv.
        """
        # Clean ID
        arxiv_id = re.sub(r'^arxiv:', '', arxiv_id, flags=re.IGNORECASE)
        
        base_name = os.path.join(self.work_dir, arxiv_id)
        pdf_path = f"{base_name}.pdf"
        source_tar_path = f"{base_name}.tar.gz"
        source_dir = f"{base_name}_source"
        
        result = {}
        
        # 1. Download PDF
        print(f"Downloading PDF for arXiv:{arxiv_id}...")
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        try:
            response = requests.get(pdf_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                result['pdf'] = pdf_path
                print(f"PDF saved to {pdf_path}")
            else:
                print(f"Failed to download PDF: {response.status_code}")
        except Exception as e:
            print(f"Error downloading PDF: {e}")

        # 2. Download Source (e-print)
        print(f"Downloading source for arXiv:{arxiv_id}...")
        source_url = f"https://arxiv.org/e-print/{arxiv_id}"
        try:
            response = requests.get(source_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(source_tar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract source
                os.makedirs(source_dir, exist_ok=True)
                try:
                    # Check if it's a tar/gzip file
                    if tarfile.is_tarfile(source_tar_path):
                        with tarfile.open(source_tar_path) as tar:
                            tar.extractall(path=source_dir)
                        result['source_dir'] = source_dir
                        print(f"Source extracted to {source_dir}")
                    else:
                        print("Downloaded source is not a tar archive (likely a single PDF or error page).")
                except Exception as e:
                    print(f"Error extracting source: {e}")
            else:
                print(f"Failed to download source: {response.status_code}")
        except Exception as e:
            print(f"Error downloading source: {e}")
            
        return result

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using PyMuPDF.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
        text_content = []
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text_content.append(page.get_text())
            doc.close()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")
            
        return "\n\n".join(text_content)

    def get_manuscript_text(self, identifier: str, source: str = "arxiv") -> str:
        """
        High-level method to get the best available text for a paper.
        Prioritizes LaTeX source extraction over PDF OCR/Text extraction.
        """
        paths = self.fetch_paper(identifier, source)
        
        # Priority 1: TeX Source
        if 'source_dir' in paths:
            tex_files = list(Path(paths['source_dir']).glob("*.tex"))
            # Heuristic: Find the main file (often ms.tex, main.tex, or the largest one)
            if tex_files:
                # Naive selection: Largest .tex file
                main_tex = max(tex_files, key=lambda p: p.stat().st_size)
                print(f"Found TeX source: {main_tex.name}")
                with open(main_tex, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
        
        # Priority 2: PDF Text Extraction
        if 'pdf' in paths:
            print("Extracting text from PDF...")
            return self.extract_text_from_pdf(paths['pdf'])
            
        raise ValueError("Could not retrieve manuscript text.")
