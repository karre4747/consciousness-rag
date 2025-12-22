# 🛑 CRITICAL HANDOFF STATUS - READ ME FIRST

**Date:** December 20, 2025
**System State:** High-Performance RAG (64GB RAM Mac Studio)
**Server:** `localhost:8001` (uvicorn)

## 🚀 Current Mission
The user is processing a backlog of ~500 large PDF documents (books).
**Goal:** Run "Deep Analysis" (Pass 3) on all documents using **FULL TEXT CONTEXT**.

## ✅ WHAT IS FIXED & WORKING
1.  **Limits Removed:** I have removed the legacy 500-character limits in:
    *   `backend/main.py`: Now aggregates ALL chunks of a document into `full_text` before analysis.
    *   `backend/tagging.py`: Now accepts up to 100k characters for Claude analysis prompts.
    *   `backend/tagging.py`: OpenAI tagging (Pass 2) now reads full chunk text (limit removed).
    
2.  **"Analyze Pending" Button:**
    *   Added to `index.html` (Analysis Tab).
    *   Automatically fetches *only* un-analyzed documents.
    *   Use this for "Autopilot" processing.

3.  **Cost Tracking:**
    *   Dashboard updated to show "API Spending" (OpenAI vs Claude).
    *   Verified working.

## ⚠️ KNOWN FRICTIONS / UI CONFUSION
1.  **"Re-tag Selected" Button:**
    *   *Issue:* Only works if you first click "Verify Tagging Status" to reveal the specific checkboxes (`.retag-select`).
    *   *User Confusion:* User tries to use it from other tabs where checkboxes are `.doc-select`.
    *   *Fix:* Needs to be unified or clearly instructed.

2.  **"Analyze Selected" Button:**
    *   *Issue:* Sometimes fails silently if polling refreshes the list while selecting.
    *   *Workaround:* Use "Analyze Pending" instead.

## ⏭️ IMMEDIATE NEXT STEPS (For Next Agent)
1.  **Verify Server is Running:** It should be on port 8001. If not, start it: `python3 -m uvicorn main:app --host 0.0.0.0 --port 8001`
2.  **Execute Analysis:**
    *   Instruct user to click **"Analyze Pending"**. 
    *   Monitor logs (`tail -f` or similar) to confirm FULL TEXT is being processed (look for "Aggregated X unique documents").
3.  **Address "Tags" vs "Analysis":**
    *   User wants to "upgrade" shallow tags. Currently requires "Re-tag Selected" (OpenAI).
    *   Consider adding a "Re-process Complete Document" workflow that does Pass 2 + Pass 3 in one go.

## 📂 Key Files Modified
- `backend/main.py`: Deduplication & Aggregation logic added to `/analyze-documents`.
- `backend/tagging.py`: Limits removed in `generate_tags_batch_openai` and `claude_second_pass_analysis`.
- `backend/static/index.html`: Added "Analyze Pending" button.

**Codebase is currently in "unlimited" mode. Do not revert to 500-char limits.**
