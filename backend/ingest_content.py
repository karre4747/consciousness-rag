#!/usr/bin/env python3
"""
Evolve Consciousness Engine - Content Ingestion Script
Batch upload documents from your content library to the vector database
"""

import requests
import json
import os
import time
from pathlib import Path
from typing import List, Dict
import argparse


class ContentIngester:
    """Handles batch ingestion of content into Evolve"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
    
    def ingest_file(self, file_path: Path, program_level: str = "beginner", use_ai_tagging: bool = False) -> bool:
        """Ingest a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare request
            data = {
                "text": content,
                "title": file_path.stem,  # Filename without extension
                "source": str(file_path),
                "program_level": program_level,
                "use_ai_tagging": use_ai_tagging
            }
            
            # Upload
            print(f"  Uploading: {file_path.name}...", end=" ")
            response = requests.post(f"{self.api_url}/upload", json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ ({result['chunks_created']} chunks)")
                self.stats["success"] += 1
                return True
            else:
                print(f"✗ Error: {response.status_code}")
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "file": str(file_path),
                    "error": response.text
                })
                return False
                
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
            self.stats["failed"] += 1
            self.stats["errors"].append({
                "file": str(file_path),
                "error": str(e)
            })
            return False
    
    def ingest_directory(self, directory: Path, program_level: str = "beginner", 
                        use_ai_tagging: bool = False, pattern: str = "*.md"):
        """Ingest all files in a directory"""
        files = list(directory.glob(pattern))
        self.stats["total"] = len(files)
        
        print(f"\n📚 Found {len(files)} files to ingest")
        print(f"📁 Directory: {directory}")
        print(f"🎯 Program Level: {program_level}")
        print(f"🤖 AI Tagging: {'Enabled' if use_ai_tagging else 'Disabled'}\n")
        
        for i, file_path in enumerate(files, 1):
            print(f"[{i}/{len(files)}]", end=" ")
            self.ingest_file(file_path, program_level, use_ai_tagging)
            time.sleep(0.5)  # Rate limiting
        
        self.print_summary()
    
    def print_summary(self):
        """Print ingestion summary"""
        print("\n" + "="*60)
        print("  INGESTION SUMMARY")
        print("="*60)
        print(f"Total files:     {self.stats['total']}")
        print(f"✓ Successful:    {self.stats['success']}")
        print(f"✗ Failed:        {self.stats['failed']}")
        
        if self.stats["errors"]:
            print("\n❌ Errors:")
            for error in self.stats["errors"]:
                print(f"  - {error['file']}: {error['error']}")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Ingest content into Evolve Consciousness Engine")
    parser.add_argument("directory", type=str, help="Directory containing content files")
    parser.add_argument("--level", type=str, default="beginner", 
                       choices=["beginner", "intermediate", "advanced"],
                       help="Program level for the content")
    parser.add_argument("--pattern", type=str, default="*.md",
                       help="File pattern to match (default: *.md)")
    parser.add_argument("--ai-tagging", action="store_true",
                       help="Enable AI-enhanced tagging (slower but more accurate)")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000",
                       help="API URL (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ Error: Directory not found: {directory}")
        return
    
    # Check API connection
    try:
        response = requests.get(f"{args.api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Error: API is not healthy")
            return
        print(f"✓ Connected to Evolve API at {args.api_url}\n")
    except Exception as e:
        print(f"❌ Error: Cannot connect to API at {args.api_url}")
        print(f"   Make sure the server is running: python main.py")
        return
    
    # Run ingestion
    ingester = ContentIngester(args.api_url)
    ingester.ingest_directory(
        directory=directory,
        program_level=args.level,
        use_ai_tagging=args.ai_tagging,
        pattern=args.pattern
    )


if __name__ == "__main__":
    main()
