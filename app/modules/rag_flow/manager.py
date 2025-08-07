"""
Example code for a product manager module in a FastAPI application.
This code includes methods for creating, reading, updating, and deleting products.
Remove this code if it's not relevant to your project.
"""

import tempfile
from fastapi import HTTPException, Request
from app.models.api_schema import RawFlowProcessChunks
from app.services.aws_service import download_file_from_s3
from app.utils.logger import logger
from app.common.constants import STATUS_TYPES
from app.config.main import Config

from rag.app.paper import chunk as paper_chunk
from rag.app.naive import chunk as naive_chunk
from rag.app.book import chunk as book_chunk
from rag.app.laws import chunk as laws_chunk
from rag.app.manual import chunk as manual_chunk

import sys
import os
import json

class Manager:

    def __init__(self, request: Request, data: RawFlowProcessChunks):
        if data.tenantId is None:
            raise HTTPException(status_code=400, detail="Tenant ID not provided in request")
        self.request = request

        self.data = data
        self.method = data.chunkingMethod if data.chunkingMethod else "naive"
        self.tokens = data.chunkingTokenSize if data.chunkingTokenSize else 512
        self.layout = data.chunkingLayout if data.chunkingLayout else "DeepDOC"
        self.output = data.outputFile if data.outputFile else None


    async def process_chunks(self):        
        try:

            # Create a temporary file path
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name + self.data.s3URL

            print(temp_file_path, self.data.s3URL)
            # Download file from S3 using download_file_from_s3
            download_file_from_s3(temp_file_path, self.data.s3URL)

            chunks = self.main(temp_file_path)

            return {
                "chunks": chunks,
            }

        except Exception as e:
            logger.error(f"Error in process_chunks: {str(e)}")
            return {
                "message": "Error in process_chunks",
                "summary": str(e),
            }

    def progress_callback(self, progress=None, msg="", **kwargs):
        """Progress callback"""
        if progress is not None:
            print(f"Progress: {progress*100:.1f}% - {msg}")
        else:
            print(f"Status: {msg}")

    def extract_chunks(self, pdf_path, method="naive", token_size=512, layout="DeepDOC",
                    from_page=0, to_page=100000, language="English"):
        """Extract chunks directly using RAGFlow chunking methods"""
        # Read PDF
        with open(pdf_path, 'rb') as f:
            binary = f.read()

        filename = os.path.basename(pdf_path)

        # Create config - ONLY using parameters that exist in RAGFlow code
        # These are the only parameters used in paper.py line 147-150
        parser_config = {
            "chunk_token_num": token_size,
            "delimiter": "\n!?。；！？",
            "layout_recognize": layout
        }

        print(f"📄 Processing: {filename}")
        print(f"🔧 Method: {method}")
        print(f"⚙️ Config: {parser_config}")

        # Get chunking function
        chunking_functions = {
            "paper": paper_chunk,
            "naive": naive_chunk,
            "book": book_chunk,
            "laws": laws_chunk,
            "manual": manual_chunk
        }

        if method not in chunking_functions:
            raise ValueError(f"Unknown method: {method}")

        # Call chunking function directly with ONLY the parameters used in RAGFlow
        chunks = chunking_functions[method](
            filename=filename,
            binary=binary,
            from_page=from_page,
            to_page=to_page,
            lang=language,
            callback=self.progress_callback,
            parser_config=parser_config
        )

        print(f"✅ Generated {len(chunks)} chunks")
        return chunks

    def save_chunks(self, chunks, output_file):
        """Save chunks to JSON"""
        # Make chunks serializable
        serializable_chunks = []
        for chunk in chunks:
            if isinstance(chunk, dict):
                processed = {}
                for key, value in chunk.items():
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        processed[key] = value
                    else:
                        processed[key] = str(value)
                serializable_chunks.append(processed)
            else:
                serializable_chunks.append(str(chunk))

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_chunks, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(chunks)} chunks to: {output_file}")

    def main(self, file_path):
        """Main function"""

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        # Extract chunks
        chunks = self.extract_chunks(
            pdf_path= file_path,
            method=self.method,
            token_size=self.tokens,
            layout=self.layout
        )

        # Save chunks
        if self.output:
            output_file = self.output
        else:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = f"{base_name}_chunks.json"

        self.save_chunks(chunks, output_file)

        filtered_chunks = [{"content_with_weight": c["content_with_weight"]} for c in chunks if "content_with_weight" in c]

        return filtered_chunks
