from schemas.output_schema import AnalysisOutput
from agents.failure_prediction_agent import FailurePredictionAgent
from agents.architecture_agent import ArchitectureAgent
# from agents.incident_reviewer_agent import IncidentReviewerAgent # Future
from orchestration.state import PipelineState

# Singleton agents to avoid reloading models
_failure_agent = None
_architecture_agent = None
# _reviewer_agent = None

def get_agents():
    global _failure_agent, _architecture_agent
    if _failure_agent is None:
        _failure_agent = FailurePredictionAgent()
    if _architecture_agent is None:
        _architecture_agent = ArchitectureAgent()
    return _failure_agent, _architecture_agent

def run_pipeline(user_input: str, provider: str = "openrouter", model_id: str = "google/gemini-2.0-flash-exp:free") -> AnalysisOutput:
    """
    Main orchestration function.
    1. Failure Prediction Agent (Identifies risks)
    2. Architecture Agent (Proposes mitigations)
    3. Reviewer Agent (Validates) - TODO
    4. Return structured output
    """
    print(f"🚀 Starting Pipeline for: {user_input[:50]}...")
    print(f"🤖 AI Config: {provider} using {model_id}")
    
    # 1. Initialize State & Agents
    state = PipelineState()
    state.input = user_input
    fail_agent, arch_agent = get_agents()
    
    # Configure Agents dynamically
    fail_agent.provider = provider
    fail_agent.model_id = model_id
    
    # 2. Failure Prediction
    print("🕵️‍♂️ Phase 1: Failure Prediction...")
    failures = fail_agent.run(user_input)
    state.failures = failures
    
    # 3. Architecture Design
    print("🏗️ Phase 2: Architecture Design...")
    architecture = arch_agent.run(failures)
    state.architecture = architecture
    
    # 4. Review (Future)
    # state.review = review_agent.run(architecture)
    review_score = 8 # Placeholder
    review_comments = "Architecture addresses detected risks."

    # 5. Final Output Construction
    output = AnalysisOutput(
        input_summary=user_input[:100] + "...",
        detected_failures=failures,
        proposed_architecture=architecture,
        review_score=review_score,
        review_comments=review_comments
    )
    
    print("✅ Pipeline Complete.")
    return output
