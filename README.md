# Read-Raw-image-data
**This  project contains codes to process a raw image file and do basic image processing steps.**
*Read - Raw - image - data* tool is a **tkinter App** to read a  16 bit or 32 bit **.raw image** and convert it to a **RGB image**.
Displays **histogram** of the raw data.
Also can be used to select any given ROI and display *RGB histogram* of the selected region.
There is also bit shift slider enabled that is useful to bring out signals in darker regions of the image.

**How to use the tool:**  

1. **Load main_ReadRaw.py** and click run.
2. Load the json file from the *config_files* folder.
3. Once opened, the parameters of the .raw image will be displayed on the tkinter app window.
4. Click *Add image* button to load the .raw file.
5. RGB image is dsipalyed on the right side of the window.
6. To use the *RGB histogram*, drag the cursor on any desired region of interest and then click *Select ROI* button. 
7. Now press 'RGB histogram' button, and the 8 bit RGB histogram of the seleted ROI will be displayed.
8. To select *bit_shift* operation, slide the *bit_shift* slider and you can see how the intensity of the displayed RGB image varies.

**.....................................................................
Example use cases: ..................................................................................................................**

1. Use X3F_ovt.json file to open sun_1536x1824.raw file.
2. Use SONY_config.json file to open sony_16bit.raw file.
3. You can edit/modify the json file and set your own attributes for opening your .raw images.
