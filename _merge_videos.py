from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

filename1 = "CR_5_cropped.mp4"
filename2 = "HR_Manifold_merged_merged.mp4"
filename_out = os.path.splitext(filename1)[0] + '__' + os.path.splitext(filename2)[0] + '.mp4'

# loading video dsa gfg intro video
clip1 = VideoFileClip(filename1)
clip2 = VideoFileClip(filename2)
 
# getting subclip as video is large
clip1_range = clip1.subclip(0, clip1.duration)
 
# getting subclip as video is large
clip2_range = clip2.subclip(0, clip2.duration)

# concatenating both the clips
final = concatenate_videoclips([clip1_range, clip2_range])

#writing the video into a file / saving the combined video
final.write_videofile(filename_out)
