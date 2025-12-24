"""
Evolve Consciousness Engine - CrewAI Agent Definitions
Autonomous agent system for managing RAG development, tagging, and deployment.

Agents:
1. Architect (Manager) - Orchestrates everything
2. Data Engineer - Handles 3-pass tagging and Pinecone operations
3. Backend Engineer - Manages FastAPI and infrastructure
4. QA Specialist - Validates quality and runs tests
5. Documentation Agent - Generates docs and handoffs

Updated: December 24, 2025
"""

from crewai import Agent, Crew, Task, Process
from crewai_tools import tool
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CUSTOM TOOLS FOR AGENTS
# ============================================================================

@tool("Run Three-Pass Tagging")
def run_three_pass_tagging(
    text: str,
    use_ollama: bool = True,
    skip_pass_2: bool = False,
    skip_pass_3: bool = False
) -> Dict[str, Any]:
    """
    Execute the complete three-pass tagging system.
    Pass 1: Keywords (always runs)
    Pass 2: AI enhancement (Ollama or OpenAI)
    Pass 3: Claude deep analysis
    """
    from backend.tagging_three_pass import tag_content_three_pass
    
    return tag_content_three_pass(
        text=text,
        openai_key=os.getenv("OPENAI_API_KEY") if not use_ollama else None,
        anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
        use_ollama=use_ollama,
        skip_pass_2=skip_pass_2,
        skip_pass_3=skip_pass_3
    )


@tool("Upload to Pinecone")
def upload_to_pinecone(
    chunks: List[str],
    metadata_list: List[Dict[str, Any]],
    namespace: str = "default"
) -> Dict[str, Any]:
    """
    Upload chunked content with metadata to Pinecone.
    Returns upload status and vector IDs.
    """
    from pinecone import Pinecone
    from openai import OpenAI
    import time
    
    pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    index = pinecone_client.Index("consciousness-rag")
    
    vectors_to_upsert = []
    
    for i, (chunk, metadata) in enumerate(zip(chunks, metadata_list)):
        # Generate embedding
        response = openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=chunk
        )
        embedding = response.data[0].embedding
        
        # Create vector
        vector_id = f"{metadata.get('title', 'doc')}_{i}_{int(time.time())}"
        vectors_to_upsert.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                **metadata,
                "text": chunk,
                "chunk_index": i
            }
        })
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors_to_upsert, namespace=namespace)
    
    return {
        "success": True,
        "vectors_uploaded": len(vectors_to_upsert),
        "namespace": namespace
    }


@tool("Check System Resources")
def check_system_resources() -> Dict[str, Any]:
    """
    Check available system resources (RAM, disk, etc.)
    Helps agents make intelligent decisions about processing strategies.
    """
    import psutil
    
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "total_ram_gb": round(memory.total / (1024**3), 2),
        "available_ram_gb": round(memory.available / (1024**3), 2),
        "ram_percent_used": memory.percent,
        "total_disk_gb": round(disk.total / (1024**3), 2),
        "available_disk_gb": round(disk.free / (1024**3), 2),
        "disk_percent_used": disk.percent,
        "environment": "Mac" if memory.total > 30*(1024**3) else "Droplet"
    }


