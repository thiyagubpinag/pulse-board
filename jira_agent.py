import os
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
import sys
from urllib.parse import quote

from data_models import Sprint, SprintStatus, UserStory

load_dotenv()

# ==== Jira Auth & Config ====
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BOARD_ID = os.getenv("JIRA_BOARD_ID")

# Validate required environment variables
required_vars = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_BOARD_ID"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Clean up the base URL
JIRA_BASE_URL = JIRA_BASE_URL.rstrip('/')
if '//' in JIRA_BASE_URL.replace('https://', '').replace('http://', ''):
    JIRA_BASE_URL = JIRA_BASE_URL.replace('//', '/')

auth = (JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ==== Jira API Functions ====

def make_jira_request(url: str, retry_count: int = 2) -> Optional[Dict[str, Any]]:
    """Make a request to Jira API with error handling and retry logic."""
    for attempt in range(retry_count + 1):
        try:
            print(f"Making request to: {url} (attempt {attempt + 1})")
            response = requests.get(url, headers=headers, auth=auth, timeout=60)  # Increased timeout
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            print(f"Timeout on attempt {attempt + 1}: {e}")
            if attempt < retry_count:
                print("Retrying...")
                continue
            else:
                print("Max retries reached. Continuing with partial data...")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    return None

def get_board_id_by_name(board_name: str) -> Optional[int]:
    """Get board ID by board name."""
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    
    data = make_jira_request(url)
    if not data:
        return None
    
    boards = data.get("values", [])
    for board in boards:
        if board.get("name") == board_name:
            return board.get("id")
    
    print(f"Board '{board_name}' not found.")
    return None

def get_active_sprint() -> Optional[Sprint]:
    """Fetch the active sprint from the specified board."""
    try:
        board_id = int(JIRA_BOARD_ID)
    except ValueError:
        print(f"Board identifier '{JIRA_BOARD_ID}' is not numeric. Looking up board ID...")
        board_id = get_board_id_by_name(JIRA_BOARD_ID)
        if not board_id:
            return None
    
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint?state=active"
    
    data = make_jira_request(url)
    if not data:
        return None
    
    sprints = data.get("values", [])
    if not sprints:
        print("No active sprints found.")
        return None
    
    sprint_data = sprints[0]
    
    return Sprint(
        id=sprint_data.get("id"),
        name=sprint_data.get("name"),
        state=sprint_data.get("state"),
        start_date=sprint_data.get("startDate"),
        end_date=sprint_data.get("endDate"),
        complete_date=sprint_data.get("completeDate"),
        board_id=sprint_data.get("originBoardId"),
        goal=sprint_data.get("goal", "")
    )

def get_sprint_issues(sprint_id: int, max_issues: int = 100) -> List[Dict[str, Any]]:
    """Get all issues in a sprint with improved error handling."""
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    
    all_issues = []
    start_at = 0
    max_results = 50
    
    while start_at < max_issues:  # Limit total requests to avoid timeouts
        paginated_url = f"{url}?startAt={start_at}&maxResults={max_results}&fields=summary,assignee,status,customfield_10016,labels,created,issuetype,priority"
        
        data = make_jira_request(paginated_url)
        if not data:
            print(f"Failed to fetch issues starting at {start_at}. Using partial data...")
            break
        
        issues = data.get("issues", [])
        if not issues:
            print("No more issues found.")
            break
        
        all_issues.extend(issues)
        print(f"Fetched {len(all_issues)} issues so far...")
        
        # Check if there are more results
        if len(issues) < max_results:
            print("Reached end of issues.")
            break
        
        start_at += max_results
    
    return all_issues

def extract_story_points(issue: Dict[str, Any]) -> Optional[int]:
    """Extract story points from issue (customfield_10016 is common for story points)."""
    fields = issue.get("fields", {})
    
    # Common story points fields - adjust these based on your Jira configuration
    story_points_fields = [
        "customfield_10016",  # Common story points field
        "customfield_10004",  # Alternative story points field
        "storyPoints",
        "customfield_10002"
    ]
    
    for field in story_points_fields:
        if field in fields and fields[field] is not None:
            try:
                return int(float(fields[field]))
            except (ValueError, TypeError):
                continue
    
    return None

def parse_user_story(issue: Dict[str, Any]) -> UserStory:
    """Parse Jira issue into UserStory format."""
    fields = issue.get("fields", {})
    
    # Extract assignee
    assignee_data = fields.get("assignee")
    assignee = assignee_data.get("displayName", "Unassigned") if assignee_data else "Unassigned"
    
    # Extract status
    status_data = fields.get("status", {})
    status = status_data.get("name", "Unknown").lower()
    
    # Extract labels/tags
    labels = fields.get("labels", [])
    
    # Extract creation date as start date
    created = fields.get("created", "")
    start_date = created.split("T")[0] if created else ""
    
    return UserStory(
        id=issue.get("key", ""),
        title=fields.get("summary", ""),
        assignee=assignee,
        start_date=start_date,
        status=status,
        story_points=extract_story_points(issue),
        tags=labels if labels else None
    )

def calculate_sprint_metrics(user_stories: List[UserStory], sprint: Sprint) -> Dict[str, int]:
    """Calculate sprint metrics from user stories."""
    total_stories = len(user_stories)
    completed_stories = len([s for s in user_stories if s.status.lower() in ["done", "completed", "closed"]])
    unassigned_stories = len([s for s in user_stories if s.assignee.lower() == "unassigned"])
    
    # Calculate story points
    total_story_points = sum(story.story_points for story in user_stories if story.story_points)
    completed_story_points = sum(
        story.story_points for story in user_stories 
        if story.story_points and story.status.lower() in ["done", "completed", "closed"]
    )
    
    # Calculate completion percentage
    completion = int((completed_stories / total_stories * 100)) if total_stories > 0 else 0
    
    # Count critical bugs (issues with high/highest priority and bug type)
    critical_bugs = len([
        s for s in user_stories 
        if any(tag and ("bug" in tag.lower() or "critical" in tag.lower()) for tag in (s.tags or []))
    ])
    
    return {
        "completion": completion,
        "target": 80,  # Default target, adjust as needed
        "critical_bugs": critical_bugs,
        "unassigned_stories": unassigned_stories,
        "velocity": completed_story_points,
        "planned_velocity": total_story_points
    }

def get_sprint_status() -> Optional[SprintStatus]:
    """Get complete sprint status with all user stories and metrics."""
    
    # Get active sprint
    sprint = get_active_sprint()
    if not sprint:
        print("No active sprint found.")
        return None
    
    print(f"Found active sprint: {sprint.name}")
    
    # Get all issues in the sprint
    sprint_issues = get_sprint_issues(sprint.id)
    if not sprint_issues:
        print("No issues found in sprint.")
        return None
    
    print(f"Found {len(sprint_issues)} issues in sprint")
    
    # Parse issues into UserStory objects
    user_stories = [parse_user_story(issue) for issue in sprint_issues]
    
    # Calculate metrics
    metrics = calculate_sprint_metrics(user_stories, sprint)
    
    # Create SprintStatus object
    sprint_status = SprintStatus(
        sprint_name=sprint.name,
        start_date=sprint.start_date.split("T")[0] if sprint.start_date else "",
        end_date=sprint.end_date.split("T")[0] if sprint.end_date else "",
        completion=metrics["completion"],
        target=metrics["target"],
        critical_bugs=metrics["critical_bugs"],
        unassigned_stories=metrics["unassigned_stories"],
        velocity=metrics["velocity"],
        planned_velocity=metrics["planned_velocity"],
        user_stories=user_stories
    )
    
    return sprint_status

def print_sample_data(sprint_status: SprintStatus):
    """Print a sample of the data structure for verification."""
    print("\n" + "="*60)
    print("SAMPLE DATA STRUCTURE:")
    print("="*60)
    
    # SprintStatus sample
    print("SprintStatus:")
    print(f"  sprint_name: '{sprint_status.sprint_name}'")
    print(f"  start_date: '{sprint_status.start_date}'")
    print(f"  end_date: '{sprint_status.end_date}'")
    print(f"  completion: {sprint_status.completion}")
    print(f"  target: {sprint_status.target}")
    print(f"  critical_bugs: {sprint_status.critical_bugs}")
    print(f"  unassigned_stories: {sprint_status.unassigned_stories}")
    print(f"  velocity: {sprint_status.velocity}")
    print(f"  planned_velocity: {sprint_status.planned_velocity}")
    print(f"  user_stories: List[UserStory] (length: {len(sprint_status.user_stories)})")
    
    # UserStory samples
    if sprint_status.user_stories:
        print("\nFirst 3 UserStory examples:")
        for i, story in enumerate(sprint_status.user_stories[:3]):
            print(f"\nUserStory {i+1}:")
            print(f"  id: '{story.id}'")
            print(f"  title: '{story.title[:60]}...' " if len(story.title) > 60 else f"  title: '{story.title}'")
            print(f"  assignee: '{story.assignee}'")
            print(f"  start_date: '{story.start_date}'")
            print(f"  status: '{story.status}'")
            print(f"  story_points: {story.story_points}")
            print(f"  tags: {story.tags}")

def print_sprint_status(sprint_status: SprintStatus):
    """Pretty print the sprint status."""
    print("\n" + "="*60)
    print(f"SPRINT STATUS: {sprint_status.sprint_name}")
    print("="*60)
    print(f"Duration: {sprint_status.start_date} to {sprint_status.end_date}")
    print(f"Completion: {sprint_status.completion}% (Target: {sprint_status.target}%)")
    print(f"Velocity: {sprint_status.velocity}/{sprint_status.planned_velocity} story points")
    print(f"Critical Bugs: {sprint_status.critical_bugs}")
    print(f"Unassigned Stories: {sprint_status.unassigned_stories}")
    print(f"Total User Stories: {len(sprint_status.user_stories)}")
    
    print("\nFIRST 5 USER STORIES:")
    print("-" * 60)
    
    for i, story in enumerate(sprint_status.user_stories[:5]):
        print(f"{i+1}. ID: {story.id}")
        print(f"   Title: {story.title}")
        print(f"   Assignee: {story.assignee}")
        print(f"   Status: {story.status}")
        print(f"   Story Points: {story.story_points}")
        print(f"   Start Date: {story.start_date}")
        if story.tags:
            print(f"   Tags: {', '.join(story.tags)}")
        print("-" * 40)
    
    if len(sprint_status.user_stories) > 5:
        print(f"... and {len(sprint_status.user_stories) - 5} more stories")

def get_all_sprints(board_id: int) -> List[Sprint]:
    """Fetch all sprints from the Jira board."""
    sprints = []
    start_at = 0
    while True:
        url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint?startAt={start_at}&maxResults=50"
        data = make_jira_request(url)
        if not data or "values" not in data:
            break

        for s in data["values"]:
            sprints.append(Sprint(
                id=s["id"],
                name=s["name"],
                state=s["state"],
                start_date=s.get("startDate"),
                end_date=s.get("endDate"),
                complete_date=s.get("completeDate"),
                board_id=s.get("originBoardId"),
                goal=s.get("goal")
            ))

        if data.get("isLast", True):
            break
        start_at += 50
    return sprints

def get_sprint_status_for_sprint(sprint: Sprint) -> Optional[SprintStatus]:
    issues = get_sprint_issues(sprint.id)
    if not issues:
        return None
    user_stories = [parse_user_story(issue) for issue in issues]
    metrics = calculate_sprint_metrics(user_stories, sprint)

    return SprintStatus(
        sprint_name=sprint.name,
        start_date=sprint.start_date.split("T")[0] if sprint.start_date else "",
        end_date=sprint.end_date.split("T")[0] if sprint.end_date else "",
        completion=metrics["completion"],
        target=metrics["target"],
        critical_bugs=metrics["critical_bugs"],
        unassigned_stories=metrics["unassigned_stories"],
        velocity=metrics["velocity"],
        planned_velocity=metrics["planned_velocity"],
        user_stories=user_stories
    )

def generate_sprint_code_array(sprint_statuses: List[SprintStatus]) -> str:
    def format_user_story(story: UserStory) -> str:
        tags_str = f', {story.tags}' if story.tags else ''
        return f'UserStory("{story.id}", "{story.title}", "{story.assignee}", "{story.start_date}", "{story.status}", {story.story_points}{tags_str})'

    code_lines = ['self.sprints = [']
    for sprint in sprint_statuses:
        code_lines.append(f'    SprintStatus(')
        code_lines.append(f'        sprint_name="{sprint.sprint_name}",')
        code_lines.append(f'        start_date="{sprint.start_date}",')
        code_lines.append(f'        end_date="{sprint.end_date}",')
        code_lines.append(f'        completion={sprint.completion},')
        code_lines.append(f'        target={sprint.target},')
        code_lines.append(f'        critical_bugs={sprint.critical_bugs},')
        code_lines.append(f'        unassigned_stories={sprint.unassigned_stories},')
        code_lines.append(f'        velocity={sprint.velocity},')
        code_lines.append(f'        planned_velocity={sprint.planned_velocity},')
        code_lines.append(f'        user_stories=[')
        for story in sprint.user_stories:
            code_lines.append(f'            {format_user_story(story)},')
        code_lines.append(f'        ]')
        code_lines.append(f'    ),')
    code_lines.append(']')
    return '\n'.join(code_lines)

def fetch_all_sprint_statuses(limit: int = 2) -> List[SprintStatus]:
    """
    Fetch the last `limit` number of sprints (including active sprint) and generate SprintStatus list.
    
    Args:
        limit (int): Number of most recent sprints to fetch. Default is 3.
    
    Returns:
        List[SprintStatus]: List of populated SprintStatus dataclass instances.
    """
    print(f"Fetching last {limit} sprints and generating SprintStatus list...")

    board_id = int(JIRA_BOARD_ID) if JIRA_BOARD_ID.isdigit() else get_board_id_by_name(JIRA_BOARD_ID)
    if not board_id:
        print("Board ID not found. Exiting.")
        return []

    all_sprints = get_all_sprints(board_id)
    if not all_sprints:
        print("No sprints found on board.")
        return []

    sprint_statuses = []
    for sprint in all_sprints[-limit:]:  # Adjust how many sprints to return
        status = get_sprint_status_for_sprint(sprint)
        if status:
            sprint_statuses.append(status)

    return sprint_statuses
