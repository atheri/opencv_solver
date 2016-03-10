import sys
import cv2
import numpy as np
import itertools

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
    adjusted_src = np.uint8(cv2.normalize(div, div, 0, 255, cv2.NORM_MINMAX)) # Turn color values back to 0-255 from floats

    # Threshold to binary image to find contours
    thresh = cv2.adaptiveThreshold(adjusted_src, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 2)
    _, contours, hier = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
    _, cnts_x, hier = cv2.findContours(threshx, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    _, cnts_y, hier = cv2.findContours(threshy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
   

    lines_x = find_n_largest_contours(10, cnts_x)
    lines_y = find_n_largest_contours(10, cnts_y)
    
    line_img_x = np.zeros((img.shape), np.uint8)
    line_img_y = np.zeros((img.shape), np.uint8)
    for line in lines_x:
        cv2.drawContours(line_img_x,[line],0,(255,255,255),-1)
    for line in lines_y:
        cv2.drawContours(line_img_y,[line],0,(255,255,255),-1)

    intersections = cv2.bitwise_and(line_img_x, line_img_y)
    intersections = cv2.cvtColor(intersections, cv2.COLOR_RGB2GRAY) # Grayscale

    _, cnts_inter, hier = cv2.findContours(intersections, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    centroids = []
    for i, cnt in enumerate(cnts_inter):
        mom = cv2.moments(cnt)
        x = int(mom['m10']/mom['m00'])
        y = int(mom['m01']/mom['m00'])
        
        centroids.append((x,y))

    c = np.array(centroids, dtype = np.float32)
    c2 = c[np.argsort(c[:,1])]

    b = np.vstack([c2[i*10:(i+1)*10][np.argsort(c2[i*10:(i+1)*10,0])] for i in range(10)])
    bm = b.reshape((10,10,2))
    
    """ Printing centroid numbers on image
    flat = bm.flatten()
    for i in range(0,len(flat),2):
        x = flat[i]
        y = flat[i+1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(int(i/2)), (x,y), font, 1, (255,0,0))
        cv2.circle(img, (x,y), 4, (0,255,0), -1)
    """ 
    
    # Adjusted (not blurred) original, output
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Grayscale
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)) 
    close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    div = np.float32(gray)/close
    adjusted_orig = np.uint8(cv2.normalize(div, div, 0, 255, cv2.NORM_MINMAX))

    output = np.zeros((450,450), np.uint8)
    for i, j in enumerate(b):
        r = int(i/10)
        c = i%10

        if r != 9 and c != 9:
            src = bm[r:r+2, c:c+2, :].reshape((4,2))
            dst = np.array([[c*50    ,r*50],
                            [(c+1)*50,r*50],
                            [c*50    ,(r+1)*50],
                            [(c+1)*50,(r+1)*50]], np.float32)
            retval = cv2.getPerspectiveTransform(src, dst)
            warp = cv2.warpPerspective(div, retval, (450,450))
            output[r*50:(r+1)*50 , c*50:(c+1)*50] = warp[r*50:(r+1)*50 , c*50:(c+1)*50].copy()

    # Digit recognizer
    digit_img = cv2.imread('digits.png')
    digit_gray = cv2.cvtColor(digit_img, cv2.COLOR_BGR2GRAY)

    # Split image to 5500 cells, 20x20 each
    cells = [np.hsplit(row,100) for row in np.vsplit(digit_gray,55)]
    cells = np.array(cells)

    # Prepare train_data and
    train = cells[:,:100].reshape(-1,400).astype(np.float32)
    
    # Labels
    k = list(range(10))
    k.append(-1)
    train_labels = np.repeat(k,500)[:,np.newaxis]

    # KNN
    knn = cv2.ml.KNearest_create()
    knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)

    # Feed image
    _, output_thresh = cv2.threshold(output, 200, 255, cv2.THRESH_BINARY_INV)
    output_resize = cv2.resize(output_thresh, (180,180), interpolation=cv2.INTER_AREA)
    sudoku_cells = [np.hsplit(row,9) for row in np.vsplit(output_resize,9)]
    sudoku_cells = np.array(sudoku_cells)
    for i in range(9):
        for j in range(9):
            sudoku_cells[i][j] = cv2.rectangle(sudoku_cells[i][j], (0,0), (19,19), 0, 3)

    cv2.imshow('03', sudoku_cells[0][3])
    sudoku_cells = sudoku_cells[:,:].reshape(-1,400).astype(np.float32)
    
    cv2.imshow('output_reize', output_resize)

    # Test
    """
    nine = cv2.imread('9.jpg')
    nine_g = cv2.cvtColor(nine, cv2.COLOR_BGR2GRAY)
    _, nine1 = cv2.threshold(nine_g, 200, 255, cv2.THRESH_BINARY_INV)
    
    cv2.imshow('before', nine1)
    nine1 = cv2.resize(nine1, (20,20), interpolation=cv2.INTER_AREA)
    cv2.imshow('after', nine1)
    
    nine1 = np.array(nine1).reshape(-1,400).astype(np.float32)
    """

    ret,result,neighbours,dist = knn.findNearest(sudoku_cells,k=21)


    result = result.reshape(9,9)
    print_board(result)

    cv2.imshow('Original', img)
    cv2.imshow('Output', output)
    
    cv2.waitKey(0)              # Waits for any keypress
    cv2.destroyAllWindows()               

def find_n_largest_contours(n, contours):
    area_list = [(cv2.contourArea(cnt), cnt) for cnt in contours]
    area_list.sort(key=lambda x: x[0])
    lines = area_list[-n:]
    return [line[1] for line in lines]

def print_board(board):
    flat = board.flatten()
    flat = [0 if x == -1 else int(x) for x in flat]
    
    flat = [flat[i:i+3] for i in range(0, len(flat), 3)]
    flat = [flat[i:i+3] for i in range(0, len(flat), 3)]

    for i, row in enumerate(flat):
        if i%3 == 0:
            print('-'*25)
        print('|',end=" ")
        for subrow in row:
            for num in subrow:
                print(num,end=" ")
            print('|',end=" ")
        print()
    print('-'*25)

if __name__ == '__main__':
    main()
