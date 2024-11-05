from moviepy.editor import VideoFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

def speed_up_sequence(in_loc, start_time, end_time, multiplier, out_loc):
    # Import video clip
    clip = VideoFileClip(in_loc)
    
    # Split the video into three parts: before, during, and after the sequence to speed up
    before = clip.subclip(0, start_time)
    during = clip.subclip(start_time, end_time).fx(vfx.speedx, multiplier)
    after = clip.subclip(end_time)
    
    # Concatenate the parts back together
    final_clip = concatenate_videoclips([before, during, after])
    
    # Save the final video clip
    final_clip.write_videofile(out_loc, codec='libx264')

def speed_up_all(in_loc, multiplier, out_loc):
    # Import video clip
    clip = VideoFileClip(in_loc)
    
    # # Modify the FPS
    # clip = clip.set_fps(clip.fps * multiplier)

    # Speed up the entire video
    final_clip = clip.fx(vfx.speedx, multiplier)
    
    # Save the final video clip
    final_clip.write_videofile(out_loc, codec='libx264')

# Example usage
in_loc = ".\\input\\" + "cr_rev05.mp4"
out_loc = ".\\input\\" + "cr_rev06.mp4"
start_time = 24  # in seconds
end_time = 41  # in seconds
multiplier = 3

speed_up_sequence(in_loc, start_time, end_time, multiplier, out_loc)
# speed_up_all(in_loc, multiplier, out_loc)