from dataclasses import dataclass
from typing import List, Optional
# ==== Data Models ====

@dataclass
class DailyUpdate:
    member_id: str
    date: str
    mood: str
    blockers: List[str]
    achievements: List[str]
    comments: str
    working_hours: int

@dataclass
class WorkloadData:
    member_id: str
    active_tasks: int
    completed_tasks: int
    sla_breaches: int
    overtime_hours: int
    code_commits: int
    pull_requests: int

@dataclass
class GoalData:
    member_id: str
    sprint_goals: int
    completed_goals: int
    velocity: float
    story_points: int
    expected_completion: float

@dataclass
class AnalysisResult:
    agent_type: str
    member_id: str
    risk: str
    flags: List[str]
    recommendations: List[str]

@dataclass
class UserStory:
    id: str
    title: str
    assignee: str
    start_date: str
    status: str                  # e.g., "in progress", "done", "unassigned"
    story_points: Optional[int] = None
    tags: Optional[List[str]] = None

@dataclass
class SprintStatus:
    sprint_name: str
    start_date: str
    end_date: str
    completion: int              # e.g., 40%
    target: int                  # e.g., 60%
    critical_bugs: int
    unassigned_stories: int
    velocity: int                # Completed story points
    planned_velocity: int
    user_stories: List[UserStory]


@dataclass
class Sprint:
    id: int
    name: str
    state: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    complete_date: Optional[str] = None
    board_id: int = None
    goal: Optional[str] = None   
# ==== Sample Data ====
