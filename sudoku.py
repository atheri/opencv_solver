import sys
import cv2
import numpy as np

def main():

    # Require image be provided on command line
    if len(sys.argv) != 2:
        print("Usage: python3 sudoku.py [image]")
        sys.exit()

    # Load Image
    img = cv2.imread(sys.argv[1])
    height, width, channels = img.shape
    
    # Resize image so both dimensions are less than max_dim
    max_dim = 1000
    if height > max_dim or width > max_dim:
        if height > width:
            img = cv2.resize(img, None, fx=max_dim/height, fy=max_dim/height, interpolation=cv2.INTER_AREA)
        else:
            img = cv2.resize(img, None, fx=max_dim/width, fy=max_dim/width, interpolation=cv2.INTER_AREA)

    # Blur and grayscale image
    blur = cv2.GaussianBlur(img,(5,5),0) # Tuple level of blur, must be odd
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY) # Grayscale

    # Create a black image to be used as a mask the same dimensions as image
    mask = np.zeros((gray.shape), np.uint8)

    # A circular kernel for the morphologyEx function
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11))  # Tuple adjusts circle size
    # Create a 'background' image with morphologic close
    close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    
    # Use the closing image to normalize brightness / background 
    div = np.float32(gray)/close
    global adjusted_src
    adjusted_src = np.uint8(cv2.normalize(div, div, 0, 255, cv2.NORM_MINMAX)) # Turn color values back to 0-255 from floats

    # Threshold to binary image to find contours
    thresh = cv2.adaptiveThreshold(adjusted_src, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 2)
    _, contours, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # find Contour with largest area (should be sudoku grid)
    best_cnt = find_n_largest_contours(1,contours)

    # Update mask image
    cv2.drawContours(mask, [best_cnt[0]], 0, 255, -1)

    # Second order Sobel derivative to find horizontal and vertical lines
    # looks at change in color intensity
    sobelx = cv2.Sobel(adjusted_src,-1,2,0,ksize=5)
    sobely = cv2.Sobel(adjusted_src,-1,0,2,ksize=5)
    
    # AND with mask to get rid of image outside of sudoku grid
    maskedx = cv2.bitwise_and(sobelx,mask)
    maskedy = cv2.bitwise_and(sobely,mask)
   
    # Clean up some noise before finding contours
    _, threshx = cv2.threshold(maskedx, 200, 255, cv2.THRESH_BINARY)
    _, threshy = cv2.threshold(maskedy, 200, 255, cv2.THRESH_BINARY)
   
    # Dilate the lines the help ensure that it is solid (dilation increases white size)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1,6))
    threshx = cv2.dilate(threshx, kernel, iterations=1)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(6,1))
    threshy = cv2.dilate(threshy, kernel, iterations=1)

    # Find contours of vertical and horizontal line images
    _, cnts_x, hier = cv2.findContours(threshx, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    _, cnts_y, hier = cv2.findContours(threshy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
   

    lines_x = find_n_largest_contours(10, cnts_x)
    lines_y = find_n_largest_contours(10, cnts_y)
    
    line_img_x = np.zeros((img.shape), np.uint8)
    line_img_y = np.zeros((img.shape), np.uint8)
    for line in lines_x:
        cv2.drawContours(line_img_x,[line],0,(255,255,255),-1)
    for line in lines_y:
        cv2.drawContours(line_img_y,[line],0,(255,255,255),-1)

    cv2.imshow('line_img_x', line_img_x)
    cv2.imshow('line_img_y', line_img_y)
    # Display Image
    #cv2.namedWindow('masked')
    #cv2.namedWindow('res')
    #cv2.createTrackbar('B', 'thresh', 5, 100, remake)
    #cv2.setTrackbarPos('B', 'thresh', 7)
    cv2.waitKey(0)              # Waits for any keypress
    cv2.destroyAllWindows()               

def find_n_largest_contours(n, contours):
    area_list = [(cv2.contourArea(cnt), cnt) for cnt in contours]
    area_list.sort(key=lambda x: x[0])
    lines = area_list[-n:]
    return [line[1] for line in lines]

"""
def remake(x):
    b = cv2.getTrackbarPos('B', 'thresh')
    if b % 2 != 1:
        b = b+1
        cv2.setTrackbarPos('B', 'thresh', b)
    thresh = cv2.adaptiveThreshold(adjusted_src, 255, 0, 1, b, 2)

    cv2.imshow('thresh', thresh)
"""

if __name__ == '__main__':
    main()
