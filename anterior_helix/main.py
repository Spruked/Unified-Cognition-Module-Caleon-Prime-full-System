from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from reflection_vault import ReflectionVault

app = FastAPI(title="Anterior Helix - Planning & Decision Making")

# Initialize reflection vault
reflection_vault = ReflectionVault("anterior_helix_reflection_vault.json", "anterior_helix")

class PlanningRequest(BaseModel):
    goal: str
    constraints: Dict[str, Any]
    available_resources: List[str]
    context: Dict[str, Any]
    emotion: Optional[Dict[str, float]] = None
    relationship: Optional[str] = None
    legacy_weight: str = "medium"

class DecisionOption(BaseModel):
    option_id: str
    description: str
    feasibility_score: float
    risk_score: float
    expected_outcome: str

class Plan:
    def __init__(self):
        self.decision_tree = {}
        self.learning_history = []

    def generate_options(self, request: PlanningRequest) -> List[DecisionOption]:
        """Generate decision options based on goal and constraints"""
        options = []

        # Basic planning logic
        if "time" in request.constraints:
            time_constraint = request.constraints["time"]
            if time_constraint < 5:
                options.append(DecisionOption(
                    option_id="quick_solution",
                    description="Implement immediate short-term solution",
                    feasibility_score=0.9,
                    risk_score=0.7,
                    expected_outcome="Fast resolution with potential long-term issues"
                ))

        if len(request.available_resources) > 3:
            options.append(DecisionOption(
                option_id="comprehensive_approach",
                description="Use all available resources for thorough solution",
                feasibility_score=0.6,
                risk_score=0.3,
                expected_outcome="Comprehensive solution with optimal results"
            ))

        # Default option
        options.append(DecisionOption(
            option_id="balanced_approach",
            description="Balanced approach considering all factors",
            feasibility_score=0.8,
            risk_score=0.5,
            expected_outcome="Reasonable solution balancing speed and quality"
        ))

        return options

    def evaluate_option(self, option: DecisionOption, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a decision option in context"""
        # Simple evaluation logic
        context_multiplier = 1.0
        if context.get("urgency") == "high":
            context_multiplier = 1.3

        adjusted_feasibility = min(1.0, option.feasibility_score * context_multiplier)
        adjusted_risk = option.risk_score / context_multiplier

        return {
            "option_id": option.option_id,
            "adjusted_feasibility": adjusted_feasibility,
            "adjusted_risk": adjusted_risk,
            "recommendation_score": (adjusted_feasibility * 0.7) + ((1 - adjusted_risk) * 0.3)
        }

planner = Plan()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Anterior Helix"}

@app.post("/plan")
async def create_plan(request: PlanningRequest):
    """Generate planning options for a given goal"""
    try:
        options = planner.generate_options(request)

        # Evaluate each option
        evaluated_options = []
        for option in options:
            evaluation = planner.evaluate_option(option, request.context)
            evaluated_options.append({
                "option": option.dict(),
                "evaluation": evaluation
            })

        # Sort by recommendation score
        evaluated_options.sort(key=lambda x: x["evaluation"]["recommendation_score"], reverse=True)

        return {
            "goal": request.goal,
            "options_count": len(options),
            "recommended_option": evaluated_options[0] if evaluated_options else None,
            "all_options": evaluated_options
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decide")
async def make_decision(request: PlanningRequest):
    """Make a final decision based on planning"""
    try:
        options = planner.generate_options(request)
        if not options:
            return {"decision": "no_viable_options", "reasoning": "No feasible options found"}

        # Select best option
        best_option = max(options, key=lambda x: x.feasibility_score * (1 - x.risk_score))

        # Store decision for learning
        planner.learning_history.append({
            "goal": request.goal,
            "decision": best_option.option_id,
            "timestamp": asyncio.get_event_loop().time()
        })

        # Log reflection in vault
        from datetime import datetime
        case_id = f"anterior_decision_{int(asyncio.get_event_loop().time() * 1000)}"
        
        emotional_context = "neutral"
        if request.emotion:
            dominant_emotion = max(request.emotion.keys(), key=lambda k: request.emotion[k])
            emotional_context = dominant_emotion

        ethical_dilemma = f"Decision dilemma for goal: {request.goal[:50]}..."
        initial_decision = f"Selected {best_option.option_id} with confidence {best_option.feasibility_score:.2f}"
        refined_reasoning = f"Final decision: {best_option.description}. Expected outcome: {best_option.expected_outcome}"
        lesson = f"Learned that {best_option.option_id} is optimal when feasibility is prioritized over risk for {request.goal[:30]}..."
        
        priority_tags = ["planning", "decision"]
        if best_option.feasibility_score < 0.7:
            priority_tags.append("uncertainty")
        if "time" in str(request.constraints).lower():
            priority_tags.append("urgency")

        reflection_vault.log_reflection(
            case_id=case_id,
            emotional_context=emotional_context,
            ethical_dilemma=ethical_dilemma,
            initial_decision=initial_decision,
            refined_reasoning=refined_reasoning,
            lesson=lesson,
            reflection_type="conditional",
            priority_tags=priority_tags,
            resolution_status="resolved"
        )

        return {
            "decision": best_option.option_id,
            "description": best_option.description,
            "confidence": best_option.feasibility_score,
            "expected_outcome": best_option.expected_outcome
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning_history")
async def get_learning_history(limit: int = 10):
    """Get recent decision-making history"""
    recent_history = planner.learning_history[-limit:]
    return {"history": recent_history}

@app.get("/vault/stats")
async def get_vault_stats():
    """Get reflection vault statistics"""
    return reflection_vault.get_vault_statistics()

@app.get("/vault/query")
async def query_vault(query_type: str = "unresolved", tags: str = None, limit: int = 10):
    """Query the reflection vault"""
    tag_list = tags.split(",") if tags else None
    return reflection_vault.query_vault(query_type, tag_list, limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)