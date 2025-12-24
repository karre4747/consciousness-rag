"""
Evolve Consciousness Engine - CrewAI Task Definitions
Autonomous workflows for content ingestion, tagging, and deployment.

Key Workflows:
1. Content Ingestion - Process documents through 3-pass tagging → Pinecone
2. Quality Validation - Ensure tags meet standards
3. API Endpoint Creation - Build new endpoints
4. Deployment - Deploy to production

Updated: December 24, 2025
"""

from crewai import Task
from typing import Dict, Any, List
from agents.consciousness_agents import (
    create_architect_agent,
    create_data_engineer_agent,
    create_backend_engineer_agent,
    create_qa_specialist_agent,
    create_documentation_agent
)


# ============================================================================
# CONTENT INGESTION WORKFLOW
# ============================================================================

def create_ingestion_analyze_task(content: str, metadata: Dict[str, Any]) -> Task:
    """
    STEP 1: Architect analyzes content and creates ingestion plan.
    """
    return Task(
        description=f"""Analyze this content and create an ingestion plan:

Content preview: {content[:500]}...
Metadata: {metadata}

Determine:
1. Should we use all three tagging passes or skip some for cost/speed?
2. What's the optimal chunking strategy for this content?
3. Environment constraints (RAM, rate limits)
4. Expected completion time and cost

Provide a detailed plan for the Data Engineer.""",
        agent=create_architect_agent(),
        expected_output="Detailed ingestion plan with pass selections and strategy"
    )


def create_ingestion_tag_task(content: str, plan: str) -> Task:
    """
    STEP 2: Data Engineer executes three-pass tagging.
    """
    return Task(
        description=f"""Execute three-pass tagging based on this plan:

PLAN FROM ARCHITECT:
{plan}

CONTENT TO TAG:
{content}

Execute:
1. Pass 1: Keyword tagging (always run)
2. Pass 2: AI enhancement (if plan requires it)
3. Pass 3: Claude analysis (if plan requires it)

Chunk content at 1800 characters with 200-char overlap.
Return comprehensive tagging results for all chunks.""",
        agent=create_data_engineer_agent(),
        expected_output="Complete tagging results with all tags, chunks, and metadata"
    )


def create_ingestion_validate_task(tagging_results: Dict[str, Any]) -> Task:
    """
    STEP 3: QA Specialist validates tagging quality.
    """
    return Task(
        description=f"""Validate these tagging results:

{tagging_results}

Check:
1. All required passes completed
2. Minimum tag coverage (at least 3 categories detected)
3. No errors or missing data
4. Cross-tradition connections identified (if Pass 3 ran)

If quality gates fail, report specific issues.
If quality passes, approve for upload.""",
        agent=create_qa_specialist_agent(),
        expected_output="Quality report with pass/fail status and detailed findings"
    )


def create_ingestion_upload_task(validated_results: Dict[str, Any]) -> Task:
    """
    STEP 4: Data Engineer uploads to Pinecone.
    """
    return Task(
        description=f"""Upload validated content to Pinecone:

VALIDATED RESULTS:
{validated_results}

Execute:
1. Generate embeddings for all chunks
2. Prepare vectors with comprehensive metadata
3. Upload to Pinecone in batches
4. Verify upload success

Return upload confirmation with vector IDs.""",
        agent=create_data_engineer_agent(),
        expected_output="Upload confirmation with vector count and IDs"
    )


# ============================================================================
# AUTONOMOUS INGESTION WORKFLOW (Complete Pipeline)
# ============================================================================

def create_autonomous_ingestion_workflow(
    documents: List[Dict[str, Any]],
    use_all_passes: bool = True
) -> List[Task]:
    """
    Create complete autonomous ingestion workflow.
    
    Args:
        documents: List of {content: str, metadata: dict}
        use_all_passes: Whether to run all 3 tagging passes
        
    Returns:
        List of tasks that will execute sequentially
    """
    tasks = []
    
    for i, doc in enumerate(documents):
        content = doc["content"]
        metadata = doc.get("metadata", {})
        
        # Task 1: Analyze
        tasks.append(Task(
            description=f"""Document {i+1}/{len(documents)}: Analyze and plan ingestion

Content: {content[:500]}...
Metadata: {metadata}

Create ingestion strategy considering:
- Environment resources (check RAM availability)
- Whether to use all 3 passes or optimize for speed/cost
- Chunking strategy
- Rate limiting needs""",
            agent=create_architect_agent(),
            expected_output="Ingestion strategy and pass selection"
        ))
        
        # Task 2: Execute tagging
        tasks.append(Task(
            description=f"""Document {i+1}/{len(documents)}: Execute three-pass tagging

Follow the Architect's plan.
Run appropriate passes (1, 2, 3) based on strategy.
Chunk at 1800 chars with 200 overlap.
Return comprehensive tags.""",
            agent=create_data_engineer_agent(),
            expected_output="Complete tagging results"
        ))
        
        # Task 3: Validate
        tasks.append(Task(
            description=f"""Document {i+1}/{len(documents)}: Validate quality

Check tagging completeness and accuracy.
Ensure minimum standards met.
Report any quality issues.""",
            agent=create_qa_specialist_agent(),
            expected_output="Quality validation report"
        ))
        
        # Task 4: Upload
        tasks.append(Task(
            description=f"""Document {i+1}/{len(documents)}: Upload to Pinecone

Generate embeddings, prepare vectors, upload.
Confirm success.""",
            agent=create_data_engineer_agent(),
            expected_output="Upload confirmation"
        ))
    
    return tasks


