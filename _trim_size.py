from moviepy.editor import VideoFileClip

# Function to crop video
def crop_video(input_file, output_file, crop_top=0, crop_bottom=0, crop_left=0, crop_right=0):
    # Load the video
    clip = VideoFileClip(input_file)
    
    # Calculate new dimensions
    width, height = clip.size
    new_width = width - crop_left - crop_right
    new_height = height - crop_top - crop_bottom
    
    # Crop the video
    cropped_clip = clip.crop(x1=crop_left, y1=crop_top, x2=crop_left + new_width, y2=crop_top + new_height)
    
    # Write the output file
    cropped_clip.write_videofile(output_file)

# Example usage
input_filename = ".\\input\\" + "hr_rev01.mp4"
output_filename = ".\\input\\" +"hr_rev02.mp4"
crop_top = 0
crop_bottom = 44
crop_left = 0
crop_right = 0

crop_video(input_filename, output_filename, crop_top, crop_bottom, crop_left, crop_right)