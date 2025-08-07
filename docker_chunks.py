"""
Docker-Compatible RAGFlow Chunker
Uses only existing RAGFlow chunking methods and parameters
"""

import sys
import os
import json

try:
    # Import chunking methods - this works in Docker
    from rag.app.paper import chunk as paper_chunk
    from rag.app.naive import chunk as naive_chunk
    from rag.app.book import chunk as book_chunk
    from rag.app.laws import chunk as laws_chunk
    from rag.app.manual import chunk as manual_chunk
    
    print("✅ RAGFlow chunking modules imported successfully!")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this script in the RAGFlow container")
    sys.exit(1)

def progress_callback(progress=None, msg="", **kwargs):
    """Progress callback"""
    if progress is not None:
        print(f"Progress: {progress*100:.1f}% - {msg}")
    else:
        print(f"Status: {msg}")

def extract_chunks(pdf_path, method="naive", token_size=512, layout="DeepDOC",
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
        callback=progress_callback,
        parser_config=parser_config
    )
    
    print(f"✅ Generated {len(chunks)} chunks")
    return chunks

def save_chunks(chunks, output_file):
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

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAGFlow Docker Chunker")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--method", default="naive", 
                       choices=["paper", "naive", "book", "laws", "manual"],
                       help="Chunking method")
    parser.add_argument("--tokens", type=int, default=512,
                       help="Token size")
    parser.add_argument("--layout", default="DeepDOC",
                       choices=["DeepDOC", "Plain Text"],
                       help="Layout recognition")
    parser.add_argument("--output", default=None,
                       help="Output JSON file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"❌ File not found: {args.pdf_path}")
        return
    
    # Extract chunks
    chunks = extract_chunks(
        pdf_path=args.pdf_path,
        method=args.method,
        token_size=args.tokens,
        layout=args.layout
    )
    
    # Save chunks
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        output_file = f"{base_name}_chunks.json"
    
    save_chunks(chunks, output_file)

if __name__ == "__main__":
    main()