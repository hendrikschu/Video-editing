from moviepy.editor import VideoFileClip
 
# loading video 
filename = "Final_1080.mp4"
ratio = 1.0     # 1080 > 720
clip = VideoFileClip(filename)
clip_out = filename.split('.')[0] + '_resized_' + int(ratio*100) + 'pc.mp4'

# getting width and height of clip 1
# w1 = clip.w
# h1 = clip.h

# resizing video downsize 50 % 
clip2 = clip.resize(ratio)

clip2.write_videofile(clip_out)