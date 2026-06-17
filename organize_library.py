#!/usr/bin/env python3
"""
Consciousness RAG - Document Library Organizer
Scans folders for PDFs/DOCX and suggests collection placement based on filename/content analysis
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
import re

# Collection definitions with keywords
COLLECTIONS = {
    "addiction_recovery/substances/alcohol": [
        "alcohol", "alcoholism", "aa", "big book", "alcoholic", "drinking", "drunk", "sober", "sobriety"
    ],
    "addiction_recovery/substances/drugs": [
        "drugs", "narcotics", "opioid", "cocaine", "meth", "heroin", "fentanyl", "substance", "na"
    ],
    "addiction_recovery/substances/gambling": [
        "gambling", "gambler", "casino", "betting", "lottery"
    ],
    "addiction_recovery/behavioral/codependency": [
        "codependent", "codependency", "enabling", "boundaries", "relationship addiction"
    ],
    "addiction_recovery/behavioral/love_addiction": [
        "love addiction", "romantic obsession", "relationship patterns"
    ],
    "addiction_recovery/12_step_deep_dives/step_1": [
        "step 1", "step_1", "powerless", "unmanageable", "first step"
    ],
    "addiction_recovery/12_step_deep_dives/step_2": [
        "step 2", "step_2", "came to believe", "higher power", "sanity"
    ],
    "addiction_recovery/12_step_deep_dives/step_3": [
        "step 3", "step_3", "decision", "turn over", "will", "care of god"
    ],
    "addiction_recovery/12_step_deep_dives/step_4": [
        "step 4", "step_4", "inventory", "fourth step", "resentments", "character defects"
    ],
    "addiction_recovery/12_step_deep_dives/step_11": [
        "step 11", "step_11", "prayer", "meditation", "conscious contact", "eleventh step"
    ],
    "addiction_recovery/recovery_stages/detox": [
        "detox", "withdrawal", "physical dependence", "cleansing"
    ],
    "addiction_recovery/recovery_stages/early_recovery": [
        "early recovery", "first 90 days", "pink cloud", "newcomer"
    ],
    "addiction_recovery/recovery_stages/spiritual_awakening": [
        "spiritual awakening", "transformation", "rebirth", "step 12"
    ],
    "metaphysics/teachers/blavatsky": [
        "blavatsky", "secret doctrine", "isis unveiled", "theosophy", "mahatma"
    ],
    "metaphysics/teachers/goddard": [
        "goddard", "neville", "imagination", "feeling is the secret", "manifesting"
    ],
    "metaphysics/teachers/steiner": [
        "steiner", "rudolf", "anthroposophy", "waldorf", "spiritual science"
    ],
    "metaphysics/teachers/murphy": [
        "murphy", "joseph murphy", "subconscious mind", "power of subconscious"
    ],
    "metaphysics/teachers/hawkins": [
        "hawkins", "david hawkins", "consciousness levels", "map of consciousness", "power vs force"
    ],
    "metaphysics/teachers/dispenza": [
        "dispenza", "joe dispenza", "breaking the habit", "becoming supernatural"
    ],
    "metaphysics/teachers/lipton": [
        "lipton", "bruce lipton", "biology of belief", "epigenetics"
    ],
    "metaphysics/teachers/leadbeater": [
        "leadbeater", "charles leadbeater", "clairvoyance", "thought forms", "chakras"
    ],
    "metaphysics/teachers/besant": [
        "besant", "annie besant", "ancient wisdom"
    ],
    "metaphysics/teachers/hall": [
        "manly", "manly p hall", "manly hall", "secret teachings", "philosophical research"
    ],
    "metaphysics/traditions/hermetic": [
        "hermetic", "hermes", "kybalion", "emerald tablet", "thoth"
    ],
    "metaphysics/traditions/kabbalah": [
        "kabbalah", "kabbalistic", "tree of life", "sephiroth", "zohar"
    ],
    "metaphysics/traditions/vedic": [
        "vedic", "vedas", "upanishads", "sanskrit", "brahman"
    ],
    "metaphysics/traditions/buddhist": [
        "buddhist", "buddhism", "dharma", "buddha", "noble truths", "nirvana"
    ],
    "metaphysics/traditions/taoist": [
        "tao", "taoism", "yin yang", "i ching", "lao tzu"
    ],
    "metaphysics/energy_systems/chakras": [
        "chakra", "kundalini", "anahata", "muladhara", "sahasrara", "third eye"
    ],
    "metaphysics/energy_systems/meridians": [
        "meridian", "acupuncture", "tcm", "qi", "chi", "lung meridian"
    ],
    "science_bridge/quantum_physics/consciousness_observer": [
        "observer effect", "quantum consciousness", "measurement problem", "copenhagen"
    ],
    "science_bridge/quantum_physics/quantum_brain": [
        "quantum brain", "microtubules", "orch or", "penrose", "hameroff"
    ],
    "science_bridge/neuroscience/addiction_neurobiology": [
        "dopamine", "reward pathway", "nucleus accumbens", "addiction brain", "neurotransmitter"
    ],
    "science_bridge/neuroscience/neuroplasticity": [
        "neuroplasticity", "neural pathways", "brain rewiring", "synaptic"
    ],
    "science_bridge/neuroscience/trauma_brain": [
        "trauma brain", "amygdala", "ptsd", "fight or flight", "nervous system"
    ],
    "science_bridge/consciousness_studies/academic_papers": [
        "academia", "journal", "study", "research", "paper", "abstract"
    ],
    "science_bridge/epigenetics": [
        "epigenetic", "gene expression", "dna methylation", "histone"
    ],
    "healing_modalities/therapy_types/cbt": [
        "cbt", "cognitive behavioral", "cognitive therapy", "beck"
    ],
    "healing_modalities/therapy_types/dbt": [
        "dbt", "dialectical behavior", "linehan"
    ],
    "healing_modalities/therapy_types/emdr": [
        "emdr", "eye movement", "bilateral stimulation"
    ],
    "healing_modalities/therapy_types/somatic": [
        "somatic", "body work", "somatic experiencing", "levine"
    ],
    "healing_modalities/trauma_work/childhood_patterns": [
        "childhood trauma", "inner child", "aces", "adverse childhood"
    ],
    "healing_modalities/trauma_work/attachment_theory": [
        "attachment theory", "attachment style", "attachment patterns", "bowlby", "anxious attachment", "avoidant attachment"
    ],
    "healing_modalities/trauma_work/polyvagal_theory": [
        "polyvagal", "vagus nerve", "porges", "ventral vagal"
    ],
    "healing_modalities/energy_healing/reiki": [
        "reiki", "usui", "energy healing"
    ],
    "healing_modalities/energy_healing/breathwork": [
        "breathwork", "pranayama", "wim hof", "holotropic"
    ],
}


def analyze_filename(filename: str) -> List[Tuple[str, float]]:
    """
    Analyze filename and return scored collection matches
    Returns: List of (collection_path, score) sorted by score
    """
    filename_lower = filename.lower()
    matches = []

    for collection, keywords in COLLECTIONS.items():
        score = 0.0
        for keyword in keywords:
            if keyword in filename_lower:
                # Exact match scores higher
                if keyword == filename_lower.replace(".pdf", "").replace(".docx", "").replace("-", " ").replace("_", " "):
                    score += 10.0
                # Word boundary match
                elif re.search(r'\b' + re.escape(keyword) + r'\b', filename_lower):
                    score += 5.0
                # Partial match (only allow for keywords longer than 4 characters to avoid false matches on "na" or "aa")
                else:
                    if len(keyword) > 4:
                        score += 2.0

        if score >= 5.0:
            matches.append((collection, score))

    # Sort by score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def scan_directory(directory: str, extensions: List[str] = [".pdf", ".docx"]) -> List[Path]:
    """Find all PDFs and DOCX files in directory and subdirectories"""
    files = []
    for ext in extensions:
        files.extend(Path(directory).rglob(f"*{ext}"))
    return files


def main():
    # Configuration
    base_dir = Path(__file__).parent
    library_dir = base_dir / "library"
    inbox_dir = library_dir / "_inbox"

    # Source directories to scan
    source_dirs = [
        "/Users/carriehuff/Documents/_ORGANIZED",
        "/Users/carriehuff/Downloads/_ORGANIZED",
    ]

    print("=" * 80)
    print("CONSCIOUSNESS RAG - DOCUMENT LIBRARY ORGANIZER")
    print("=" * 80)
    print()

    # Check if library exists
    if not library_dir.exists():
        print(f"❌ Error: Library directory not found at {library_dir}")
        print("   Run from the consciousness-rag folder or create the library first.")
        return

    print(f"📂 Scanning source directories...")
    print()

    all_files = []
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            files = scan_directory(source_dir)
            all_files.extend(files)
            print(f"   Found {len(files)} documents in {source_dir}")

    print()
    print(f"📊 Total documents found: {len(all_files)}")
    print()

    if len(all_files) == 0:
        print("No PDF or DOCX files found in source directories.")
        return

    # Analyze each file
    print("🔍 Analyzing filenames and suggesting placements...")
    print()

    suggestions = []

    for file_path in all_files:
        filename = file_path.name
        matches = analyze_filename(filename)

        if matches:
            suggestions.append({
                "file": file_path,
                "filename": filename,
                "matches": matches[:3]  # Top 3 matches
            })

    # Display suggestions
    print("=" * 80)
    print("SUGGESTED PLACEMENTS")
    print("=" * 80)
    print()

    if len(suggestions) == 0:
        print("❌ No automatic matches found.")
        print("   Place files manually in library/_inbox/ and organize later.")
        return

    for i, suggestion in enumerate(suggestions[:50], 1):  # Show first 50
        print(f"{i}. {suggestion['filename']}")
        print(f"   Source: {suggestion['file'].parent}")
        print(f"   Suggested collections:")
        for collection, score in suggestion['matches']:
            confidence = "HIGH" if score >= 10 else "MEDIUM" if score >= 5 else "LOW"
            print(f"      [{confidence}] {collection} (score: {score:.1f})")
        print()

    if len(suggestions) > 50:
        print(f"... and {len(suggestions) - 50} more documents")
        print()

    # Ask for action
    print("=" * 80)
    print("ACTIONS")
    print("=" * 80)
    print()
    print("Choose an action:")
    print("1. Copy ALL files to library/_inbox/ (you organize manually later)")
    print("2. Copy files to suggested folders (auto-organize by top match)")
    print("3. Generate organization script (review before running)")
    print("4. Exit (no changes)")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        print()
        print("Copying files to inbox...")
        inbox_dir.mkdir(parents=True, exist_ok=True)

        for suggestion in suggestions:
            src = suggestion['file']
            dst = inbox_dir / suggestion['filename']

            # Handle duplicates
            if dst.exists():
                base = dst.stem
                ext = dst.suffix
                counter = 1
                while dst.exists():
                    dst = inbox_dir / f"{base}_{counter}{ext}"
                    counter += 1

            try:
                shutil.copy2(src, dst)
                print(f"   ✓ {suggestion['filename']}")
            except Exception as e:
                print(f"   ✗ {suggestion['filename']} - Error: {e}")

        print()
        print(f"✅ Done! {len(suggestions)} files copied to {inbox_dir}")
        print("   Organize them manually when ready.")

    elif choice == "2":
        print()
        print("Auto-organizing files into collections...")

        for suggestion in suggestions:
            if not suggestion['matches']:
                continue

            # Use top match
            collection, score = suggestion['matches'][0]
            collection_dir = library_dir / collection
            collection_dir.mkdir(parents=True, exist_ok=True)

            src = suggestion['file']
            dst = collection_dir / suggestion['filename']

            # Handle duplicates
            if dst.exists():
                base = dst.stem
                ext = dst.suffix
                counter = 1
                while dst.exists():
                    dst = collection_dir / f"{base}_{counter}{ext}"
                    counter += 1

            try:
                shutil.copy2(src, dst)
                print(f"   ✓ {suggestion['filename']} → {collection}")
            except Exception as e:
                print(f"   ✗ {suggestion['filename']} - Error: {e}")

        print()
        print(f"✅ Done! {len(suggestions)} files organized into collections.")

    elif choice == "3":
        script_path = base_dir / "organize_library_commands.sh"

        with open(script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Generated organization commands\n")
            f.write("# Review this file before running!\n\n")

            for suggestion in suggestions:
                if not suggestion['matches']:
                    continue

                collection, score = suggestion['matches'][0]
                collection_dir = library_dir / collection

                src = suggestion['file']
                dst = collection_dir / suggestion['filename']

                f.write(f'# {suggestion["filename"]} → {collection}\n')
                f.write(f'mkdir -p "{collection_dir}"\n')
                f.write(f'cp "{src}" "{dst}"\n\n')

        os.chmod(script_path, 0o755)

        print()
        print(f"✅ Script generated: {script_path}")
        print("   Review the file, then run: ./organize_library_commands.sh")

    else:
        print()
        print("Exiting without changes.")


if __name__ == "__main__":
    main()
