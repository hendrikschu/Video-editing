from moviepy.editor import VideoFileClip

filename = ".\\input\\cr_rev05.mp4"
filename_out = ".\\input\\cr_rev06.mp4"
first_seconds_cut = 0
last_seconds_cut = 45

# loading video dsa gfg intro video
clip = VideoFileClip(filename)

# get video duration 
duration = clip.duration 

# getting subclip as video is large
final = clip.subclip(first_seconds_cut, duration - last_seconds_cut)

#writing the video into a file / saving the combined video
final.write_videofile(filename_out)
