from typing import List, Dict, Any

def build_citations(matches: List[Dict[str, Any]]) -> str:
    """
    Format a list of Pinecone matches into a beautiful, structured markdown citation section.
    Deduplicates sources by title and shows the highest match relevance score.
    """
    if not matches:
        return ""
        
    # Aggregate matches by document title
    sources = {}
    for match in matches:
        title = match.get("title", "Unknown Document")
        score = match.get("score", 0.0)
        text_snippet = match.get("text", "")
        tags = match.get("tags", [])
        
        # Keep the highest relevance score and aggregate tags
        if title not in sources:
            sources[title] = {
                "max_score": score,
                "snippets": [text_snippet[:120].strip() + "..."],
                "tags": set(tags[:5])
            }
        else:
            if score > sources[title]["max_score"]:
                sources[title]["max_score"] = score
            sources[title]["tags"].update(tags[:3])
            if len(sources[title]["snippets"]) < 2:
                sources[title]["snippets"].append(text_snippet[:120].strip() + "...")
                
    # Build markdown citation text
    lines = ["\n\n### 📚 Sources Referenced\n"]
    for idx, (title, info) in enumerate(sources.items(), 1):
        relevance_percent = int(info["max_score"] * 100)
        tags_str = ", ".join(info["tags"]) if info["tags"] else "General"
        
        lines.append(f"{idx}. **{title}** (Relevance: {relevance_percent}%)")
        lines.append(f"   * *Topics*: {tags_str}")
        lines.append(f"   * *Excerpt*: \"{info['snippets'][0]}\"")
        if len(info["snippets"]) > 1:
            lines.append(f"   * *Excerpt*: \"{info['snippets'][1]}\"")
            
    return "\n".join(lines)