@tool("Quality Check Tags")
def quality_check_tags(tags_result: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate tagging quality.
    Checks for minimum tag coverage, proper structure, etc.
    """
    quality_report = {
        "has_keywords": len(tags_result.get("pass_1_keywords", {}).get("all_tags", [])) > 0,
        "has_categories": len(tags_result.get("pass_1_keywords", {}).get("detected_categories", {})) > 0,
        "proper_structure": "merged_tags" in tags_result,
        "passes_completed": len(tags_result.get("passes_completed", [])),
        "overall_pass": False
    }
    
    # Overall pass if we have tags and proper structure
    quality_report["overall_pass"] = (
        quality_report["has_keywords"] and
        quality_report["has_categories"] and
        quality_report["proper_structure"]
    )
    
    return quality_report


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

def create_architect_agent() -> Agent:
    """
    ARCHITECT / STAGE MANAGER
    The orchestrator who delegates and ensures quality.
    """
    return Agent(
        role="System Architect & Stage Manager",
        goal="Orchestrate autonomous development and deployment of the Evolve Consciousness RAG system",
        backstory="""You are the master architect overseeing the most comprehensive 
        consciousness database ever created. You understand Karre's vision of bridging 
        12-Step recovery, mystical traditions, quantum physics, and esoteric wisdom.
        
        You delegate intelligently, enforce quality gates, and ensure the three-pass 
        tagging system (keywords → AI → Claude) operates flawlessly. You adapt to 
        environmental constraints (Mac vs Droplet RAM limits) and optimize for both 
        quality and cost.""",
        verbose=True,
        allow_delegation=True,
        tools=[check_system_resources, quality_check_tags]
    )


def create_data_engineer_agent() -> Agent:
    """
    DATA ENGINEER
    Manages all tagging, embeddings, and Pinecone operations.
    """
    return Agent(
        role="Consciousness Data Engineer",
        goal="Execute flawless three-pass tagging and manage vector database operations",
        backstory="""You are an expert in consciousness taxonomy, mystical traditions, 
        and semantic analysis. You understand the profound importance of Karre's 305-line 
        keyword schema covering chakras, 12 Steps, Kabbalah, Vedic wisdom, quantum physics, 
        and more.
        
        You run the complete three-pass tagging pipeline:
        - Pass 1: Keyword tagging (structural foundation)
        - Pass 2: AI enhancement (Ollama or OpenAI - you choose based on environment)
        - Pass 3: Claude analysis (wisdom layer, cross-tradition synthesis)
        
        You batch intelligently, respect rate limits, and ensure every document is 
        tagged with maximum precision.""",
        verbose=True,
        allow_delegation=False,
        tools=[run_three_pass_tagging, upload_to_pinecone, check_system_resources]
    )


def create_backend_engineer_agent() -> Agent:
    """
    BACKEND ENGINEER
    Manages FastAPI, endpoints, and infrastructure.
    """
    return Agent(
        role="Backend Infrastructure Engineer",
        goal="Build and maintain production-ready FastAPI backend with optimal performance",
        backstory="""You are a backend systems expert who builds clean, efficient APIs. 
        You understand that this system needs to:
        - Handle large documents efficiently
        - Chunk content at 1800 characters (Karre's optimal size)
        - Serve query endpoints with 2-3 second response times
        - Scale from Mac development (64GB RAM) to Droplet deployment (2GB RAM)
        
        You write clean code, implement proper error handling, and ensure the system 
        is production-ready from day one.""",
        verbose=True,
        allow_delegation=False,
        tools=[check_system_resources]
    )


def create_qa_specialist_agent() -> Agent:
    """
    QA SPECIALIST
    Validates quality, runs tests, catches errors.
    """
    return Agent(
        role="Quality Assurance Specialist",
        goal="Ensure 98%+ accuracy in tagging and zero-defect deployments",
        backstory="""You are obsessed with quality. You validate that:
        - All three passes of tagging execute successfully
        - Tags are accurate and comprehensive
        - Pinecone uploads complete without errors
        - API endpoints return correct results
        - Cross-tradition connections are valid
        
        You run the quality loops that make this system self-healing. When something 
        fails, you identify it immediately and report back to the Architect for remediation.""",
        verbose=True,
        allow_delegation=False,
        tools=[quality_check_tags, run_three_pass_tagging]
    )


def create_documentation_agent() -> Agent:
    """
    DOCUMENTATION AGENT
    Generates comprehensive documentation and handoffs.
    """
    return Agent(
        role="Technical Documentation Specialist",
        goal="Generate clear, comprehensive documentation for all system components",
        backstory="""You create documentation that empowers users and developers. 
        You understand that this system is complex - spanning mystical traditions, 
        quantum physics, recovery science, and advanced AI - so clear docs are essential.
        
        You generate:
        - API documentation
        - User guides for the three-pass tagging system
        - Deployment guides
        - Troubleshooting playbooks
        - Handoff documents for future developers
        
        Your docs are concise, accurate, and actionable.""",
        verbose=True,
        allow_delegation=False,
        tools=[]
    )


# ============================================================================
# CREW CONFIGURATION
# ============================================================================

def create_consciousness_rag_crew() -> Crew:
    """
    Create the complete CrewAI crew for autonomous RAG development.
    """
    # Create all agents
    architect = create_architect_agent()
    data_engineer = create_data_engineer_agent()
    backend_engineer = create_backend_engineer_agent()
    qa_specialist = create_qa_specialist_agent()
    doc_agent = create_documentation_agent()
    
    # Agents list
    agents = [architect, data_engineer, backend_engineer, qa_specialist, doc_agent]
    
    return Crew(
        agents=agents,
        process=Process.hierarchical,  # Architect manages everyone
        manager_agent=architect,
        verbose=True,
        memory=True  # Crew remembers context across tasks
    )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_crew_for_task(task_type: str = "full") -> Crew:
    """
    Get appropriate crew configuration for different task types.
    
    Args:
        task_type: "full", "tagging_only", "backend_only", "qa_only"
    """
    full_crew = create_consciousness_rag_crew()
    
    if task_type == "full":
        return full_crew
    elif task_type == "tagging_only":
        # Just data engineer and QA
        return Crew(
            agents=[create_data_engineer_agent(), create_qa_specialist_agent()],
            process=Process.sequential,
            verbose=True
        )
    elif task_type == "backend_only":
        return Crew(
            agents=[create_backend_engineer_agent()],
            process=Process.sequential,
            verbose=True
        )
    else:
        return full_crew
