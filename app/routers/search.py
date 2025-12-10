import json
import os
import re
import difflib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

UPLOAD_DIR = "uploads"

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    max_results: int = 20
    fuzzy_threshold: float = 0.6

class SearchResult(BaseModel):
    text: str
    file_name: str
    page_number: int
    score: float
    source: Optional[str] = None
    metadata: Optional[dict] = None

def get_fuzzy_score(query: str, text: str) -> float:
    """
    Returns a score between 0 and 1 indicating how well the query matches the text.
    Uses difflib.SequenceMatcher for string similarity.
    """
    if not text: return 0.0
    
    # Normalization
    query_lower = query.lower()
    text_lower = text.lower()
    
    # 1. Exact substring match (Highest Priority)
    if query_lower in text_lower:
        return 1.0
    
    # 2. Key word match (words present)
    query_words = query_lower.split()
    if not query_words: return 0.0
    
    words_in_text = 0
    for word in query_words:
        if word in text_lower:
            words_in_text += 1
    
    word_overlap_score = words_in_text / len(query_words)
    
    # 3. Fuzzy match (SequenceMatcher)
    # This is expensive on long text, so we might want to check overlap first
    if word_overlap_score > 0.5:
        return 0.9  # High confidence if most words are there
        
    s = difflib.SequenceMatcher(None, query_lower, text_lower)
    match = s.find_longest_match(0, len(query_lower), 0, len(text_lower))
    
    # If the longest match is a significant portion of the query, it's a good hit
    if match.size / len(query_lower) > 0.7:
        return 0.8
        
    # Standard ratio
    return s.ratio()

@router.post("")
async def search(query: SearchQuery) -> List[SearchResult]:
    """
    Search extracted text for query using fuzzy matching.
    Reads from *_extracted.json files.
    """
    results = []
    
    try:
        # Iterate over all _extracted.json files in UPLOAD_DIR
        if not os.path.exists(UPLOAD_DIR):
            return []

        print(f"DEBUG: Searching in {UPLOAD_DIR}")
        for filename in os.listdir(UPLOAD_DIR):
            print(f"DEBUG: Found file {filename}")
            if filename.endswith('_extracted.json'):
                file_path = os.path.join(UPLOAD_DIR, filename)
                original_filename = filename.replace('_extracted.json', '')
                if original_filename.endswith('_cellinfo.json'): 
                    continue # Skip aux files if named poorly
                
                # Determine original file name (strip extra suffix if any)
                # Our convention: "doc.pdf_extracted.json" -> "doc.pdf"
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        blocks = json.load(f)
                        
                    for block in blocks:
                        text = block.get("text", "")
                        score = get_fuzzy_score(query.query, text)
                        
                        if score >= query.fuzzy_threshold:
                            results.append(SearchResult(
                                text=text,
                                file_name=original_filename,
                                page_number=block.get("page", 1),
                                score=score,
                                source=block.get("source", "unknown"),
                                metadata=block.get("metadata", {})
                            ))
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    continue

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        print(f"DEBUG: Found {len(results)} results")
        return results[:query.max_results]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))