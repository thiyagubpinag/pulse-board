
from typing import Any, Dict, List
from data_models import AnalysisResult


class CorrelationEngine:
    @staticmethod
    def correlate(analyses: List[AnalysisResult]) -> Dict[str, Any]:
        # Group analyses by member
        grouped = {}
        for analysis in analyses:
            if analysis.member_id not in grouped:
                grouped[analysis.member_id] = []
            grouped[analysis.member_id].append(analysis)
        
        overloaded, underutilized, burnout, critical, recommendations = [], [], [], [], []
        
        for member_id, member_analyses in grouped.items():
            # Check for specific conditions
            high_load = any(
                a.agent_type == "workload" and "High task load" in a.flags 
                for a in member_analyses
            )
            high_stress = any(
                a.agent_type == "wellbeing" and "High stress levels detected" in a.flags 
                for a in member_analyses
            )
            underused = any(
                a.agent_type == "workload" and "Underutilized capacity" in a.flags 
                for a in member_analyses
            )
            
            # Categorize members and generate recommendations
            if high_load and high_stress:
                overloaded.append(member_id)
                burnout.append(member_id)
                critical.append(f"{member_id}: High workload + stress")
                recommendations.append(f"URGENT: Redistribute {member_id}'s workload")
            elif high_load:
                overloaded.append(member_id)
            elif underused:
                underutilized.append(member_id)
            
            if high_stress and not high_load:
                burnout.append(member_id)
                recommendations.append(f"Support {member_id} with 1:1 check-in")
        
        return {
            "overloaded": overloaded,
            "underutilized": underutilized,
            "burnout": burnout,
            "critical": critical,
            "recommendations": recommendations
        }
