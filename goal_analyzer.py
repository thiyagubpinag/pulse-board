
from typing import List
from data_models import AnalysisResult, GoalData


class GoalAnalyzer:
    @staticmethod
    def analyze(goal_data: List[GoalData]) -> List[AnalysisResult]:
        results = []
        for data in goal_data:
            flags, recommendations = [], []
            risk = "low"
            completion_rate = data.completed_goals / data.sprint_goals
            
            # Low completion rate
            if completion_rate < 0.5:
                flags.append("Low sprint completion rate")
                recommendations.append("Review sprint commitments")
                risk = "high"
            
            # Velocity behind expected
            if data.velocity < data.expected_completion:
                flags.append("Behind velocity")
                recommendations.append("Assess task complexity")
                if risk != "high":
                    risk = "medium"
            
            # Exceeding goals
            if completion_rate > 0.9:
                flags.append("Exceeding goals")
                recommendations.append("Increase sprint capacity")
            
            results.append(AnalysisResult("goal", data.member_id, risk, flags, recommendations))
        
        return results

