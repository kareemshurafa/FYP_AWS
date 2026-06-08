from PIL import Image
import os

# Reference - adapted from https://www.tutorialspoint.com/python_pillow/python_pillow_change_color_by_changing_pixel_values.htm
# obtain the list of files
filelist = os.listdir("predictions")

for i in range(len(filelist)):
    # opening the image with conversion to RGBA to include transparency values
    image = Image.open("predictions/" + filelist[i]).convert("RGBA")

    # get pixel data from image
    pixels = list(image.getdata())

    # colour pixel definitions with an extra alpha value attatched for transparency
    # 255 = 0% transparency, 0 = 100% transparency
    red = (235, 34, 34, 255)
    blue = (34, 34, 255, 255)
    # transparent used for replacing the black background
    transparent = (0, 0, 0, 0)
    # colour 1 and colour 2 are the 2 greyscale values in the original prediction image
    colour1 = (1, 1, 1, 255)
    colour2 = (2, 2, 2, 255)
    black = (0, 0, 0, 255)

    # create a new list for the pixels to be added in the new image
    # goes through the pixel list of the original image pixels, and changes the colours respectively each iteration
    pixels = [red if pixel == colour2 else pixel for pixel in pixels]
    pixels = [blue if pixel == colour1 else pixel for pixel in pixels]
    pixels = [transparent if pixel == black else pixel for pixel in pixels]
    
    # creating a new blank RGBA image with the same dimensions
    new_image = Image.new("RGBA", image.size)
    # adds all the new pixels into the new image
    new_image.putdata(pixels)
    
    # saves image to file path
    new_image.save(filelist[i].removesuffix('.png') + "_prediction.png")

