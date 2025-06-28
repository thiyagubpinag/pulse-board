from typing import List
from data_models import AnalysisResult, WorkloadData


class WorkloadAnalyzer:
    @staticmethod
    def analyze(workload_data: List[WorkloadData]) -> List[AnalysisResult]:
        results = []
        for data in workload_data:
            flags, recommendations = [], []
            risk = "low"
            
            # High task load check
            if data.active_tasks > 10:
                flags.append("High task load")
                recommendations.append("Redistribute tasks")
                risk = "high"
            
            # Overtime check
            if data.overtime_hours > 10:
                flags.append("Excessive overtime")
                recommendations.append("Reduce workload")
                risk = "high"
            
            # SLA breach check
            if data.sla_breaches > 1:
                flags.append("SLA violations detected")
                recommendations.append("Review deadlines")
                if risk != "high":
                    risk = "medium"
            
            # Underutilization check
            if data.active_tasks < 4 and data.overtime_hours < 3:
                flags.append("Underutilized capacity")
                recommendations.append("Assign more tasks")
            
            results.append(AnalysisResult("workload", data.member_id, risk, flags, recommendations))
        
        return results
