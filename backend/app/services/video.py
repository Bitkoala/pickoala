import os
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VideoService:
    @staticmethod
    def generate_thumbnail(video_path: str, output_path: str, time_offset: str = "00:00:01") -> bool:
        """
        Generate a thumbnail for a video file using ffmpeg.
        
        :param video_path: Absolute path to the source video file.
        :param output_path: Absolute path where the thumbnail should be saved.
        :param time_offset: Timestamp to take the screenshot (default 1s).
        :return: True if successful, False otherwise.
        """
        try:
            # Check if input file exists
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False

            # Run ffmpeg command
            # ffmpeg -ss 00:00:01 -i input.mp4 -vframes 1 -q:v 2 output.jpg
            cmd = [
                "ffmpeg",
                "-y",               # Overwrite output file without asking
                "-ss", time_offset, # Seek to timestamp
                "-i", video_path,   # Input file
                "-vframes", "1",    # Output 1 frame
                "-q:v", "2",        # Quality (2-31, lower is better)
                output_path         # Output file
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return False
                
            if not os.path.exists(output_path):
                logger.error("FFmpeg finished but output file missing")
                return False
                
            return True

        except Exception as e:
            logger.exception(f"Error generating thumbnail: {str(e)}")
            return False

video_service = VideoService()
