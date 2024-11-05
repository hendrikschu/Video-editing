from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import concatenate_videoclips, VideoFileClip

def remove_segment(input_file, start_remove, end_remove, output_file):
    """
    Removes a segment from start_remove to end_remove from the video and saves the result as output_file.
    
    :param input_file: Path to the input video file.
    :param start_remove: Start time of the segment to remove in seconds.
    :param end_remove: End time of the segment to remove in seconds.
    :param output_file: Path to save the resulting video file.
    """
    # Load the video
    video = VideoFileClip(input_file)
    
    # Define the clips before and after the segment to remove
    clip_before = video.subclip(0, start_remove)
    clip_after = video.subclip(end_remove, video.duration)
    
    # Concatenate the clips
    final_clip = concatenate_videoclips([clip_before, clip_after])
    
    # Write the result to the output file
    final_clip.write_videofile(output_file, codec="libx264")
    print(f"Segment removed and video saved as {output_file}")

if __name__ == "__main__":
    input_file = ".\\input\\manifold_rev02.mp4"
    start_remove = 28
    end_remove = 38
    output_file = ".\\input\\manifold_rev03.mp4"

    remove_segment(input_file, start_remove, end_remove, output_file)