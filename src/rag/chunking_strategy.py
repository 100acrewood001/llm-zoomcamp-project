"""
Text chunking strategies for document processing.
Handles document segmentation with overlap and metadata preservation.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.extractors.text_extractor import Document, Page
from src.utils.logging_config import get_logger, LoggerMixin, log_performance


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    chunk_id: str
    source_document: str
    page_numbers: List[int]
    start_char: int
    end_char: int
    metadata: Dict[str, Any]


class BasicChunkingStrategy(LoggerMixin):
    """
    Basic chunking strategy using recursive character splitting.
    Optimized for annual report text with financial content preservation.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        preserve_financial_tables: bool = True
    ):
        """
        Initialize chunking strategy.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators for text splitting
            preserve_financial_tables: Whether to try preserving financial table structure
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.preserve_financial_tables = preserve_financial_tables
        
        # Default separators optimized for financial documents
        if separators is None:
            separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks  
                ". ",    # Sentence endings
                ", ",    # Clause breaks
                " "      # Word boundaries
            ]
        
        # Initialize LangChain splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
        
        self.logger.info(
            "Chunking strategy initialized",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators_count=len(separators)
        )
    
    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Split document into overlapping chunks with metadata preservation.
        
        Args:
            document: Document object to chunk
            
        Returns:
            List of Chunk objects with preserved metadata
        """
        start_time = time.time()
        
        try:
            all_chunks = []
            
            # Process each page
            for page in document.pages:
                page_chunks = self._chunk_page(page, document)
                all_chunks.extend(page_chunks)
            
            # Post-process chunks for quality
            processed_chunks = self._post_process_chunks(all_chunks)
            
            duration = time.time() - start_time
            self.logger.info(
                "Document chunking completed",
                **log_performance(
                    "chunk_document",
                    duration,
                    document=document.filename,
                    pages_processed=len(document.pages),
                    chunks_created=len(processed_chunks),
                    avg_chunk_size=sum(len(c.text) for c in processed_chunks) // len(processed_chunks) if processed_chunks else 0
                )
            )
            
            return processed_chunks
            
        except Exception as e:
            self.logger.error(f"Chunking failed for document {document.filename}: {e}")
            raise
    
    def _chunk_page(self, page: Page, document: Document) -> List[Chunk]:
        """
        Chunk a single page with metadata tracking.
        
        Args:
            page: Page object to chunk
            document: Parent document for metadata
            
        Returns:
            List of chunks for this page
        """
        if not page.text.strip():
            return []
        
        # Pre-process page text for better chunking
        processed_text = self._preprocess_page_text(page.text)
        
        # Split text using LangChain splitter
        text_chunks = self.text_splitter.split_text(processed_text)
        
        # Create chunk objects with metadata
        chunks = []
        current_char_pos = 0
        
        for i, chunk_text in enumerate(text_chunks):
            # Find actual position in original text
            start_pos = page.text.find(chunk_text.strip()[:50])  # Use first 50 chars as anchor
            if start_pos == -1:
                start_pos = current_char_pos
            
            end_pos = start_pos + len(chunk_text)
            current_char_pos = end_pos - self.chunk_overlap  # Account for overlap
            
            # Generate unique chunk ID
            chunk_id = f"{document.filename}_p{page.page_number}_c{i+1}"
            
            # Create chunk metadata
            chunk_metadata = {
                "source_document": document.filename,
                "source_page": page.page_number,
                "chunk_index": i,
                "chunk_type": self._classify_chunk_content(chunk_text),
                "page_metadata": page.metadata,
                "document_metadata": document.metadata
            }
            
            # Create chunk object
            chunk = Chunk(
                text=chunk_text.strip(),
                chunk_id=chunk_id,
                source_document=document.filename,
                page_numbers=[page.page_number],
                start_char=start_pos,
                end_char=end_pos,
                metadata=chunk_metadata
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _preprocess_page_text(self, text: str) -> str:
        """
        Pre-process page text for better chunking.
        
        Args:
            text: Raw page text
            
        Returns:
            Processed text optimized for chunking
        """
        if self.preserve_financial_tables:
            # Try to preserve financial table structure
            text = self._preserve_financial_tables(text)
        
        # Normalize whitespace while preserving structure
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double newline
        
        return text.strip()
    
    def _preserve_financial_tables(self, text: str) -> str:
        """
        Attempt to preserve financial table structure in text.
        
        Args:
            text: Page text that may contain financial tables
            
        Returns:
            Text with table structure markers
        """
        # Pattern to detect financial table rows (numbers with currency or percentage indicators)
        financial_patterns = [
            r'[$]\s*[\d,]+\.?\d*',  # Currency amounts
            r'[\d,]+\.?\d*\s*[%]',   # Percentages  
            r'[\d,]+\.?\d*\s*(million|billion|thousand)',  # Scale indicators
            r'\(\s*[\d,]+\.?\d*\s*\)',  # Negative numbers in parentheses
        ]
        
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            # Check if line contains financial data
            is_financial = any(re.search(pattern, line, re.IGNORECASE) for pattern in financial_patterns)
            
            if is_financial:
                # Add table preservation markers
                processed_lines.append(f"[FINANCIAL_DATA] {line.strip()}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _classify_chunk_content(self, chunk_text: str) -> str:
        """
        Classify the type of content in a chunk.
        
        Args:
            chunk_text: Text content of the chunk
            
        Returns:
            Content type classification
        """
        text_lower = chunk_text.lower()
        
        # Financial data indicators
        if any(keyword in text_lower for keyword in ['revenue', 'income', 'profit', 'assets', 'liabilities', 'cash flow']):
            if '[FINANCIAL_DATA]' in chunk_text:
                return 'financial_table'
            else:
                return 'financial_text'
        
        # Risk factors
        if any(keyword in text_lower for keyword in ['risk', 'uncertainty', 'challenge', 'threat']):
            return 'risk_factors'
        
        # Business description
        if any(keyword in text_lower for keyword in ['business', 'operations', 'strategy', 'market']):
            return 'business_description'
        
        # Management discussion
        if any(keyword in text_lower for keyword in ['management', 'discussion', 'analysis', 'outlook']):
            return 'management_discussion'
        
        return 'general'
    
    def _post_process_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Post-process chunks for quality and deduplication.
        
        Args:
            chunks: List of raw chunks
            
        Returns:
            Processed and deduplicated chunks
        """
        if not chunks:
            return []
        
        processed_chunks = []
        seen_content = set()
        
        for chunk in chunks:
            # Skip very short chunks
            if len(chunk.text.strip()) < 50:
                continue
            
            # Simple deduplication based on first 100 characters
            content_signature = chunk.text[:100].strip().lower()
            if content_signature in seen_content:
                continue
            
            seen_content.add(content_signature)
            
            # Clean chunk text
            chunk.text = self._clean_chunk_text(chunk.text)
            
            # Update metadata with processing info
            chunk.metadata['processed'] = True
            chunk.metadata['final_length'] = len(chunk.text)
            
            processed_chunks.append(chunk)
        
        return processed_chunks
    
    def _clean_chunk_text(self, text: str) -> str:
        """
        Clean and format chunk text.
        
        Args:
            text: Raw chunk text
            
        Returns:
            Cleaned chunk text
        """
        # Remove table preservation markers
        text = re.sub(r'\[FINANCIAL_DATA\]\s*', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def chunk_text_directly(self, text: str, source_name: str = "direct_input") -> List[Chunk]:
        """
        Chunk text directly without page structure.
        
        Args:
            text: Text to chunk
            source_name: Name to use as source identifier
            
        Returns:
            List of chunks
        """
        if not text.strip():
            return []
        
        # Pre-process text
        processed_text = self._preprocess_page_text(text)
        
        # Split using LangChain splitter
        text_chunks = self.text_splitter.split_text(processed_text)
        
        chunks = []
        current_pos = 0
        
        for i, chunk_text in enumerate(text_chunks):
            chunk_id = f"{source_name}_c{i+1}"
            
            chunk = Chunk(
                text=chunk_text.strip(),
                chunk_id=chunk_id,
                source_document=source_name,
                page_numbers=[1],  # Default to page 1 for direct text
                start_char=current_pos,
                end_char=current_pos + len(chunk_text),
                metadata={
                    "source_document": source_name,
                    "chunk_index": i,
                    "chunk_type": self._classify_chunk_content(chunk_text),
                    "direct_input": True
                }
            )
            
            chunks.append(chunk)
            current_pos += len(chunk_text) - self.chunk_overlap
        
        return self._post_process_chunks(chunks)


import time

if __name__ == "__main__":
    # Test the chunking strategy
    from src.extractors.text_extractor import TextExtractor, Document, Page
    
    # Create test document
    test_text = """
    Revenue Analysis
    
    Total revenue for fiscal year 2024 was $150 million, representing a 25% increase from the previous year's $120 million. This growth was driven by strong performance in our core business segments.
    
    Financial Position
    
    Assets: $500 million
    Liabilities: $300 million  
    Shareholders' Equity: $200 million
    
    The company maintains a strong balance sheet with total assets of $500 million and manageable debt levels.
    
    Risk Factors
    
    The company faces various risks including market competition, regulatory changes, and economic uncertainties that could impact future performance.
    """
    
    # Create mock document
    page = Page(page_number=1, text=test_text, metadata={"width": 612, "height": 792})
    document = Document(
        filepath="test.pdf",
        filename="test.pdf", 
        pages=[page],
        total_pages=1,
        metadata={"title": "Test Financial Report"}
    )
    
    # Test chunking
    chunker = BasicChunkingStrategy(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_document(document)
    
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({chunk.chunk_id}):")
        print(f"Type: {chunk.metadata['chunk_type']}")
        print(f"Length: {len(chunk.text)}")
        print(f"Text preview: {chunk.text[:100]}...")
    
    # Test direct text chunking
    direct_chunks = chunker.chunk_text_directly(test_text, "direct_test")
    print(f"\nDirect chunking created {len(direct_chunks)} chunks")
