import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from PIL import Image, ImageOps, ImageTk, ImageFilter
from tkinter import ttk
import numpy as np
import cv2
import matplotlib.pyplot as plt
import json
import os

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

root = tk.Tk()
root.geometry("1000x800")
root.title("Read RAW image  Tool - IQ")
root.config(bg="white")

pen_color = "black"
pen_size = 5
file_path = ""
canvas_width=750
canvas_height=600
rect_id = None
x1=0
x2=0
y1=0
y2=0

global image1
global img1
global roi
global filename
global filename_image
global image2

global Image_width
global Image_height
global Image_bit_depth
global Endian_type
global Header

def read_image() :
    global file_path
    global img1
    global image1
    global image2
    global rect_id
    global scale_factor_width
    global scale_factor_height
    global image_raw
    global filename_image
    file_path = filedialog.askopenfilename(initialdir= os.getcwd())
    filename_image = os.path.basename(file_path).split('.')[0]
    # image = Image.open(file_path)
    if Image_bit_depth == str('uint32') and Endian_type =='ieee-be':
        raw = np.fromfile(file_path, '>u4')
    elif Image_bit_depth == str('uint16') and Endian_type =='ieee-be':
        raw = np.fromfile(file_path, '>u2')
    elif Image_bit_depth == str('uint32') and Endian_type =='ieee-le':
        raw = np.fromfile(file_path, '<u4')
    elif Image_bit_depth == str('uint16') and Endian_type =='ieee-le':
        raw = np.fromfile(file_path, '<u2')

    width, height = int(Image_width), int(Image_height)

    if Header ==False:
       image_raw = raw[len(raw) - height * width :].reshape(height, width)
       image_raw = image_raw.reshape(height, width)

    elif Header == True:
        image_raw = raw[int(Header_length):len(raw)].reshape(height, width)
        image_raw = image_raw.reshape(height, width)
    if Unmirror == True:
        image_raw = image_raw[:, : :-1]

    linear_raw_scaled_16bit = (image_raw.astype('float') * (65535 / (np.max(image_raw) - 0))).astype('uint16')

    if Bayer_pattern == 'RGGB' or Bayer_pattern =='rggb' :
        img1 = cv2.cvtColor(linear_raw_scaled_16bit, cv2.COLOR_BAYER_BG2BGR)
    elif Bayer_pattern == 'BGGR' or Bayer_pattern =='bggr' :
         img1 = cv2.cvtColor(linear_raw_scaled_16bit, cv2.COLOR_BAYER_RG2BGR)
    elif Bayer_pattern == 'GBRG' or Bayer_pattern == 'gbrg':
        img1 = cv2.cvtColor(linear_raw_scaled_16bit, cv2.COLOR_BAYER_GR2BGR)

    cv2.imwrite(filename_image + 'RawProcessed.tif' , img1)
    image1 = Image.open(filename_image+'RawProcessed.tif')
    scale_factor_width = Image_width/canvas_width
    scale_factor_height = Image_height/canvas_height
    image1 = image1.resize((int(Image_width/scale_factor_width),int(Image_height/scale_factor_height)))

    image2 = ImageTk.PhotoImage(image1)
    canvas.image = image2
    canvas.create_image(0,0, image=image2, anchor="nw")

    rect_id = canvas.create_rectangle(x1, y1, x2, y2, dash=(2, 2), fill='', outline='white')
    return image1,scale_factor_height, scale_factor_width,image_raw,linear_raw_scaled_16bit

def View_Histogram(image1) :

    image = image1
    histogram = image.histogram()
    redh = histogram[0 :256]
    greenh = histogram[256 :512]
    blueh = histogram[512 :768]

    r, g, b = image.split()
    Mean_red = np.mean(r)
    Mean_green = np.mean(g)
    Mean_blue = np.mean(b)

    std_red = np.std(r)
    std_green = np.std(g)
    std_blue = np.std(b)

    plt.Figure(figsize=(30, 15), dpi=100)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

    plt.subplot(311)
    for i in range(0, 256) :
        plt.bar(i, redh[i], color='red', alpha=0.3)

    ax1.plot(np.linspace(0, 256, 256), redh, color='red', label='(Mean,Stdev)=(%0.1f,%0.1f)' % (Mean_red, std_red))
    ax1.legend(loc='upper left')

    plt.subplot(312)
    for i in range(0, 256) :
        plt.bar(i, greenh[i], color='green', alpha=0.3)
    ax2.plot(np.linspace(0, 256, 256), greenh, color='green', label='(Mean,Stdev)=(%0.1f,%0.1f)' % (Mean_green, std_green))
    ax2.legend(loc='upper left')


    plt.subplot(313)
    for i in range(0, 256) :
        plt.bar(i, blueh[i], color='blue', alpha=0.3)

    ax3.plot(np.linspace(0, 256, 256), blueh, color='blue', label='(Mean,Stdev)=(%0.1f,%0.1f)' % (Mean_blue, std_blue))
    ax3.legend(loc='upper left')
    plt.show()


