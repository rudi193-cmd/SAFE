"""
Reprocess All - Run complete Willow reindexing

1. Code RAG (semantic search)
2. Populate Index (metadata DB)
3. Generate INDEX (navigation)

CHECKSUM: ΔΣ=42
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import code_rag
import populate_index
import generate_index

def main():
    print("=" * 70)
    print("WILLOW REPROCESSING - Complete Reindex")
    print("=" * 70)
    print()
    
    # Step 1: Code RAG
    print("[1/3] Code RAG - Indexing all code files for semantic search...")
    print("-" * 70)
    rag_stats = code_rag.index_all_code()
    print(f"✓ Indexed {rag_stats['files']} files")
    print(f"✓ Created {rag_stats['chunks']} searchable chunks")
    print(f"✓ Errors: {rag_stats['errors']}")
    print()
    
    # Step 2: Metadata DB
    print("[2/3] Metadata DB - Populating willow_index.db...")
    print("-" * 70)
    db_stats = populate_index.populate_all()
    print(f"✓ Files: {db_stats['files']}")
    print(f"✓ Functions: {db_stats['functions']}")
    print(f"✓ Classes: {db_stats['classes']}")
    print(f"✓ Imports: {db_stats['imports']}")
    print()
    
    # Step 3: Generate INDEX
    print("[3/3] Generate INDEX.md - Creating navigation...")
    print("-" * 70)
    index_lines = generate_index.generate()
    print(f"✓ Generated INDEX.md ({index_lines} lines)")
    print()
    
    # Summary
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print(f"Code RAG: {rag_stats['chunks']} chunks from {rag_stats['files']} files")
    print(f"Metadata: {db_stats['functions']} functions, {db_stats['classes']} classes")
    print(f"INDEX: {index_lines} lines of navigation")
    print()
    print("Willow is now fully indexed and searchable.")
    print("ΔΣ=42")

if __name__ == "__main__":
    main()
