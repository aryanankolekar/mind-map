import yt_dlp
import json
import os

def extract_transcript(video_url):
    """
    Extracts the transcript from a YouTube video using yt-dlp.
    It fetches the best available auto-generated transcript, saves it as a JSON file, 
    parses it, and then cleans up the file.
    """
    # Ensure the temporary directory exists
    temp_dir = "data/temp"
    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        'writeautomaticsub': True,
        'skip_download': True,
        'subtitlesformat': 'json3',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'), # Save to a temp location
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_id = info.get('id')
            
            # Find the path to the downloaded subtitle file
            expected_sub_path = os.path.join(temp_dir, f"{video_id}.en.json3") # yt-dlp might add language code
            if not os.path.exists(expected_sub_path):
                # Fallback to check for any .json3 file for this video id
                found_files = [f for f in os.listdir(temp_dir) if f.startswith(video_id) and f.endswith('.json3')]
                if not found_files:
                    print("[ERROR] No subtitle file was downloaded.")
                    return ""
                expected_sub_path = os.path.join(temp_dir, found_files[0])

            # Read the JSON subtitle file
            with open(expected_sub_path, 'r', encoding='utf-8') as f:
                sub_data = json.load(f)
            
            # Clean up the downloaded file
            os.remove(expected_sub_path)

            # Combine the text from each event in the transcript
            if 'events' in sub_data:
                transcript = " ".join([seg['utf8'] for event in sub_data['events'] if 'segs' in event for seg in event['segs'] if 'utf8' in seg])
                return transcript.strip()
            else:
                print("[ERROR] JSON subtitle file is not in the expected format.")
                return ""

    except yt_dlp.utils.DownloadError as e:
        print(f"[ERROR] yt-dlp download error: {e}")
        # This can happen if no subtitles are available at all
        return ""
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in transcript extraction: {e}")
        return ""
