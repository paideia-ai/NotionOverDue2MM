import os
from datetime import datetime, timedelta

import requests


def fetch_overdue_upcoming_tasks(api_key, database_id):
    # API URL to query the database
    query_url = f'https://api.notion.com/v1/databases/{database_id}/query'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    # Data for POST request to find tasks due before today
    today = datetime.now().strftime("%Y-%m-%d")
    # data = {"filter": {"property": "Due", "date": {"before": today}}}
    data = {
        "filter": {
            "and": [{
                "property": "Due",
                "date": {
                    "on_or_before":
                    (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
                }
            }, {
                "property": "Status",
                "status": {
                    "does_not_equal": "Done"
                }
            }, {
                "property": "Status",
                "status": {
                    "does_not_equal": "Archived"
                }
            }]
        }
    }
    response = requests.post(query_url, headers=headers, json=data)
    tasks = response.json().get('results', [])

    # print(tasks[:3]) #for debug purpose

    # Function to fetch user name from user ID , not used anymore
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
    upcoming_summary = "# Task due in 7 days\n"
    current_date = datetime.now()
    for task in tasks:
        due_date = parse_date(task['properties']['Due']['date']['start'])
        if due_date < current_date:
            task_name = task['properties']['Task name']['title'][0][
                'plain_text']
            status = task['properties']['Status']['status']['name']
            days_overdue = days_between(due_date, current_date)
            page_url = task['url']
            assignee_name = task['properties']['Assignee']['people'][0]['name']

            summary += f"## {task_name}\n"
            summary += f"- {assignee_name}\n"
            summary += f"- {status}\n"
            summary += f"- {days_overdue} days overdue\n"
            summary += f"- {page_url}\n"
        elif due_date >= current_date and due_date <= current_date + timedelta(
                days=7):
            task_name = task['properties']['Task name']['title'][0][
                'plain_text']
            status = task['properties']['Status']['status']['name']
            days_until_due = (due_date - current_date).days
            page_url = task['url']
            assignee_name = task['properties']['Assignee']['people'][0]['name']

            upcoming_summary += f"## {task_name}\n"
            upcoming_summary += f"- {assignee_name}\n"
            upcoming_summary += f"- {status}\n"
            upcoming_summary += f"- Due in {days_until_due} days\n"
            upcoming_summary += f"- {page_url}\n"

    return summary + "\n" + upcoming_summary


# retrieve notion overdue
api_key = os.environ['NOTION_API']
database_id = 'a05b2e9a2a38458db15a682ce03e9a4c'
notion_tasks = fetch_overdue_upcoming_tasks(api_key, database_id)


def post_to_mattermost(channel_id, message, bot_token):
    url = 'https://mattermost.paideia.uno/api/v4/posts'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bot_token}'
    }
    data = {
        'channel_id': channel_id,
        'message': message,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print('Message posted to Mattermost successfully.')
    else:
        print(
            f'Failed to post message to Mattermost. Status code: {response.status_code}'
        )


# Example call to post_to_mattermost function
# Ensure you replace 'your_bot_token_here' with your actual Mattermost bot token

mm_bot_acc = os.environ['MM_BOT_ACC']
post_to_mattermost('a9mk36w6htbdtbeddf4za19pph', notion_tasks, mm_bot_acc)
