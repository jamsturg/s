import os
from googleapiclient.discovery import build

API_KEY = "AIzaSyD06KbGHAHPtjInLO_T1qgsqem99bcnVHA"

def get_user_input():
    api_key = input("Enter your YouTube API key: ")
    playlist_id = input("Enter the playlist ID: ")
    print("Enter player names separated by commas (e.g., Player1,Player2,Player3):")
    players = input().split(',')
    sanitized_players = []
    for player in players:
        sanitized_player = player.strip().replace(' ', '_')
        sanitized_players.append(sanitized_player)
    return api_key, playlist_id, sanitized_players

def sanitize_title(title):
    """Sanitize and shorten the video title to ensure valid path names."""
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        title = title.replace(char, '')
    title = title[:50]  # Limit title length to avoid path length issues
    title = title.replace(' ', '_')  # Replace spaces with underscores
    return title


def fetch_playlist_items(youtube, playlist_id, pageToken=None):
    return youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50,  # Adjust based on your needs
        pageToken=pageToken
    ).execute()


def create_directory_structure(api_key, playlist_id, players):
    youtube = build('youtube', 'v3', developerKey=api_key)
    base_path = os.path.join('C:\\Users\\J9434\\PycharmProjects\\flaskProject1', 'HCL Poker Hand Histories')
    os.makedirs(base_path, exist_ok=True)

    next_page_token = None
    while True:
        response = fetch_playlist_items(youtube, playlist_id, next_page_token)
        for item in response['items']:
            video_title = sanitize_title(item['snippet']['title'])
            video_date = item['snippet']['publishedAt'][:10]  # Gets only the date part YYYY-MM-DD
            folder_name = f"{video_date} {video_title}"
            folder_path = os.path.join(base_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Adding subfolders for each player
            for player in players:
                player_folder_path = os.path.join(folder_path, player)
                os.makedirs(player_folder_path, exist_ok=True)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

if __name__ == '__main__':
    api_key, playlist_id, players = get_user_input()
    create_directory_structure(api_key, playlist_id, players)