# button that would display the plot

def Select_ROI(img1,scale_factor_height,scale_factor_width) :
    global image1
    global roi

    global x1,y1,x2,y2
    imCrop1 = img1[int((y1)*scale_factor_width) :int((y2)*scale_factor_width), int((x1)*scale_factor_height) :int((x2)* scale_factor_height)]
    imCrop_8bit = (imCrop1.astype('float') * (255/(np.max(imCrop1)))).astype('uint8')

    roi= (int((x1)*scale_factor_height) ,int((y1)*scale_factor_width) ,int((x2)* scale_factor_height),int((y2)*scale_factor_width))

    if len(imCrop1) > 0 :
       image1 = Image.fromarray(cv2.cvtColor(imCrop_8bit, cv2.COLOR_BGR2RGB))

    top = tk.Toplevel(root)
    top.geometry("500x150")
    top.title("Selected ROI: (%d, %d, %d, %d)" % roi)
    img = ImageTk.PhotoImage(image1)
    label = tk.Label(top,image = img).pack()
    label.draw()

def read_sensor_config(filename):
    global Image_bit_depth
    global Image_height
    global Image_width
    global Bayer_pattern
    global Endian_type
    global Header
    global Header_length
    global Unmirror
    with open(filename) as fp :
        sensor_config_data = json.load(fp)
    
    Sensor = sensor_config_data['sensor']
    Bayer_pattern = sensor_config_data['bayer_order']
    Image_width = sensor_config_data['cols']
    Image_height = sensor_config_data['rows']
    Image_bit_depth = sensor_config_data['data_format']
    Endian_type = sensor_config_data['endian_type']
    Header = sensor_config_data['header']
    Header_length = sensor_config_data['header_length']
    Unmirror = sensor_config_data['unmirror']
    textbox_image_bit_depth.insert("3.0", '%s' % Image_bit_depth)
    textbox_image_width.insert("3.0", '%s' % Image_width)
    textbox_image_height.insert("3.0", '%s' % Image_height)
    textbox_image_bayer.insert("3.0", '%s' % Bayer_pattern)
    textbox_image_sensor.insert("3.0", '%s' % Sensor)
    return Image_bit_depth, Image_height, Image_width, Bayer_pattern, Endian_type,Header,Sensor,Header_length,Unmirror

def ROI(event) :
    global x1
    global y1

    x1, y1 = event.x, event.y

def Update_ROI(event):
    global rect_id
    global x1, x2, y1, y2

    x2, y2 = event.x, event.y

    canvas.coords(rect_id, x1, y1, x2, y2)

def clear_canvas() :
    canvas.delete("all")
    '''
    textbox_image_bit_depth.delete(1.0,tk.END)
    textbox_image_width.delete(1.0,tk.END)
    textbox_image_height.delete(1.0,tk.END)
    textbox_image_bayer.delete(1.0,tk.END)
    '''

