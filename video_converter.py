import cv2
import numpy as np
import os, shutil
import sys
from colour import Color
import conf
import datetime
from PIL import Image, ImageDraw, ImageFont

FRAME_INTERVAL = conf.FRAME_INTERVAL
ASCII_IMAGE_FOLDER = conf.ASCII_IMAGE_FOLDER
VIDEO_2_IMAGE_FOLDER = conf.VIDEO_2_IMAGE_FOLDER

def video2Pic(video_path, sc, gcf):
    videoCapture = cv2.VideoCapture()
    videoCapture.open(video_path)

    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)

    print("fps = ", fps, "Frames = ", frames)
    img_count = 0

    for i in range(int(frames)):
        img_path = "{}/{}.png".format(VIDEO_2_IMAGE_FOLDER, str(img_count))

        ret, frame = videoCapture.read()

        
        if ret is False:
            print("Frame %d read fail", i)
            break;
        
        if i % FRAME_INTERVAL == 0:
            cv2.imwrite(img_path, frame)

            asciiImg = asciiart(img_path, sc, gcf) 
            asciiImg_path = "{}/{}.png".format(ASCII_IMAGE_FOLDER, str(img_count))
            # print(asciiImg_path)
            asciiImg.save(asciiImg_path)

            img_count += 1

    return fps


def pic2Video(fps, image_folder):
    img = cv2.imread("{}/0.png".format(image_folder))
    size = (img.shape[1], img.shape[0])

# XVID -> avi
# MP4V -> mp4
# MJPG -> mp4
    fourcc = cv2.VideoWriter_fourcc(*"MP4V")
    videoWrite = cv2.VideoWriter("outputs/video/out001.mp4", fourcc, fps/FRAME_INTERVAL, size)

    print("Start writing to video")
    files = os.listdir(image_folder)
    num = len(files)
    print(num)
    for i in range(0, num):
        img_path = "{}/{}.png".format(image_folder, str(i))
        if not os.path.exists(img_path):
            print('Image not found')
            exit(-1)
        img = cv2.imread(img_path)
        videoWrite.write(img)

def removeImages(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def main():
    if len(sys.argv) > 1:
        media_path = sys.argv[1]
    else:
        media_path = "1.mp4"

    if len(sys.argv) > 2:
        sc = sys.argv[2]    # pixel sampling rate in width
    else:
        sc = conf.SC    # pixel sampling rate in width

    if len(sys.argv) > 3:
        gcf= sys.argv[3]      # contrast adjustment
    else:
        gcf= conf.GCF      # contrast adjustment

    starttime = datetime.datetime.now()

    if(media_path.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.tif', '.tiff'))):
        print("process Image")
        processImage(media_path, sc, gcf)
    else:
        print("process Video")
        processVideo(media_path, sc, gcf)

    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds)

def processVideo(video_path, sc, gcf):
    if not os.path.exists(video_path):
        print('Video not found')
        exit(-1)
    removeImages(ASCII_IMAGE_FOLDER)
    removeImages(VIDEO_2_IMAGE_FOLDER)
    
    fps = video2Pic(video_path=video_path, sc=sc, gcf=gcf )

    pic2Video(fps, ASCII_IMAGE_FOLDER)


def asciiart(in_f, SC, GCF, color1='black', color2='blue', bgcolor='white'):

    # The array of ascii symbols from white to black
    chars = np.asarray(list(' .,:irs?@9B&#'))

    # Load the fonts and then get the the height and width of a typical symbol 
    # You can use different fonts here
    font = ImageFont.load_default()
    letter_width = font.getsize("x")[0]
    letter_height = font.getsize("x")[1]

    WCF = letter_height/letter_width

    #open the input file
    img = Image.open(in_f)

    #Based on the desired output image size, calculate how many ascii letters are needed on the width and height
    widthByLetter=round(img.size[0]*SC*WCF)
    heightByLetter = round(img.size[1]*SC)
    S = (widthByLetter, heightByLetter)

    #Resize the image based on the symbol width and height
    img = img.resize(S)
    
    #Get the RGB color values of each sampled pixel point and convert them to graycolor using the average method.
    # Refer to https://www.johndcook.com/blog/2009/08/24/algorithms-convert-color-grayscale/ to know about the algorithm
    img = np.sum(np.asarray(img), axis=2)
    
    # Normalize the results, enhance and reduce the brightness contrast. 
    # Map grayscale values to bins of symbols
    img -= img.min()
    img = (1.0 - img/img.max())**GCF*(chars.size-1)
    
    # Generate the ascii art symbols 
    lines = ("\n".join( ("".join(r) for r in chars[img.astype(int)]) )).split("\n")

    # Create gradient color bins
    nbins = len(lines)
    colorRange =list(Color(color1).range_to(Color(color2), nbins))

    #Create an image object, set its width and height
    newImg_width= letter_width *widthByLetter
    newImg_height = letter_height * heightByLetter
    newImg = Image.new("RGBA", (newImg_width, newImg_height), bgcolor)
    draw = ImageDraw.Draw(newImg)

    # Print symbols to image
    leftpadding=0
    y = 0
    lineIdx=0
    for line in lines:
        color = colorRange[lineIdx]
        lineIdx +=1

        draw.text((leftpadding, y), line, color.hex, font=font)
        y += letter_height

    # Save the image file
    return newImg

# main
def processImage(image_path, sc, gcf):
    if not os.path.exists(image_path):
        print('Image not found')
        exit(-1)

    img = asciiart(image_path, sc, gcf) 
    asciiImg_path = "{}".format(conf.OUT)
    img.save(asciiImg_path)


if __name__ == "__main__":
    main()
    # pic2Video(30, ASCII_IMAGE_FOLDER)
