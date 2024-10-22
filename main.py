import redis
import json
from github_issue_creator import create_issues_for_repo

def process_repo_message(repo_data):
    # Extract necessary information from the message
    repo_name = repo_data['repo_name']
    owner = repo_data['owner']
    token = repo_data['token']

    # Call the existing function to create issues
    create_issues_for_repo(repo_name, owner, token)

def main():
    # Set up Redis connection
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = redis_client.pubsub()

    # Subscribe to the channel
    pubsub.subscribe('repo_ready_for_issues')

    print("Listening for messages on 'repo_ready_for_issues' channel...")

    # Listen for messages
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                repo_data = json.loads(message['data'])
                print(f"Received message for repo: {repo_data['repo_name']}")
                process_repo_message(repo_data)
            except json.JSONDecodeError:
                print("Error: Invalid JSON message received")
            except KeyError as e:
                print(f"Error: Missing required key in message: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")

if __name__ == "__main__":
    main()