def select_file():
    global filename
    filetypes = (
        ('text files', '*.json'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open Sensor config file',
        initialdir= os.getcwd(),
        filetypes=filetypes)

    showinfo(
        title='Selected File',
        message=filename
    )
    textbox_image_bit_depth.delete(1.0,tk.END)
    textbox_image_width.delete(1.0,tk.END)
    textbox_image_height.delete(1.0,tk.END)
    textbox_image_bayer.delete(1.0,tk.END)
    textbox_image_sensor.delete(1.0,tk.END)
    read_sensor_config(filename)

def Bit_shift_right(val):
    global rect_id2
    raw = np.clip(np.right_shift(image_raw,int(val)), 0, 255).astype('uint8')

    if Bayer_pattern == 'RGGB' or Bayer_pattern == 'rggb' :
        img2 = cv2.cvtColor(raw, cv2.COLOR_BAYER_BG2BGR)
    elif Bayer_pattern == 'BGGR' or Bayer_pattern == 'bggr' :
        img2 = cv2.cvtColor(raw, cv2.COLOR_BAYER_RG2BGR)
    elif Bayer_pattern == 'GBRG' or Bayer_pattern == 'gbrg' :
        img2 = cv2.cvtColor(raw, cv2.COLOR_BAYER_GR2BGR)

    cv2.imwrite(filename_image+str(val)+'bitshift.tif', img2)
    fil = filename_image+str(val)+'bitshift.tif'
    image2 = Image.open(fil)
    scale_factor_width = Image_width / canvas_width
    scale_factor_height = Image_height / canvas_height
    image2 = image2.resize((int(Image_width / scale_factor_width), int(Image_height / scale_factor_height)))
    # canvas.config(width=Image_width/2, height=Image_height/2)
    image3 = ImageTk.PhotoImage(image2)
    canvas.image = image3
    canvas.create_image(0, 0, image=image3, anchor="nw")

    #rect_id2 = canvas.create_rectangle(x1, y1, x2, y2, dash=(4, 4), fill='', outline='white')
    return image3

def View_Raw_Histogram(image_raw):
    image = image_raw.flatten()

    num_bins = int(np.sqrt(len(image)))
    plt.hist(image,num_bins,color='black',alpha=0.5)
    plt.xlabel('Raw pixel values',fontweight="bold")
    plt.ylabel('Frequency',fontweight="bold")

    plt.title('Histogram - Raw Image',fontweight="bold")
    plt.show()

#rect_ROI = tk.Canvas.create_rectangle(x1, y1, x1, y1,dash=(2,2), fill='', outline='black')
left_frame = tk.Frame(root, width=100, height=600, bg="white")
left_frame.pack(side="left", fill="y")

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)

tk.Label(left_frame, text=" Sensor",bg="grey").pack()
textbox_image_sensor= tk.Text(left_frame,height=1, width=10)
textbox_image_sensor.pack(pady=15)

tk.Label(left_frame, text=" Image bit depth",bg="grey").pack()
textbox_image_bit_depth = tk.Text(left_frame,height=1, width=10)
#textbox_image_bit_depth.insert("3.0","")
textbox_image_bit_depth.pack(pady=15)

tk.Label(left_frame, text=" Image Width",bg="grey").pack()
textbox_image_width= tk.Text(left_frame,height=1, width=10)
textbox_image_width.pack(pady=15)


tk.Label(left_frame, text=" Image Height",bg="grey").pack()
textbox_image_height= tk.Text(left_frame,height=1, width=10)
textbox_image_height.pack(pady=15)

tk.Label(left_frame, text=" Debayer pattern",bg="grey").pack()
textbox_image_bayer= tk.Text(left_frame,height=1, width=10)
textbox_image_bayer.pack(pady=15)
# canvas_left_frame = tk.Canvas.

# open button
Sensor_Config_button = tk.Button(left_frame,text='Load Sensor config',command=select_file,bg="#9bcdff")
#Sensor_Config_button.place(x=400, y=20)
Sensor_Config_button.pack(padx=25, pady=10)

image_button = tk.Button(left_frame, text="Add Image",  command=read_image, bg="#9bcdff")
image_button.pack( padx=15, pady=10)

image_button = tk.Button(left_frame, text="Select ROI", command=lambda: Select_ROI(img1,scale_factor_width,scale_factor_height), bg="#9bcdff")
image_button.pack( padx=15, pady=10)

clear_button = tk.Button(left_frame, text="Clear", command=clear_canvas, bg="#FF9797")

w2 = tk.Scale(left_frame, from_=0, to=16,command=Bit_shift_right, orient='horizontal',label='Bit Shift',bg="#9bcdff")
w2.pack()

plot_button = tk.Button(master=root, command=lambda:View_Histogram(image1), height=2, width=20, text=" View RGB Histogram",bg="#9bcdff")
plot_button.pack()
#plot_button.place(x=300,y=1)

HistRaw_plot_button = tk.Button(master=left_frame, command=lambda:View_Raw_Histogram(image_raw), height=2, width=20, text=" View Raw Histogram",bg="#9bcdff")
HistRaw_plot_button.pack(padx=25,pady=10)
#HistRaw_plot_button.place(x=700, y=3)

clear_button.pack(pady=10)

canvas.pack()

canvas.bind('<Button-1>', ROI)
canvas.bind('<B1-Motion>', Update_ROI)

root.mainloop()
