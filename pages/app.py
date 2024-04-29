import os
import tempfile
import cv2
from flask import Flask, render_template, request, jsonify
from pytube import YouTube
import requests
import base64

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    youtube_link = request.form['youtube_link']
    video_path = download_video(youtube_link)
    frames_folder = extract_frames(video_path)
    hand_histories = analyze_frames(frames_folder)
    output_folder = "C:\\Users\\J9434\\PycharmProjects\\flaskProject1\\outputs"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "hand_histories.txt")
    with open(output_file, 'w') as f:
        f.write('\n'.join(hand_histories))
    return jsonify({'hand_histories': hand_histories})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    response = chat_with_claude(user_input)
    return jsonify({'response': response})

def download_video(youtube_link):
    yt = YouTube(youtube_link)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    video_path = video.download()
    return video_path

def extract_frames(video_path):
    frames_folder = tempfile.mkdtemp()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(frames_folder, f'frame_{frame_count}.jpg')
        cv2.imwrite(frame_path, frame)
        frame_count += 1
    cap.release()
    return frames_folder

def analyze_frames(frames_folder):
    hand_histories = []
    for frame_file in sorted(os.listdir(frames_folder)):
        frame_path = os.path.join(frames_folder, frame_file)
        with open(frame_path, 'rb') as f:
            frame_data = f.read()
        frame_base64 = base64.b64encode(frame_data).decode('utf-8')
        response = requests.post(
            'https://api.anthropic.com/v1/images/analyze',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer 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'
            },
            json={
                'image': frame_base64,
                'prompt': 'Analyze the poker hand in the image and generate a PokerStars hand history.'
            }
        )
        if response.status_code == 200:
            result = response.json()
            hand_history = result['output']
            hand_histories.append(hand_history)
    return hand_histories

def chat_with_claude(user_input):
    response = requests.post(
        'https://api.anthropic.com/v1/complete',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer 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'
        },
        json={
            'prompt': f'User: {user_input}\nAssistant:',
            'model': 'claude-v1',
            'max_tokens_to_sample': 100
        }
    )
    if response.status_code == 200:
        result = response.json()
        assistant_response = result['completion']
        return assistant_response
    else:
        return "Sorry, I couldn't generate a response at the moment."

if __name__ == '__main__':
    app.run()