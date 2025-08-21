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
from deepdoc.parser.pdf_parser import RAGFlowPdfParser

from rag.app.paper import chunk as paper_chunk
from rag.app.naive import chunk as naive_chunk
from rag.app.book import chunk as book_chunk
from rag.app.laws import chunk as laws_chunk
from rag.app.manual import chunk as manual_chunk
from rag.app.presentation import chunk as ppt_chunk
from rag.app.qa import chunk as qa_chunk
from rag.app.table import chunk as table_chunk
from rag.app.resume import chunk as resume_chunk
from rag.app.picture import chunk as pic_chunk
from rag.app.one import chunk as one_chunk
from rag.app.email_update import chunk as email_chunk
from rag.app.tag import chunk as tag_chunk


import sys
import os
import re
import json
import time
import hashlib
from email.message import EmailMessage
from datetime import datetime, timezone
import base64

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
        # self.kb_id=data.kb_id
    
#     def _convert_to_eml(self, original_filename, original_binary, callback):
#         """
#         Converts a document containing email text into a clean, valid .eml file.
#         """
#         # Step 1: Reliably extract the full text from the source document.
#         text_chunks = one_chunk(
#             filename=original_filename,
#             binary=original_binary,
#             callback=callback
#         )
#         full_text = "\n".join([c.get('content_with_weight', '') for c in text_chunks])

#         if not full_text.strip():
#             raise ValueError("Failed to extract any text from the document. The document might be empty or image-based.")

#         # Step 2: Intelligently find the original headers and the true email body.
#         from_addr = re.search(r"^\s*From\s*:\s*(.+)$", full_text, re.MULTILINE | re.IGNORECASE)
#         to_addr = re.search(r"^\s*To\s*:\s*(.+)$", full_text, re.MULTILINE | re.IGNORECASE)
#         subject = re.search(r"^\s*Subject\s*:\s*(.+)$", full_text, re.MULTILINE | re.IGNORECASE)

#         # Default to the entire text as the body.
#         email_body = full_text

#         # Find the end of the last known header to reliably find where the body begins.
#         header_end_index = max(
#             (from_addr.end() if from_addr else -1),
#             (to_addr.end() if to_addr else -1),
#             (subject.end() if subject else -1)
#         )

#         if header_end_index != -1:
#             # The body starts after the first blank line following the headers.
#             body_start_index = full_text.find('\n\n', header_end_index)
#             if body_start_index != -1:
#                 # We have successfully isolated the true body of the original email.
#                 email_body = full_text[body_start_index:].strip()
        
#         # Step 3: Construct a new, clean EML file using the parts we found.
#         # Prioritize using the headers found in the text; otherwise, use defaults.
#         from_email = from_addr.group(1).strip() if from_addr else "sender@example.com"
#         to_email = to_addr.group(1).strip() if to_addr else "receiver@example.com"
#         subject_text = subject.group(1).strip() if subject else f"Converted: {original_filename}"

#         # Manually construct the raw EML content as a string for maximum reliability.
#         eml_content = f"""From: {from_email}
# To: {to_email}
# Subject: {subject_text}
# Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')}
# MIME-Version: 1.0
# Content-Type: text/plain; charset="utf-8"
# Content-Transfer-Encoding: 8bit

# {email_body}"""

#         # Step 4: Encode the clean string to binary and return.
#         new_eml_filename = os.path.splitext(original_filename)[0] + ".eml"
#         eml_binary = eml_content.encode('utf-8')

#         print(f"✅ Clean EML conversion complete. New file: {new_eml_filename}")
#         print(f"📄 EML body length: {len(email_body)} characters")
#         return new_eml_filename, eml_binary

#     def _convert_to_eml(self, original_filename, original_binary, callback):
#         """
#         Extracts text and creates an EML file with a special header
#         containing the original, rich text with parser tags.
#         """
#         # 1. Reliably extract text using one_chunk. The output contains special tags.
#         text_chunks = one_chunk(
#             filename=original_filename,
#             binary=original_binary,
#             callback=callback
#         )
#         # The text with '@@...##' tags is in the 'content_with_weight' key
#         tagged_text = "\n".join([c.get('content_with_weight', '') for c in text_chunks])

#         if not tagged_text.strip():
#             raise ValueError("Failed to extract any text from the document.")

#         # 2. Create a clean, plain-text version for the visible email body
#         # by removing the special tags.
#         plain_text_body = RAGFlowPdfParser.remove_tag(tagged_text)

#         # 3. Encode the original tagged text to safely put it in a header.
#         encoded_tagged_text = base64.b64encode(tagged_text.encode('utf-8')).decode('ascii')

