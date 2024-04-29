from datetime import datetime
import requests
import os


def fetch_overdue_tasks(api_key, database_id):
  # API URL to query the database
  query_url = f'https://api.notion.com/v1/databases/{database_id}/query'
  headers = {
      'Authorization': f'Bearer {api_key}',
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json'
  }
  # Data for POST request to find tasks due before today
  today = datetime.now().strftime("%Y-%m-%d")
  data = {"filter": {"property": "Due", "date": {"before": today}}}
  response = requests.post(query_url, headers=headers, json=data)
  tasks = response.json().get('results', [])

  # Function to fetch user name from user ID
  def get_user_name(user_id):
    user_url = f'https://api.notion.com/v1/users/{user_id}'
    user_response = requests.get(user_url, headers=headers)
    user_data = user_response.json()
    return user_data.get('name', 'Unknown User')

  # Function to parse dates and calculate overdue days
  def parse_date(iso_date):
    return datetime.fromisoformat(iso_date.replace('Z', '+00:00'))

  def days_between(d1, d2):
    return abs((d2 - d1).days)

  # Build the summary string
  summary = "# overdue task summary\n"
  current_date = datetime.now()
  for task in tasks:
    due_date = parse_date(task['properties']['Due']['date']['start'])
    if due_date < current_date:
      task_name = task['properties']['Task name']['title'][0]['plain_text']
      assignee_id = task['properties']['Assignee']['people'][0]['id']
      status = task['properties']['Status']['status']['name']
      days_overdue = days_between(due_date, current_date)
      page_url = task['url']
      assignee_name = get_user_name(assignee_id)

      summary += f"## {task_name}\n"
      summary += f"- {assignee_name}\n"
      summary += f"- {status}\n"
      summary += f"- {days_overdue} days overdue\n"
      summary += f"- {page_url}\n"

  return summary


# Example usage:
api_key = os.environ['NOTION_API']

database_id = 'a05b2e9a2a38458db15a682ce03e9a4c'
print(fetch_overdue_tasks(api_key, database_id))
