from typing import List
from data_models import SprintStatus, AnalysisResult, UserStory
from datetime import datetime, timedelta

class SprintStatusAnalyzer:
    @staticmethod
    def analyze(sprint: SprintStatus) -> List[AnalysisResult]:
        flags = []
        recommendations = []
        risk = "low"

        # Completion vs. target check
        if sprint.completion < sprint.target * 0.6:
            flags.append(f"Low progress: {sprint.completion}% vs target {sprint.target}%")
            recommendations.append("Investigate delays and reallocate resources")
            risk = "medium"

        # Critical bugs check
        if sprint.critical_bugs >= 3:
            flags.append(f"{sprint.critical_bugs} critical bugs unresolved")
            recommendations.append("Prioritize fixing critical bugs")
            risk = "high"

        # Velocity health check
        if sprint.velocity < sprint.planned_velocity * 0.5:
            flags.append(f"Velocity is low: {sprint.velocity} / {sprint.planned_velocity}")
            recommendations.append("Review capacity and scope creep")
            if risk != "high":
                risk = "medium"

        # User Story Analysis
        unassigned = [us for us in sprint.user_stories if not us.assignee]
        stuck_stories = []
        overloaded_members = {}

        for us in sprint.user_stories:
            # Detect stuck stories
            if us.status == "in progress":
                try:
                    start_date = datetime.strptime(us.start_date, "%Y-%m-%d")
                    if start_date < datetime.today() - timedelta(days=5):
                        stuck_stories.append(us)
                except Exception:
                    flags.append(f"Invalid or missing start date in story {us.id}")
                    recommendations.append(f"Check start date of {us.id}")
                    risk = "medium"

            # Count number of stories per member
            if us.assignee:
                overloaded_members[us.assignee] = overloaded_members.get(us.assignee, 0) + 1

        # Flag unassigned stories
        if unassigned:
            flags.append(f"{len(unassigned)} user stories are unassigned")
            recommendations.append("Assign all unclaimed stories to team members")
            if risk != "high":
                risk = "medium"

        # Flag stuck stories
        if stuck_stories:
            stuck_titles = ', '.join([us.id for us in stuck_stories])
            flags.append(f"Stories stuck in progress: {stuck_titles}")
            recommendations.append("Follow up on long-running tasks")
            risk = "high"

        # Flag members with more than 3 stories assigned
        overloaded = [member for member, count in overloaded_members.items() if count > 3]
        if overloaded:
            flags.append(f"Members with high story load: {', '.join(overloaded)}")
            recommendations.append("Balance story assignments across team")
            if risk != "high":
                risk = "medium"

        return [
            AnalysisResult(
                agent_type="sprint",
                member_id="team",
                risk=risk,
                flags=flags,
                recommendations=recommendations
            )
        ]
