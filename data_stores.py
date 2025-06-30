
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

        # self.sprints = fetch_all_sprint_statuses()
        
        self.sprints = [
             # Sprint 40 - before last
            SprintStatus(
                sprint_name="Sprint 40 - Griffin",
                start_date="2025-05-15",
                end_date="2025-05-29",
                completion=75,
                target=80,
                critical_bugs=1,
                unassigned_stories=1,
                velocity=70,
                planned_velocity=80,
                user_stories=[
                    UserStory("US-081", "Add feature toggle", "alice", "2025-05-15", "done", 8),
                    UserStory("US-082", "Write unit tests", "bob", "2025-05-16", "done", 5)
                ]
            ),

            # Sprint 41 - last sprint
            SprintStatus(
                sprint_name="Sprint 41 - Falcon",
                start_date="2025-06-01",
                end_date="2025-06-15",
                completion=70,
                target=70,
                critical_bugs=1,
                unassigned_stories=0,
                velocity=65,
                planned_velocity=70,
                user_stories=[
                    UserStory("US-091", "Add settings page", "alice", "2025-06-01", "done", 5),
                    UserStory("US-092", "Refactor auth module", "bob", "2025-06-02", "done", 8),
                    UserStory("US-093", "Design onboarding UI", "charlie", "2025-06-03", "done", 5)
                ]
            ),

            # Sprint 42 - current sprint
            SprintStatus(
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
        ]

