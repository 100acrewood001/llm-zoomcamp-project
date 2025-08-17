"""
Text extraction from PDF documents using PyMuPDF.
Handles PDF parsing with metadata preservation and error handling.
"""

import fitz  # PyMuPDF
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from src.utils.logging_config import get_logger, LoggerMixin, log_performance, log_error


@dataclass
class Page:
    """Represents a page from a document."""
    page_number: int
    text: str
    metadata: Dict[str, Any]


@dataclass
class Document:
    """Represents a complete document."""
    filepath: str
    filename: str
    pages: List[Page]
    total_pages: int
    metadata: Dict[str, Any]


class TextExtractor(LoggerMixin):
    """
    PDF text extractor using PyMuPDF with error handling and metadata preservation.
    """
    
    def __init__(self, max_file_size_mb: int = 50):
        """
        Initialize text extractor.
        
        Args:
            max_file_size_mb: Maximum allowed file size in MB
        """
        self.max_file_size_mb = max_file_size_mb
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        self.logger.info("Text extractor initialized", max_file_size_mb=max_file_size_mb)
    
    def extract_text_from_pdf(self, pdf_path: str) -> Document:
        """
        Extract text from PDF file with page-level metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Document object with extracted text and metadata
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is too large or corrupted
            Exception: If extraction fails
        """
        start_time = time.time()
        
        # Validate file
        self._validate_file(pdf_path)
        
        try:
            # Open PDF document
            pdf_document = fitz.open(pdf_path)
            
            # Extract document metadata
            doc_metadata = self._extract_document_metadata(pdf_document)
            
            # Extract pages
            pages = []
            total_text_length = 0
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Extract text from page
                page_text = page.get_text()
                
                # Clean and normalize text
                cleaned_text = self.clean_text(page_text)
                
                # Extract page metadata
                page_metadata = self._extract_page_metadata(page, page_num)
                
                # Create page object
                page_obj = Page(
                    page_number=page_num + 1,  # 1-indexed for user display
                    text=cleaned_text,
                    metadata=page_metadata
                )
                
                pages.append(page_obj)
                total_text_length += len(cleaned_text)
            
            pdf_document.close()
            
            # Create document object
            document = Document(
                filepath=pdf_path,
                filename=Path(pdf_path).name,
                pages=pages,
                total_pages=len(pages),
                metadata={
                    **doc_metadata,
                    "total_text_length": total_text_length,
                    "extraction_timestamp": time.time()
                }
            )
            
            duration = time.time() - start_time
            self.logger.info(
                "PDF text extraction completed",
                **log_performance(
                    "extract_text_from_pdf",
                    duration,
                    filename=Path(pdf_path).name,
                    total_pages=len(pages),
                    total_text_length=total_text_length
                )
            )
            
            return document
            
        except Exception as e:
            self.logger.error(
                "PDF extraction failed",
                **log_error(e, {"pdf_path": pdf_path})
            )
            raise
    
    def _validate_file(self, filepath: str):
        """
        Validate PDF file before processing.
        
        Args:
            filepath: Path to file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too large or wrong format
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > self.max_file_size_bytes:
            raise ValueError(
                f"File too large: {file_size / (1024*1024):.1f}MB. "
                f"Maximum allowed: {self.max_file_size_mb}MB"
            )
        
        # Check file extension
        if not filepath.lower().endswith('.pdf'):
            raise ValueError(f"Unsupported file format. Expected PDF, got: {Path(filepath).suffix}")
    
    def _extract_document_metadata(self, pdf_document) -> Dict[str, Any]:
        """
        Extract metadata from PDF document.
        
        Args:
            pdf_document: PyMuPDF document object
            
        Returns:
            Dictionary with document metadata
        """
        try:
            metadata = pdf_document.metadata
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "pages": pdf_document.page_count,
                "encrypted": pdf_document.is_encrypted
            }
        except Exception as e:
            self.logger.warning(f"Could not extract document metadata: {e}")
            return {"pages": pdf_document.page_count}
    
    def _extract_page_metadata(self, page, page_num: int) -> Dict[str, Any]:
        """
        Extract metadata from a single page.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
            
        Returns:
            Dictionary with page metadata
        """
        try:
            # Get page dimensions
            rect = page.rect
            
            # Count text elements
            text_dict = page.get_text("dict")
            block_count = len(text_dict.get("blocks", []))
            
            return {
                "page_number": page_num + 1,
                "width": rect.width,
                "height": rect.height,
                "rotation": page.rotation,
                "block_count": block_count,
                "has_images": len(page.get_images()) > 0,
                "has_links": len(page.get_links()) > 0
            }
        except Exception as e:
            self.logger.warning(f"Could not extract page metadata for page {page_num}: {e}")
            return {"page_number": page_num + 1}
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace while preserving structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines but preserve paragraph breaks
            if line:
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1]:  # Add single empty line for paragraph breaks
                cleaned_lines.append("")
        
        # Join lines and normalize whitespace
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive consecutive spaces within lines
        import re
        cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
        
        # Remove excessive newlines (more than 2 consecutive)
        cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def extract_text_by_pages(self, pdf_path: str, page_range: Optional[List[int]] = None) -> List[Page]:
        """
        Extract text from specific pages only.
        
        Args:
            pdf_path: Path to PDF file
            page_range: List of page numbers (1-indexed) to extract, None for all pages
            
        Returns:
            List of Page objects for requested pages
        """
        document = self.extract_text_from_pdf(pdf_path)
        
        if page_range is None:
            return document.pages
        
        # Filter pages (convert to 0-indexed for internal use)
        filtered_pages = []
        for page_num in page_range:
            if 1 <= page_num <= document.total_pages:
                filtered_pages.append(document.pages[page_num - 1])
            else:
                self.logger.warning(f"Page {page_num} out of range for document with {document.total_pages} pages")
        
        return filtered_pages
    
    def get_document_summary(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get summary information about document without full text extraction.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with document summary
        """
        self._validate_file(pdf_path)
        
        try:
            pdf_document = fitz.open(pdf_path)
            metadata = self._extract_document_metadata(pdf_document)
            
            # Get first page text for preview
            preview_text = ""
            if pdf_document.page_count > 0:
                first_page = pdf_document[0]
                preview_text = self.clean_text(first_page.get_text())[:500] + "..."
            
            pdf_document.close()
            
            return {
                "filename": Path(pdf_path).name,
                "file_size_mb": round(os.path.getsize(pdf_path) / (1024*1024), 2),
                "total_pages": metadata.get("pages", 0),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "creation_date": metadata.get("creation_date", ""),
                "preview_text": preview_text
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get document summary: {e}")
            raise


import time

if __name__ == "__main__":
    # Test the text extractor
    extractor = TextExtractor()
    
    # Example usage - you'll need to provide a test PDF
    test_pdf = "data/sample_annual_report.pdf"
    
    if os.path.exists(test_pdf):
        # Test document summary
        summary = extractor.get_document_summary(test_pdf)
        print("Document Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Test full extraction
        document = extractor.extract_text_from_pdf(test_pdf)
        print(f"\nExtracted {document.total_pages} pages")
        print(f"Total text length: {document.metadata['total_text_length']} characters")
        
        # Show first page preview
        if document.pages:
            first_page = document.pages[0]
            print(f"\nFirst page preview (page {first_page.page_number}):")
            print(first_page.text[:300] + "..." if len(first_page.text) > 300 else first_page.text)
    else:
        print(f"Test file not found: {test_pdf}")
        print("Please place a test PDF in the data/ directory to test the extractor.")
