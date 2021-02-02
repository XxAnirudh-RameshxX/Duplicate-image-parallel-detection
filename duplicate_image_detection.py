import tkinter as tk
import cv2
import glob
import time
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor

def filebrowser(ext = '', directory = ''):
    return [f for f in glob.glob(f"{directory}**/*{ext}", recursive=True)]

def serial_duplicate(image_dir, image_name):
    original = cv2.imread(image_name)
    start_time = time.time()
    global duplicates

    for image_ in image_dir:
        try:
            if image_name.replace('\\', '/') != image_.replace('\\', '/'):
                image_to_compare = cv2.imread(image_)
                if original.shape == image_to_compare.shape:
        
                    difference = cv2.subtract(original, image_to_compare)
                    b, g, r = cv2.split(difference)
        
                    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                        print(f'Duplicates Found: {image_} is Duplicate of {image_name}')
                        duplicates.append(image_)
                        
                        sift = cv2.xfeatures2d.SIFT_create()
                        kp_1, desc_1 = sift.detectAndCompute(original, None)
                        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)
        
                        index_params = dict(algorithm=0, trees=5)
                        search_params = dict()
                        flann = cv2.FlannBasedMatcher(index_params, search_params)
        
                        matches = flann.knnMatch(desc_1, desc_2, k=2)
        
                        good_points = []
                        for m, n in matches:
                            if m.distance < 0.6*n.distance:
                                good_points.append(m)
        
                        # Define how similar they are
                        number_keypoints = 0
                        if len(kp_1) <= len(kp_2):
                            number_keypoints = len(kp_1)
                        else:
                            number_keypoints = len(kp_2)
        except Exception as e:
            pass
    
    
    
    print("--- %s seconds ---" % (time.time() - start_time))

def parallel_duplicate(image_, image_name):
    original = cv2.imread(image_name) 
    try:
        if image_name.replace('\\', '/') != image_.replace('\\', '/'):
            global duplicates
            image_to_compare = cv2.imread(image_)
            # print(image_ + ' image read successfully!')
            if original.shape == image_to_compare.shape:
                difference = cv2.subtract(original, image_to_compare)
                b, g, r = cv2.split(difference)
    
                if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                    print(f'Duplicates Found: {image_name} is Duplicate of {image_}')
                    duplicates.append(image_)
    
                    sift = cv2.xfeatures2d.SIFT_create()
                    kp_1, desc_1 = sift.detectAndCompute(original, None)
                    kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)
    
                    index_params = dict(algorithm=0, trees=5)
                    search_params = dict()
                    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
                    matches = flann.knnMatch(desc_1, desc_2, k=2)
    
                    good_points = []
                    for m, n in matches:
                        if m.distance < 0.6*n.distance:
                            good_points.append(m)
    
                    # Define how similar they are
                    number_keypoints = 0
                    if len(kp_1) <= len(kp_2):
                        number_keypoints = len(kp_1)
                    else:
                        number_keypoints = len(kp_2)
    except Exception as e:
        pass

window = tk.Tk()

folderSelected = tk.Label(master = window, text = "Folder selected!")
fileSelected = tk.Label(master = window, text = 'Image selected!')
switch_variable = tk.StringVar(value = 'Serial')

def askDirectory():
    folderSelected.pack_forget()
    directoryName = tk.filedialog.askdirectory()
    global image_dir
    image_dir = filebrowser(ext = '.jpeg', directory = directoryName)
    image_dir += filebrowser(ext='.jpg', directory = directoryName)
    folderSelected.pack()

def openImage():
    fileSelected.pack_forget()
    file = tk.filedialog.askopenfilename()
    global image_name
    image_name = file
    
    fileSelected.pack()

def find_duplicates():
    global count, duplicates
    duplicates = []
    count = 0
    if switch_variable.get() == 'Serial':
        serial_duplicate(image_dir, image_name)
    else:
        start_time = time.time()
        with ThreadPoolExecutor(max_workers = 5) as executor:
            for image_ in image_dir:
                executor.submit(parallel_duplicate, image_, image_name)
        print("--- %s seconds ---" % (time.time() - start_time))
    print('Program Executed Completely and ' + str(len(duplicates)) + ' duplicates found!')

folderSelectFrame = tk.Frame(master = window)
folderSelectFrame.pack()
label = tk.Label(master = folderSelectFrame, text = "Select folder to check in",
                 width = 50)
label.pack(side = tk.LEFT)
folderSelectButton = tk.Button(master = folderSelectFrame, text = 'Open file explorer',
                               command = askDirectory)
folderSelectButton.pack(side = tk.RIGHT)

imageSelectFrame = tk.Frame(master = window)
imageSelectFrame.pack()
label = tk.Label(master = imageSelectFrame, text = "Select image to check duplicates of",
                 width = 50)
label.pack(side = tk.LEFT)
imageSelectButton = tk.Button(master = imageSelectFrame, text = 'Open file explorer',
                              command = openImage)
imageSelectButton.pack(side = tk.RIGHT)


serial = tk.Radiobutton(master = window, text = 'Serial',
                             variable = switch_variable, indicatoron = False,
                             value = 'Serial', width = 10)
parallel = tk.Radiobutton(master = window, text = 'Parallel',
                          variable = switch_variable, indicatoron = False,
                          value = 'Parallel', width = 10)
serial.pack()
parallel.pack()
final_button = tk.Button(master = window, text = 'Find duplicates',
                         command = find_duplicates)
final_button.pack()

window.mainloop()