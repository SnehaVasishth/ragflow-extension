# email_update.py (Corrected)

import logging
from email import policy
from email.parser import BytesParser
from rag.app.naive import chunk as naive_chunk
import re
from rag.nlp import rag_tokenizer, naive_merge, tokenize_chunks
from deepdoc.parser import HtmlParser, TxtParser
from timeit import default_timer as timer
import io
import base64

def chunk(
    filename,
    binary=None,
    from_page=0,
    to_page=100000,
    lang="Chinese",
    callback=None,
    **kwargs,
):
    """
    Only eml is supported
    """
    eng = lang.lower() == "english"
    parser_config = kwargs.get(
        "parser_config",
        {"chunk_token_num": 512, "delimiter": "\n!?。；！？", "layout_recognize": "DeepDOC"},
    )
    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)),
    }
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])
    main_res = []
    attachment_res = []

    if binary:
        msg = BytesParser(policy=policy.default).parse(io.BytesIO(binary))
    else:
        msg = BytesParser(policy=policy.default).parse(open(filename, "rb"))

    # 1. Check for the special header with high-fidelity tagged text.
    tagged_text_b64 = msg.get("X-RAGFlow-Tagged-Text")

    if tagged_text_b64:
        # 2. If it exists, use the advanced path for converted documents.
        print("✅ Found high-fidelity tagged text in EML header. Using advanced path.")
        tagged_text = base64.b64decode(tagged_text_b64).decode('utf-8')
        sections = TxtParser.parser_txt(tagged_text)
        chunks = naive_merge(sections, int(parser_config.get("chunk_token_num", 128)), parser_config.get("delimiter", "\n!?。；！？"))
    else:
        # 3. If it's a normal EML file, use the simple, robust fallback.
        print("INFO: No tagged text found. Processing as a standard EML file.")
        text_txt, html_txt = [], []
        for header, value in msg.items():
            text_txt.append(f"{header}: {value}")

        def _add_content(msg_part):
            nonlocal text_txt, html_txt
            if msg_part.get_content_type() == "text/plain":
                try: text_txt.append(msg_part.get_payload(decode=True).decode(msg_part.get_content_charset()))
                except: pass
            # **FIXED**: Added logic to handle HTML parts
            elif msg_part.get_content_type() == "text/html":
                try: html_txt.append(msg_part.get_payload(decode=True).decode(msg_part.get_content_charset()))
                except: pass
            elif msg_part.is_multipart():
                for sub_part in msg_part.iter_parts(): _add_content(sub_part)
        
        _add_content(msg)
        
        # **FIXED**: Combine both text and the converted text from the HTML part
        full_text = "\n".join(text_txt)
        if html_txt:
            html_as_text = "\n".join(HtmlParser.parser_txt("\n".join(html_txt)))
            full_text += "\n" + html_as_text

        chunks = [sec for sec, pos in TxtParser.parser_txt(full_text) if sec.strip()]

    if not chunks:
        raise ValueError("Document is empty after parsing.")

    main_res.extend(tokenize_chunks(chunks, doc, eng, None))
    
    # Attachment logic remains unchanged
    # ... (rest of the function is the same) ...
    for part in msg.iter_attachments():
        content_disposition = part.get("Content-Disposition")
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if dispositions[0].lower() == "attachment":
                attachment_filename = part.get_filename()
                if attachment_filename:
                    payload = part.get_payload(decode=True)
                    try:
                        attachment_res.extend(
                            naive_chunk(attachment_filename, payload, callback=callback, **kwargs)
                        )
                    except Exception as e:
                        logging.warning(f"Failed to chunk attachment {attachment_filename}: {e}")

    return main_res + attachment_res