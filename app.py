from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import yt_dlp

app = Flask(__name__)
app.config['CLIP_FOLDER'] = 'clips'
app.config['DOWNLOAD_FOLDER'] = 'downloads'

# Create folders if they don't exist
os.makedirs(app.config['CLIP_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def time_to_seconds(time_str):
    """Convert HH:MM:SS to seconds."""
    parts = list(map(int, time_str.split(':')))
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s

@app.route('/cut', methods=['POST'])
def cut_clip():
    data = request.get_json()
    url = data.get('url')
    start_time = data.get('start')
    end_time = data.get('end')

    if not url or not start_time or not end_time:
        return jsonify({'error': 'Missing fields'}), 400

    try:
        video_id = str(uuid.uuid4())
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{video_id}.mp4")
        clip_path = os.path.join(app.config['CLIP_FOLDER'], f"{video_id}_clip.mp4")

        # Download video using yt-dlp
        ydl_opts = {
            'outtmpl': download_path,
            'format': 'mp4/best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        start_sec = time_to_seconds(start_time)
        end_sec = time_to_seconds(end_time)

        # Load and trim the video
        clip = VideoFileClip(download_path).subclip(start_sec, end_sec)

        # Convert to vertical if necessary
        if clip.w > clip.h:
            target_width = clip.h * 9 / 16
            x_center = clip.w / 2
            vertical_clip = clip.crop(
                x_center=x_center,
                width=target_width,
                height=clip.h
            ).resize(height=720)
        else:
            vertical_clip = clip.resize(height=720)

        # Add watermark
        watermark = TextClip("Clipify", fontsize=40, color='white', font='Arial-Bold')
        watermark = watermark.set_position(("center", "bottom")).set_duration(vertical_clip.duration).set_opacity(0.7)

        final = CompositeVideoClip([vertical_clip, watermark])
        final.write_videofile(clip_path, codec='libx264', audio_codec='aac')

        return jsonify({'link': f'/clips/{os.path.basename(clip_path)}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clips/<filename>')
def serve_clip(filename):
    return send_from_directory(app.config['CLIP_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
