import os
import re
import instaloader
from typing import Dict, Optional
from datetime import datetime

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
temp_path = os.path.join(data_dir, 'temporary_downloads')

INSTAGRAM_REEL_PATTERN = r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([A-Za-z0-9_-]{11})/?'

def download_reel(url: str):
    shortcode = validate_and_extract_id(url)
    if not shortcode:
        raise ValueError("Invalid Instagram URL")
    
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=True,
        download_comments=False,
        save_metadata=False,
        quiet=True,
        download_video_thumbnails=False
    )

    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    if not post.is_video:
        raise ValueError("URL does not point to a video/reel")
    
    metadata = {
        'shortcode': post.shortcode,
        'url': url,
        'caption': post.caption if post.caption else "",
        'caption_hashtags': list(post.caption_hashtags) if post.caption_hashtags else [],
        'caption_mentions': list(post.caption_mentions) if post.caption_mentions else [],
        'likes': post.likes,
        'comments_count': post.comments,
        'views': post.video_view_count,
        'duration': post.video_duration,
        'date_posted': post.date.strftime("%Y-%m-%d_%H-%M-%S_UTC") if post.date else None,
        'owner_username': post.owner_username,
        'owner_id': post.owner_id,
        'is_sponsored': post.is_sponsored if hasattr(post, 'is_sponsored') else False,
    }

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    loader.download_post(post, target=os.path.basename(temp_path))

        # Find the downloaded video file
    video_file = os.path.join(temp_path, f'{metadata['date']}.mp4')
    if not video_file:
        raise FileNotFoundError("No video downloaded")
    
    return metadata, video_file

def validate_and_extract_id(url: str) -> Optional[str]:
    """Extract Instagram post/reel ID from URL"""
    pattern = re.compile(INSTAGRAM_REEL_PATTERN)
    match = pattern.match(url)
    return match.group(1) if match else None