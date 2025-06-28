from typing import List
from data_models import SprintStatus, AnalysisResult, UserStory
from datetime import datetime, timedelta

class SprintStatusAnalyzer:
    @staticmethod
    def analyze(sprints: List[SprintStatus]) -> List[AnalysisResult]:
        results = []

        for i, sprint in enumerate(sprints):
            flags = []
            recommendations = []
            risk = "low"

            # Basic checks
            if sprint.completion < sprint.target * 0.6:
                flags.append(f"[{sprint.sprint_name}] Low progress: {sprint.completion}% vs target {sprint.target}%")
                recommendations.append("Investigate delays and reallocate resources")
                risk = "medium"

            if sprint.critical_bugs >= 3:
                flags.append(f"[{sprint.sprint_name}] {sprint.critical_bugs} critical bugs unresolved")
                recommendations.append("Prioritize fixing critical bugs")
                risk = "high"

            if sprint.velocity < sprint.planned_velocity * 0.5:
                flags.append(f"[{sprint.sprint_name}] Low velocity: {sprint.velocity} / {sprint.planned_velocity}")
                recommendations.append("Review capacity and scope creep")
                if risk != "high":
                    risk = "medium"

            # User Story Analysis
            unassigned = [us for us in sprint.user_stories if not us.assignee]
            stuck_stories = []
            overloaded_members = {}

            for us in sprint.user_stories:
                if us.status == "in progress":
                    try:
                        start_date = datetime.strptime(us.start_date, "%Y-%m-%d")
                        if start_date < datetime.today() - timedelta(days=5):
                            stuck_stories.append(us)
                    except Exception:
                        flags.append(f"[{sprint.sprint_name}] Invalid or missing start date in story {us.id}")
                        recommendations.append(f"Check start date of {us.id}")
                        risk = "medium"

                if us.assignee:
                    overloaded_members[us.assignee] = overloaded_members.get(us.assignee, 0) + 1

            if unassigned:
                flags.append(f"[{sprint.sprint_name}] {len(unassigned)} stories unassigned")
                recommendations.append("Assign all unclaimed stories")
                if risk != "high":
                    risk = "medium"

            if stuck_stories:
                stuck_ids = ', '.join(us.id for us in stuck_stories)
                flags.append(f"[{sprint.sprint_name}] Stuck stories: {stuck_ids}")
                recommendations.append("Follow up on long-running tasks")
                risk = "high"

            overloaded = [member for member, count in overloaded_members.items() if count > 3]
            if overloaded:
                flags.append(f"[{sprint.sprint_name}] Overloaded members: {', '.join(overloaded)}")
                recommendations.append("Balance workload across team")
                if risk != "high":
                    risk = "medium"

            # Compare with previous sprint if available
            if i > 0:
                prev = sprints[i - 1]
                if sprint.velocity < prev.velocity:
                    flags.append(f"[{sprint.sprint_name}] Velocity dropped vs {prev.sprint_name}")
                    recommendations.append("Investigate root cause of velocity drop")

            results.append(AnalysisResult(
                agent_type="sprint",
                member_id="team",
                risk=risk,
                flags=flags,
                recommendations=recommendations
            ))

        return results