#         # 4. Manually construct the raw EML content with our special header.
#         eml_content = f"""From: sender@example.com
# To: receiver@example.com
# Subject: Converted: {original_filename}
# Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')}
# MIME-Version: 1.0
# X-RAGFlow-Tagged-Text: {encoded_tagged_text}
# Content-Type: text/plain; charset="utf-8"
# Content-Transfer-Encoding: 8bit

# {plain_text_body}"""

#         # 5. Encode the clean string to binary and return.
#         new_eml_filename = os.path.splitext(original_filename)[0] + ".eml"
#         eml_binary = eml_content.encode('utf-8')

#         print(f"✅ Advanced EML conversion complete. New file: {new_eml_filename}")
#         return new_eml_filename, eml_binary
    
# #     # ... (all other functions in manager.py like process_chunks, main, etc., are unchanged) ...





#earlier working

    def _convert_to_eml(self, original_filename, original_binary, callback):
        """
        Extracts text and creates an EML file with a special header
        containing the original, rich text with parser tags.
        """
        # 1. Reliably extract text using one_chunk.
        text_chunks = one_chunk(
            filename=original_filename,
            binary=original_binary,
            callback=callback
        )
        tagged_text = "\n".join([c.get('content_with_weight', '') for c in text_chunks])

        if not tagged_text.strip():
            raise ValueError("Failed to extract any text from the document.")

        # 2. Create a clean, plain-text version for parsing and for the body.
        plain_text_body = RAGFlowPdfParser.remove_tag(tagged_text)

        # 3. **NEW**: Intelligently find the original headers in the plain text.
        from_addr = re.search(r"^\s*From\s*:\s*(.+)$", plain_text_body, re.MULTILINE | re.IGNORECASE)
        to_addr = re.search(r"^\s*To\s*:\s*(.+)$", plain_text_body, re.MULTILINE | re.IGNORECASE)
        subject = re.search(r"^\s*Subject\s*:\s*(.+)$", plain_text_body, re.MULTILINE | re.IGNORECASE)

        # 4. **NEW**: Use the extracted headers, with safe fallbacks.
        from_email = from_addr.group(1).strip() if from_addr else "sender@example.com"
        to_email = to_addr.group(1).strip() if to_addr else "receiver@example.com"
        subject_text = subject.group(1).strip() if subject else f"Converted: {original_filename}"
        
        # 5. Encode the original tagged text to safely put it in the special header.
        encoded_tagged_text = base64.b64encode(tagged_text.encode('utf-8')).decode('ascii')

        # 6. Manually construct the raw EML content using the **extracted headers**.
        eml_content = f"""From: {from_email}
To: {to_email}
Subject: {subject_text}
Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')}
MIME-Version: 1.0
X-RAGFlow-Tagged-Text: {encoded_tagged_text}
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 8bit

{plain_text_body}"""

        # 7. Encode the clean string to binary and return.
        new_eml_filename = os.path.splitext(original_filename)[0] + ".eml"
        eml_binary = eml_content.encode('utf-8')

        print(f"✅ Advanced EML conversion complete. New file: {new_eml_filename}")
        return new_eml_filename, eml_binary


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
        
        if method == 'email':
            filename,binary= self._convert_to_eml(filename,binary,callback=self.progress_callback)

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
            "manual": manual_chunk,
            "presentation":ppt_chunk,
            "email":email_chunk,
            "one":one_chunk,
            "qa":qa_chunk,
            "tag":tag_chunk,
            "table":table_chunk,
            "resume":resume_chunk,
            "picture":pic_chunk,        
            
            
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
            parser_config=parser_config,
            # kb_id=self.kb_id
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
        formatted_chunks=[]
        for i,chunk in enumerate (chunks):
            content=chunk.get("content_with_weight","")
            if not content:
                content_tokens = chunk.get("content_tks", [])
                content = "".join(content_tokens)

            # If content is still empty, skip this chunk to avoid empty records
            if not content.strip():
                continue

            chunk_hash=hashlib.sha256(content.encode('utf-8')).hexdigest()
            new_chunk={
                "content":content,
                "created":int(time.time()*1000),
                "metaData":{
                    "fileName":chunk.get("docnm_kwd", self.data.s3URL.split('/')[-1]),
                    "file":f"https://s3.{os.getenv('ZBRAIN_S3_REGION')}.amazonaws.com/{os.getenv('ZBRAIN_S3_BUCKET_NAME')}/{self.data.s3URL}",
                    "characters":len(content),
                    "id":i,
                    "hash":chunk_hash,
                    "words":len(content.split()),
                    "isActive":True,
                    "knowledgeBaseImportId":self.data.s3URL.split('/')[-2]
                }
            }
            formatted_chunks.append(new_chunk)
        

        return formatted_chunks

