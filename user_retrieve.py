import requests
import os

response = requests.get(
    'https://api.notion.com/v1/users/75e0990f-e7c0-4599-a4a1-2836ba272b88',
    headers={
        'Authorization': 'Bearer ' + os.environ['NOTION_API'],
        'Notion-Version': '2022-06-28'
    })

print(response.json())
