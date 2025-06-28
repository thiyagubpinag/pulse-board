from datetime import datetime
from typing import List
from data_models import SprintStatus, DailyUpdate, AnalysisResult, WorkloadData

class SystemContextGenerator:
    @staticmethod
    def generate_context(
        sprints: List[SprintStatus],
        daily_updates: List[DailyUpdate],
        analysis_results: List[AnalysisResult],
        correlation: dict,
        workload_data: List[WorkloadData]
    ) -> str:
        today = datetime.today()

        if not sprints:
            return "No sprint data available."

        current = sprints[-1]
        previous = sprints[-2] if len(sprints) > 1 else None

        # === Sprint Flags & Recommendations ===
        sprint_flags = [res.flags for res in analysis_results if res.agent_type == "sprint"]
        sprint_recommendations = [res.recommendations for res in analysis_results if res.agent_type == "sprint"]
        sprint_flags_flat = [f for sub in sprint_flags for f in sub]
        sprint_recs_flat = [r for sub in sprint_recommendations for r in sub]

        # === SPRINT TREND ANALYSIS ===
        if previous:
            velocity_diff = current.velocity - previous.velocity
            completion_diff = current.completion - previous.completion
            bug_diff = current.critical_bugs - previous.critical_bugs

            trend_lines = [
                f"- Velocity changed: {previous.velocity} → {current.velocity} ({'+' if velocity_diff >= 0 else ''}{velocity_diff})",
                f"- Completion changed: {previous.completion}% → {current.completion}% ({'+' if completion_diff >= 0 else ''}{completion_diff}%)",
                f"- Critical bugs changed: {previous.critical_bugs} → {current.critical_bugs} ({'+' if bug_diff >= 0 else ''}{bug_diff})"
            ]
        else:
            trend_lines = ["- No previous sprint available for comparison."]

        # === User Story Details ===
        user_story_details = []
        for us in current.user_stories:
            assignee = us.assignee or "Unassigned"
            status = us.status
            try:
                start = datetime.strptime(us.start_date, "%Y-%m-%d")
                days_active = (today - start).days
            except:
                days_active = "N/A"

            est_days = us.story_points if us.story_points is not None else "?"
            remaining = (
                f"{int(est_days) - days_active} days left"
                if isinstance(days_active, int) and est_days != "?"
                else "N/A"
            )

            user_story_details.append(
                f"- {us.id}: '{us.title}' → {assignee} | status: {status}, started: {us.start_date or 'N/A'}, "
                f"est: {est_days}d, progress: {days_active}d active, {remaining}"
            )
        story_summary = "\n".join(user_story_details)

        # === Daily Update Summary ===
        daily_update_details = []
        for update in daily_updates:
            mood = update.mood.capitalize()
            blockers = ", ".join(update.blockers) if update.blockers else "None"
            progress = ", ".join(update.achievements) if update.achievements else "None"
            comments = update.comments or "No comment"
            hours = f"{update.working_hours}h"

            daily_update_details.append(
                f"- {update.member_id}: Mood: {mood} | Hours: {hours} | Blockers: {blockers} | "
                f"Progress: {progress} | Notes: {comments}"
            )
        daily_update_summary = "\n".join(daily_update_details)

        # === Workload Summary Per Member ===
        workload_summary_lines = []
        for w in workload_data:
            workload_summary_lines.append(
                f"- {w.member_id}: Tasks → active: {w.active_tasks}, completed: {w.completed_tasks} | "
                f"SLA breaches: {w.sla_breaches} | Overtime: {w.overtime_hours}h | "
                f"Commits: {w.code_commits}, PRs: {w.pull_requests}"
            )
        workload_summary = "\n".join(workload_summary_lines)

        # === Final Context Format ===
        context = f"""You are AskManager, an AI assistant for sprint and team health management.

SPRINT INFO: "{current.sprint_name}" ({current.start_date} → {current.end_date})
- Progress: {current.completion}% complete (target: {current.target}%)
- Velocity: {current.velocity} SP / {current.planned_velocity} SP
- Critical bugs: {current.critical_bugs}
- Unassigned stories: {current.unassigned_stories}

SPRINT TREND ANALYSIS:
{chr(10).join(trend_lines)}

SPRINT HEALTH FINDINGS:
{chr(10).join(f"- {flag}" for flag in sprint_flags_flat) if sprint_flags_flat else "- No major sprint-level risks detected"}

USER STORY DETAILS:
{story_summary if story_summary else "- No stories assigned for this sprint"}

DAILY TEAM UPDATES:
{daily_update_summary if daily_update_summary else "- No updates submitted today"}

WORKLOAD SUMMARY:
{workload_summary if workload_summary else "- No workload data available"}

TEAM HEALTH ANALYSIS:
- Critical Issues: {', '.join(correlation['critical']) if correlation['critical'] else 'None'}
- Overloaded members: {', '.join(correlation['overloaded']) if correlation['overloaded'] else 'None'}
- Underutilized members: {', '.join(correlation['underutilized']) if correlation['underutilized'] else 'None'}
- Burnout risk: {', '.join(correlation['burnout']) if correlation['burnout'] else 'None'}

KEY RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in (sprint_recs_flat + correlation['recommendations']))
    if sprint_recs_flat or correlation['recommendations']
    else '• No immediate actions required'}

Provide concise, actionable advice based on this data. Focus on practical solutions."""

        return context