# ============================================================================
# API ENDPOINT CREATION WORKFLOW
# ============================================================================

def create_endpoint_design_task(endpoint_spec: Dict[str, Any]) -> Task:
    """Create task for designing new API endpoint."""
    return Task(
        description=f"""Design new API endpoint:

SPECIFICATION:
{endpoint_spec}

Create:
1. FastAPI route definition
2. Request/response models
3. Error handling
4. Rate limiting strategy
5. Documentation""",
        agent=create_architect_agent(),
        expected_output="Complete endpoint design specification"
    )


def create_endpoint_implement_task(design_spec: str) -> Task:
    """Create task for implementing the endpoint."""
    return Task(
        description=f"""Implement this API endpoint:

DESIGN:
{design_spec}

Write:
1. Clean, production-ready FastAPI code
2. Proper error handling
3. Request validation
4. Response formatting

Code should be ready to merge into main.py.""",
        agent=create_backend_engineer_agent(),
        expected_output="Production-ready endpoint code"
    )


def create_endpoint_test_task(implementation: str) -> Task:
    """Create task for testing the new endpoint."""
    return Task(
        description=f"""Test this endpoint implementation:

CODE:
{implementation}

Test:
1. Valid requests succeed
2. Invalid requests fail gracefully
3. Response format is correct
4. Performance is acceptable (< 5 seconds)
5. Error messages are helpful

Report any issues found.""",
        agent=create_qa_specialist_agent(),
        expected_output="Test results with pass/fail status"
    )


# ============================================================================
# QUALITY LOOP TASK
# ============================================================================

def create_quality_loop_task(
    previous_results: Dict[str, Any],
    max_iterations: int = 3
) -> Task:
    """
    Create self-healing quality loop task.
    If quality fails, iterate up to max_iterations to fix.
    """
    return Task(
        description=f"""Quality loop iteration:

PREVIOUS RESULTS:
{previous_results}

If quality failed:
1. Analyze what went wrong
2. Adjust strategy (different model, different chunking, etc.)
3. Re-run the failed step
4. Validate again

Continue until quality passes or max iterations ({max_iterations}) reached.

If max iterations reached without success, escalate to human review.""",
        agent=create_architect_agent(),
        expected_output="Quality loop outcome: PASS or ESCALATE"
    )


# ============================================================================
# DEPLOYMENT TASK
# ============================================================================

def create_deployment_task(environment: str = "droplet") -> Task:
    """Create task for deploying to production."""
    return Task(
        description=f"""Deploy Evolve Consciousness Engine to {environment}:

1. Prepare environment (install dependencies)
2. Configure environment variables
3. Set up systemd service
4. Configure nginx reverse proxy
5. Start service
6. Verify health endpoints
7. Run smoke tests

Ensure system is production-ready with proper error handling and monitoring.""",
        agent=create_backend_engineer_agent(),
        expected_output="Deployment confirmation with health check results"
    )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_simple_ingestion_tasks(content: str, metadata: Dict[str, Any]) -> List[Task]:
    """
    Simplified version - just the essential tasks for ingesting one document.
    """
    analyze = create_ingestion_analyze_task(content, metadata)
    tag = Task(
        description=f"Execute three-pass tagging on: {content[:200]}...",
        agent=create_data_engineer_agent(),
        expected_output="Tagging results"
    )
    validate = Task(
        description="Validate tagging quality",
        agent=create_qa_specialist_agent(),
        expected_output="Quality report"
    )
    upload = Task(
        description="Upload to Pinecone",
        agent=create_data_engineer_agent(),
        expected_output="Upload confirmation"
    )
    
    return [analyze, tag, validate, upload]
