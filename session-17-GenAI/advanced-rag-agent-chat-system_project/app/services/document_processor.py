from typing import List, Dict, Any
import os
from pathlib import Path
from loguru import logger
from openai import AsyncOpenAI
import base64
from io import BytesIO
from PIL import Image
import PyPDF2
from docx import Document as DocxDocument

from app.core.config import settings


class DocumentProcessor:
    """
    Processes documents with Vision-based parsing for complex structures
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process_document(
        self,
        file_path: str,
        file_type: str
    ) -> List[Dict[str, Any]]:
        """Process document and return chunks with metadata"""
        logger.info(f"Processing document: {file_path} (type: {file_type})")
        
        if file_type == ".pdf":
            return await self.process_pdf(file_path)
        elif file_type == ".docx":
            return await self.process_docx(file_path)
        elif file_type in [".txt", ".md"]:
            return await self.process_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    async def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Process PDF with vision-based parsing for tables and complex layouts"""
        chunks = []
        
        try:
            # Convert PDF pages to images for vision parsing
            from pdf2image import pdftoimage
            
            images = pdftoimage.convert_from_path(file_path)
            
            for page_num, image in enumerate(images, start=1):
                logger.info(f"Processing PDF page {page_num}")
                
                # Convert image to base64
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Use GPT-4 Vision to parse the page
                page_content = await self._vision_parse_page(
                    img_base64,
                    page_num
                )
                
                # Chunk the parsed content
                page_chunks = self._chunk_text(
                    page_content,
                    metadata={
                        'page': page_num,
                        'source': file_path,
                        'type': 'pdf'
                    }
                )
                
                chunks.extend(page_chunks)
        
        except ImportError:
            # Fallback to text extraction if pdf2image not available
            logger.warning("pdf2image not available, using text extraction fallback")
            chunks = await self._pdf_text_fallback(file_path)
        
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            # Fallback to text extraction
            chunks = await self._pdf_text_fallback(file_path)
        
        logger.info(f"Extracted {len(chunks)} chunks from PDF")
        return chunks
    
    async def _vision_parse_page(
        self,
        img_base64: str,
        page_num: int
    ) -> str:
        """Use GPT-4 Vision to parse page content including tables and structure"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Extract all text content from this document page. 
                                
Preserve the structure and format:
- Maintain headers and their hierarchy
- Extract tables as markdown tables
- Preserve lists and bullet points
- Include figure captions
- Maintain paragraph breaks

Be thorough and accurate."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            return f"[Page {page_num}]\n\n{content}"
            
        except Exception as e:
            logger.error(f"Vision parsing failed for page {page_num}: {str(e)}")
            return f"[Page {page_num}] - Error parsing page"
    
    async def _pdf_text_fallback(self, file_path: str) -> List[Dict[str, Any]]:
        """Fallback text extraction from PDF"""
        chunks = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                
                page_chunks = self._chunk_text(
                    text,
                    metadata={
                        'page': page_num,
                        'source': file_path,
                        'type': 'pdf'
                    }
                )
                
                chunks.extend(page_chunks)
        
        return chunks
    
    async def process_docx(self, file_path: str) -> List[Dict[str, Any]]:
        """Process DOCX file"""
        chunks = []
        
        doc = DocxDocument(file_path)
        full_text = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        
        text = '\n\n'.join(full_text)
        
        chunks = self._chunk_text(
            text,
            metadata={
                'source': file_path,
                'type': 'docx'
            }
        )
        
        logger.info(f"Extracted {len(chunks)} chunks from DOCX")
        return chunks
    
    async def process_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Process plain text or markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = self._chunk_text(
            text,
            metadata={
                'source': file_path,
                'type': Path(file_path).suffix
            }
        )
        
        logger.info(f"Extracted {len(chunks)} chunks from text file")
        return chunks
    
    def _chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk_size: int = None,
        overlap: int = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk text with overlap, preserving semantic boundaries
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if overlap is None:
            overlap = settings.CHUNK_OVERLAP
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_text,
                    'metadata': {
                        **metadata,
                        'chunk_size': len(chunk_text)
                    }
                })
                
                # Start new chunk with overlap
                # Keep last paragraph for context
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], para]
                    current_size = len(current_chunk[-1]) + para_size
                else:
                    current_chunk = [para]
                    current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'metadata': {
                    **metadata,
                    'chunk_size': len(chunk_text)
                }
            })
        
        return chunks