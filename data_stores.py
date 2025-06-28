
from data_models import DailyUpdate, GoalData, SprintStatus, UserStory, WorkloadData


class DataStore:
    def __init__(self):
        self.daily_updates = [
            DailyUpdate("alice", "2025-06-28", "stressed", 
                       ["API integration issues", "Database migration"],
                       ["Fixed critical bug #458"],
                       "Working late all week, feeling overwhelmed", 10),
            DailyUpdate("bob", "2025-06-28", "okay", [],
                       ["Code review completed"],
                       "Light workload, available for more tasks", 6),
            DailyUpdate("charlie", "2025-06-28", "good",
                       ["Waiting for design approval"],
                       ["Sprint planning session", "New feature development"],
                       "Making good progress on user stories", 8)
        ]
        
        self.workload_data = [
            WorkloadData("alice", 12, 8, 2, 15, 25, 8),
            WorkloadData("bob", 3, 5, 0, 2, 8, 3),
            WorkloadData("charlie", 7, 9, 1, 5, 18, 6)
        ]
        
        self.goal_data = [
            GoalData("alice", 10, 6, 0.6, 32, 0.8),
            GoalData("bob", 6, 4, 0.67, 15, 0.7),
            GoalData("charlie", 8, 7, 0.875, 24, 0.85)
        ]

        
        self.sprint_status = SprintStatus(
            sprint_name="Sprint 42 - Phoenix",
            start_date="2025-06-17",
            end_date="2025-07-01",
            completion=40,
            target=60,
            critical_bugs=3,
            unassigned_stories=3,
            velocity=45,
            planned_velocity=75,
            user_stories=[
                UserStory("US-101", "Implement login API", "alice", "2025-06-17", "in progress", 5, ["backend"]),
                UserStory("US-102", "Create dashboard UI", "charlie", "2025-06-18", "in progress", 8, ["frontend"]),
                UserStory("US-103", "Fix session bug", "alice", "2025-06-20", "done", 3),
                UserStory("US-104", "Prepare test suite", "bob", "2025-06-21", "todo", 5, ["qa"]),
                UserStory("US-105", "Update documentation", "", "", "unassigned", 2)
            ]
        )

