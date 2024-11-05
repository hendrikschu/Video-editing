from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

in_loc = ".\\input\\" + "manifold_rev03.mp4"
out_loc = ".\\input\\" + "manifold_rev04.mp4"

# saves clip between start and end 
start_time = 0
end_time = 51

ffmpeg_extract_subclip(in_loc, start_time, end_time, targetname=out_loc)