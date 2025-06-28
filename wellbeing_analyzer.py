
from typing import List
from data_models import AnalysisResult, DailyUpdate


class WellbeingAnalyzer:
    @staticmethod
    def analyze(daily_updates: List[DailyUpdate]) -> List[AnalysisResult]:
        results = []
        for update in daily_updates:
            flags, recommendations = [], []
            risk = "low"
            
            # Mood check
            if update.mood in ["stressed", "burnout"]:
                flags.append("High stress levels detected")
                recommendations.append("Schedule 1:1 and reduce load")
                risk = "high"
            
            # Blockers check
            if len(update.blockers) > 2:
                flags.append("Multiple blockers")
                recommendations.append("Resolve blockers")
                if risk != "high":
                    risk = "medium"
            
            # Working hours check
            if update.working_hours > 9:
                flags.append("Extended working hours")
                recommendations.append("Monitor hours")
                if risk != "high":
                    risk = "medium"
            
            # Sentiment analysis
            negative_keywords = ["overwhelmed", "tired", "stressed", "frustrated"]
            if any(keyword in update.comments.lower() for keyword in negative_keywords):
                flags.append("Negative sentiment in feedback")
                recommendations.append("Immediate support required")
                risk = "high"
            
            results.append(AnalysisResult("wellbeing", update.member_id, risk, flags, recommendations))
        
        return results

