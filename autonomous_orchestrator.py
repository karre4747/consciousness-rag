"""
Evolve Consciousness Engine - Autonomous Orchestration
Main entry point for running autonomous agent workflows.

Usage Examples:
    # Process a single document autonomously
    python autonomous_orchestrator.py --mode ingest --file "path/to/doc.txt"
    
    # Process multiple documents in batch
    python autonomous_orchestrator.py --mode batch --folder "path/to/docs/"
    
    # Create a new API endpoint
    python autonomous_orchestrator.py --mode endpoint --spec endpoint_spec.json
    
    # Deploy to production
    python autonomous_orchestrator.py --mode deploy --environment droplet

Updated: December 24, 2025
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from crewai import Crew, Process
from dotenv import load_dotenv

from agents.consciousness_agents import create_consciousness_rag_crew, get_crew_for_task
from tasks.ingestion_tasks import (
    create_autonomous_ingestion_workflow,
    create_deployment_task,
    create_simple_ingestion_tasks
)

load_dotenv()


class AutonomousOrchestrator:
    """
    Main orchestrator for autonomous RAG operations.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.crew = create_consciousness_rag_crew()
    
    
    def ingest_single_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        use_all_passes: bool = True
    ) -> Dict[str, Any]:
        """
        Autonomously ingest a single document through complete pipeline.
        
        Args:
            content: Document text
            metadata: Document metadata (title, source, etc.)
            use_all_passes: Run all 3 tagging passes (default True)
            
        Returns:
            Results from the autonomous workflow
        """
        print(f"\n{'='*80}")
        print(f"AUTONOMOUS INGESTION: {metadata.get('title', 'Untitled')}")
        print(f"{'='*80}\n")
        
        # Create workflow tasks
        tasks = create_autonomous_ingestion_workflow(
            documents=[{"content": content, "metadata": metadata}],
            use_all_passes=use_all_passes
        )
        
        # Execute with crew
        self.crew.tasks = tasks
        result = self.crew.kickoff()
        
        if self.verbose:
            print(f"\n{'='*80}")
            print("INGESTION COMPLETE")
            print(f"{'='*80}\n")
            print(result)
        
        return result
    
    
    def ingest_batch(
        self,
        documents: List[Dict[str, Any]],
        use_all_passes: bool = True,
        max_concurrent: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Autonomously ingest multiple documents.
        
        Args:
            documents: List of {content: str, metadata: dict}
            use_all_passes: Run all 3 passes for each doc
            max_concurrent: Max docs to process concurrently (default 1 for safety)
            
        Returns:
            List of results for each document
        """
        print(f"\n{'='*80}")
        print(f"AUTONOMOUS BATCH INGESTION: {len(documents)} documents")
        print(f"{'='*80}\n")
        
        results = []
        
        # Process documents (for now, sequentially - could parallelize later)
        for i, doc in enumerate(documents):
            print(f"\n--- Document {i+1}/{len(documents)} ---")
            result = self.ingest_single_document(
                content=doc["content"],
                metadata=doc.get("metadata", {}),
                use_all_passes=use_all_passes
            )
            results.append(result)
        
        print(f"\n{'='*80}")
        print(f"BATCH COMPLETE: {len(results)} documents processed")
        print(f"{'='*80}\n")
        
        return results
    
    
    def create_api_endpoint(self, spec: Dict[str, Any]) -> str:
        """
        Autonomously design, implement, and test a new API endpoint.
        
        Args:
            spec: Endpoint specification {name, method, description, params}
            
        Returns:
            Production-ready endpoint code
        """
        from tasks.ingestion_tasks import (
            create_endpoint_design_task,
            create_endpoint_implement_task,
            create_endpoint_test_task
        )
        
        print(f"\n{'='*80}")
        print(f"AUTONOMOUS ENDPOINT CREATION: {spec.get('name', 'Unnamed')}")
        print(f"{'='*80}\n")
        
        # Create endpoint workflow
        tasks = [
            create_endpoint_design_task(spec),
            create_endpoint_implement_task(""),  # Will receive design from previous task
            create_endpoint_test_task("")  # Will receive implementation from previous
        ]
        
        self.crew.tasks = tasks
        result = self.crew.kickoff()
        
        if self.verbose:
            print(f"\n{'='*80}")
            print("ENDPOINT CREATION COMPLETE")
            print(f"{'='*80}\n")
            print(result)
        
        return result
    
    
    def deploy_to_production(self, environment: str = "droplet") -> Dict[str, Any]:
        """
        Autonomously deploy the system to production.
        
        Args:
            environment: Target environment (droplet, mac, etc.)
            
        Returns:
            Deployment status and health check results
        """
        print(f"\n{'='*80}")
        print(f"AUTONOMOUS DEPLOYMENT: {environment}")
        print(f"{'='*80}\n")
        
        deployment_task = create_deployment_task(environment)
        self.crew.tasks = [deployment_task]
        result = self.crew.kickoff()
        
        if self.verbose:
            print(f"\n{'='*80}")
            print("DEPLOYMENT COMPLETE")
            print(f"{'='*80}\n")
            print(result)
        
        return result


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Evolve Consciousness Engine - Autonomous Orchestration"
    )
    
    parser.add_argument(
        "--mode",
        choices=["ingest", "batch", "endpoint", "deploy"],
        required=True,
        help="Operation mode"
    )
    
    parser.add_argument("--file", help="Path to single document (for ingest mode)")
    parser.add_argument("--folder", help="Path to folder of documents (for batch mode)")
    parser.add_argument("--spec", help="Path to endpoint spec JSON (for endpoint mode)")
    parser.add_argument("--environment", default="droplet", help="Deployment environment")
    parser.add_argument("--skip-pass-2", action="store_true", help="Skip AI enhancement pass")
    parser.add_argument("--skip-pass-3", action="store_true", help="Skip Claude analysis pass")
    parser.add_argument("--verbose", action="store_true", default=True, help="Verbose output")
    
    args = parser.parse_args()
    
    orchestrator = AutonomousOrchestrator(verbose=args.verbose)
    
    # Execute based on mode
    if args.mode == "ingest":
        if not args.file:
            print("Error: --file required for ingest mode")
            return
        
        # Read file
        with open(args.file, 'r') as f:
            content = f.read()
        
        # Create metadata from filename
        metadata = {
            "title": Path(args.file).stem,
            "source": args.file,
            "type": "document"
        }
        
        # Ingest
        result = orchestrator.ingest_single_document(
            content=content,
            metadata=metadata,
            use_all_passes=not (args.skip_pass_2 and args.skip_pass_3)
        )
        
        print("\nResult:", result)
    
    elif args.mode == "batch":
        if not args.folder:
            print("Error: --folder required for batch mode")
            return
        
        # Read all text files from folder
        folder_path = Path(args.folder)
        documents = []
        
        for file_path in folder_path.glob("*.txt"):
            with open(file_path, 'r') as f:
                content = f.read()
            
            documents.append({
                "content": content,
                "metadata": {
                    "title": file_path.stem,
                    "source": str(file_path),
                    "type": "document"
                }
            })
        
        print(f"Found {len(documents)} documents")
        
        # Ingest batch
        results = orchestrator.ingest_batch(
            documents=documents,
            use_all_passes=not (args.skip_pass_2 and args.skip_pass_3)
        )
        
        print(f"\nProcessed {len(results)} documents")
    
    elif args.mode == "endpoint":
        if not args.spec:
            print("Error: --spec required for endpoint mode")
            return
        
        with open(args.spec, 'r') as f:
            spec = json.load(f)
        
        result = orchestrator.create_api_endpoint(spec)
        print("\nResult:", result)
    
    elif args.mode == "deploy":
        result = orchestrator.deploy_to_production(args.environment)
        print("\nResult:", result)


# ============================================================================
# PROGRAMMATIC USAGE EXAMPLES
# ============================================================================

def example_autonomous_ingestion():
    """Example: Process a document completely autonomously"""
    orchestrator = AutonomousOrchestrator()
    
    content = """
    The First Step of recovery states: "We admitted we were powerless over alcohol—
    that our lives had become unmanageable." This is parallel to the Buddhist concept 
    of dukkha (suffering) and the recognition that grasping creates suffering. 
    In Kabbalah, this corresponds to acknowledging the need to ascend from Malkuth 
    (material world) toward higher consciousness. The quantum physics parallel is the 
    observer effect - you cannot change what you don't acknowledge observing.
    """
    
    metadata = {
        "title": "Step 1 and Cross-Tradition Parallels",
        "source": "example",
        "program_level": "intermediate"
    }
    
    result = orchestrator.ingest_single_document(content, metadata)
    return result


def example_batch_processing():
    """Example: Process multiple documents autonomously"""
    orchestrator = AutonomousOrchestrator()
    
    documents = [
        {
            "content": "Content about chakras and energy...",
            "metadata": {"title": "Chakra System", "source": "manual"}
        },
        {
            "content": "Content about 12 Steps and mysticism...",
            "metadata": {"title": "12 Steps as Ascension", "source": "manual"}
        }
    ]
    
    results = orchestrator.ingest_batch(documents)
    return results


if __name__ == "__main__":
    main()
