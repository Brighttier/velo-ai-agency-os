"""
LangGraph State Definitions
Defines the state structure for agent workflows
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from enum import Enum
import operator


class WorkflowPhase(str, Enum):
    """Current phase of the workflow"""
    PLANNING = "planning"
    BUILDING = "building"
    TESTING = "testing"
    ARTIFACT_GENERATION = "artifact_generation"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(TypedDict):
    """
    The state that flows through the LangGraph workflow
    This is shared across all agent nodes
    """
    # Project Information
    project_id: str
    project_name: str
    project_description: str

    # Current Workflow State
    phase: WorkflowPhase
    current_agent: Optional[str]
    iteration: int
    max_iterations: int

    # Task Information
    current_task: Optional[Dict[str, Any]]
    pending_tasks: List[Dict[str, Any]]
    completed_tasks: List[Dict[str, Any]]
    failed_tasks: List[Dict[str, Any]]

    # Generated Artifacts
    artifacts: Annotated[List[Dict[str, Any]], operator.add]  # Additive - accumulates
    prd: Optional[str]
    architecture_diagram: Optional[str]
    database_schema: Optional[str]

    # Testing & Validation
    test_results: List[Dict[str, Any]]
    validation_errors: List[str]
    passed_validation: bool

    # Agent Activity
    agent_activities: Annotated[List[Dict[str, Any]], operator.add]  # Additive

    # Context & Memory
    context: Dict[str, Any]  # Additional context for agents
    messages: List[Dict[str, str]]  # Conversation history

    # Error Handling
    errors: List[str]
    retry_count: int

    # Final Output
    output: Optional[Dict[str, Any]]


class PlanningState(TypedDict):
    """State specific to the Planning Phase workflow"""
    user_prompt: str
    generated_prd: Optional[str]
    task_breakdown: List[Dict[str, Any]]
    plane_project_id: Optional[str]
    plane_issues_created: List[str]
    status: str


class BuildQAState(TypedDict):
    """State specific to the Build & QA Loop workflow"""
    task: Dict[str, Any]
    code_generated: Optional[str]
    test_passed: bool
    validation_feedback: Optional[str]
    retry_count: int
    max_retries: int
    final_code: Optional[str]
    status: str


class ArtifactState(TypedDict):
    """State specific to the Artifact Generation workflow"""
    project_id: str
    prd_content: Optional[str]
    code_files: List[Dict[str, str]]

    # Parallel artifact generation
    architecture_diagram_generated: bool
    user_manual_generated: bool
    test_report_generated: bool
    deployment_guide_generated: bool

    # Generated content
    architecture_diagram: Optional[str]
    user_manual: Optional[str]
    test_report: Optional[str]
    deployment_guide: Optional[str]

    # Storage
    gcs_paths: Dict[str, str]
    status: str


def create_initial_state(
    project_id: str,
    project_name: str,
    project_description: str
) -> AgentState:
    """
    Create initial state for a new project workflow
    """
    return AgentState(
        project_id=project_id,
        project_name=project_name,
        project_description=project_description,
        phase=WorkflowPhase.PLANNING,
        current_agent=None,
        iteration=0,
        max_iterations=10,
        current_task=None,
        pending_tasks=[],
        completed_tasks=[],
        failed_tasks=[],
        artifacts=[],
        prd=None,
        architecture_diagram=None,
        database_schema=None,
        test_results=[],
        validation_errors=[],
        passed_validation=False,
        agent_activities=[],
        context={},
        messages=[],
        errors=[],
        retry_count=0,
        output=None,
    )


def update_phase(state: AgentState, new_phase: WorkflowPhase) -> AgentState:
    """Update the workflow phase"""
    state['phase'] = new_phase
    return state


def add_artifact(
    state: AgentState,
    agent_name: str,
    artifact_type: str,
    content: str,
    metadata: Dict[str, Any] = None
) -> AgentState:
    """Add an artifact to the state"""
    artifact = {
        'agent': agent_name,
        'type': artifact_type,
        'content': content,
        'metadata': metadata or {},
        'timestamp': None  # Will be set by backend
    }

    if 'artifacts' not in state:
        state['artifacts'] = []

    state['artifacts'].append(artifact)
    return state


def log_agent_activity(
    state: AgentState,
    agent_name: str,
    action: str,
    status: str,
    metadata: Dict[str, Any] = None
) -> AgentState:
    """Log agent activity"""
    activity = {
        'agent': agent_name,
        'action': action,
        'status': status,
        'metadata': metadata or {},
        'timestamp': None  # Will be set by backend
    }

    if 'agent_activities' not in state:
        state['agent_activities'] = []

    state['agent_activities'].append(activity)
    return state


def add_error(state: AgentState, error_message: str) -> AgentState:
    """Add an error to the state"""
    if 'errors' not in state:
        state['errors'] = []

    state['errors'].append(error_message)
    return state


def increment_retry(state: AgentState) -> AgentState:
    """Increment retry counter"""
    state['retry_count'] = state.get('retry_count', 0) + 1
    return state


def should_retry(state: AgentState, max_retries: int = 5) -> bool:
    """Check if we should retry the current operation"""
    return state.get('retry_count', 0) < max_retries


def is_workflow_complete(state: AgentState) -> bool:
    """Check if the workflow is complete"""
    return (
        state['phase'] == WorkflowPhase.COMPLETED or
        state['phase'] == WorkflowPhase.FAILED or
        state['iteration'] >= state['max_iterations']
    )
