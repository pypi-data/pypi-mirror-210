from os.path import relpath
from tkinter import *
from tkinter import filedialog
from tkinter import ttk, messagebox

from PIL import ImageTk
from ReadBarcodes import getBarcode
# CHange to local .basefunctions during deployment
from basefunctions import *


class LeafAreaCalculatorGUI:
    """
    Class LeafAreaCalculatorGUI is a Tkinter GUI manager, that is responsible for interacting with the user
    and displaying results.
    The backend application is a convulutional neural network that is trained with green, red and other colors,
    to generate a robust and reliable classifier that can detect green leaf within a given image in varying light conditions and leaf shades,
    and computes the area of the green leaf with respect to a fixed red square of 4 cm^2.

    GUI includes two preview panes:
    left pane is the original window pane, that displays the original image and the name of image.
    right pane is the updated window pane, that displays the resultant analyzd image from classifier.

    Under the left pane is a navigation bar, with which user can switch left or right through multiple images. This option is diabled if user is working on only one image.

    """
    IMAGE_HEIGHT = 300
    IMAGE_WIDTH = 300

    def __init__(self, root):
        """
        LeafAreaCalculatorGUI constructor accepts the root as Tkinter main window.

        :param root: Tkinter Main Window
        Sets parameters and configurations to default.
        :type root: Tk()
        """
        self.root = root
        self.current_page = IntVar()
        self.stored_area_dict = dict()
        self.stored_barcode_dict = dict()

        self.current_image_name = None
        self.font = 'Helvetica'
        self.font_size = 9
        self.font_param = (self.font, self.font_size, 'bold')

        self.process_clicked = False
        self.all_results = list()

        self.default_image_path = os.path.dirname(__file__)
        self.default_save_path = os.path.join(os.path.dirname(__file__), 'saved_images/')
        self.was_default_set = False

        self.set_grid()
        self.set_menus()

        self.area_red_square = int(self.set_red_square.get())

    def set_menus(self):
        """
        Function set_menus: Sets the Menu tool bar for the application.
        User can select default image directory and perform batch process usind File and Tools menu options.
        """
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Set Default Image Folder", command=self.setDefaultImageLocation)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.destroy)

        toolsmenu = Menu(menu)
        menu.add_cascade(label='Tools', menu=toolsmenu)
        toolsmenu.add_command(label='Batch Process Images', command=self.process_all)
        toolsmenu.add_separator()
        toolsmenu.add_command(label='ReTrain Model', command=self.retrain_model)

        toolsmenu.add_separator()
        toolsmenu.add_command(label='View Recent Result', command=self.view_results)
        toolsmenu.add_command(label='Save Recent Results As CSV', command=self.save_results)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.About)
        helpmenu.add_command(label="Documentation", command=self.documentation)

    def retrain_model_run(self):
        """
        Function retrain_model_run: Displays model training status to user.
        A window is popped up with message: Model Training In Progress. Window is closed when model training is complete.
        """
        if (RETRAIN_MODEL_FROM_SCRATCH()):
            self.retrain_window.after(5000, self.retrain_window.destroy)
            self.my_frame.update_idletasks()

    def retrain_model(self):
        """
        Function retrain_model: Performs re-training of the classifier on user input from Tools->Retrain model.
        Note: User should retrain the model only if training images have changed, or classification model seems corrupt.
        """
        self.retrain_window = Toplevel(self.my_frame)

        label_ = Label(self.retrain_window, text='Model Training In Progress..')
        label_.pack()

        self.retrain_window.after(1000, self.retrain_model_run)

    def setDefaultImageLocation(self):
        """
        Function setDefaultImageLocation: Sets the default image directory to find images for analysis.
        """
        self.was_default_set = True
        self.default_image_path = filedialog.askdirectory(initialdir=self.default_image_path)

    def About(self):
        """
        Displays the File->About pop up box.
        """
        messagebox.showinfo("pyleaf", "pyleaf:\n Simplified Leaf Area Analysis Using Machine Learning")

    def display_this_image(self, passed_image):
        """
        Function that collects a passed image from disk and displays in the original preview window and updated result window.

        :param passed_image: The image name to be fetched from default_image_path and default_save_path
        """
        originalonly = not self.process_clicked

        self.label_image_name['text'] = passed_image
        self.show_barcode['text'] = self.stored_barcode_dict.get(passed_image, getBarcode(
            os.path.join(self.default_image_path, passed_image)))

        # Original Preview Pane
        image = Image.open(os.path.join(self.default_image_path, passed_image))
        image = image.resize((LeafAreaCalculatorGUI.IMAGE_WIDTH, LeafAreaCalculatorGUI.IMAGE_HEIGHT), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.label1.config(image=photo)
        self.label1.image = photo  # keep a reference!

        if (not originalonly):
            # Processed Preview Pane
            image = Image.open(self.default_save_path + passed_image)
        image = image.resize((LeafAreaCalculatorGUI.IMAGE_WIDTH, LeafAreaCalculatorGUI.IMAGE_HEIGHT),
                             Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.label2.config(image=photo)
        self.label2.image = photo  # keep a reference!

    def display_left(self):
        """
        The Left Arrow button of the navigation control under original preview pane.
        Disabled if navigation reaches 1/N , Enabled otherwise.
        """
        # print('Left')
        self.current_page.set(self.current_page.get() - 1)
        # print('Current page: ', self.current_page.get())
        self.display_this_image(self.list_[self.current_page.get()])
        self.page_label['text'] = '{}/{}'.format(self.current_page.get() + 1, self.number_of_images)

        if (self.process_clicked):
            self.display_result(self.stored_area_dict[self.list_[self.current_page.get()]])

        if (self.current_page.get() - 1 < 0):
            self.button_left['state'] = DISABLED
            self.button_right['state'] = ACTIVE
            self.current_page.set(0)
        else:
            self.button_left['state'] = ACTIVE
            self.button_right['state'] = ACTIVE

    def display_right(self):
        """
        The Right Arrow button of the navigation control under original preview pane.
        Disabled if navigation reaches N/N , Enabled otherwise.
        """

        # print('Right')
        self.current_page.set(self.current_page.get() + 1)
        # print('Current page: ', self.current_page.get())
        self.display_this_image(self.list_[self.current_page.get()])
        self.page_label['text'] = '{}/{}'.format(self.current_page.get() + 1, self.number_of_images)

        if (self.process_clicked):
            self.display_result(self.stored_area_dict[self.list_[self.current_page.get()]])
        if (self.current_page.get() + 1 > (self.number_of_images - 1)):
            self.button_right['state'] = DISABLED
            self.button_left['state'] = ACTIVE
            self.current_page.set(self.number_of_images - 1)
        else:
            self.button_left['state'] = ACTIVE
            self.button_right['state'] = ACTIVE

    def change_result_preview(self, every):
        """
        Update the result window pane with the passed image.

        :param every: name of the image file to load.
        :type every: string
        """
        # print('Evrry: ', every)
        analysis_info = PROCESS_IMAGE([every], self.default_image_path, self.area_red_square)
        self.area_green_leaf = analysis_info[1]

        # print('EVery: ', every)
        self.stored_area_dict[every] = round(self.area_green_leaf, 2)

        self.stored_barcode_dict[every] = getBarcode(os.path.join(self.default_image_path, every))

        analysis_info[1] = round(analysis_info[1], 2)
        analysis_info.append(self.stored_barcode_dict[every])
        self.all_results.append(analysis_info)

        # Now that image analysis is complete, load the transformed image to Label2
        image = Image.open(self.default_save_path + every)
        image = image.resize((LeafAreaCalculatorGUI.IMAGE_WIDTH, LeafAreaCalculatorGUI.IMAGE_HEIGHT), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.label2.config(image=photo)
        self.label2.image = photo  # keep a reference!

    def update_original_preview(self, photo):
        """
        Update the original window pane with the passed image.

        :param photo: name of the image file to load.
        :type photo: string
        """
        self.label1.config(image=photo)
        self.label1.image = photo  # keep a reference!

        self.label_image_name['text'] = self.current_image_name
        if (self.number_of_images == 1):
            self.page_label['text'] = '1/1'
        else:
            self.page_label['text'] = '{}/{}'.format(self.number_of_images, self.number_of_images)
            self.button_left['state'] = NORMAL
            self.button_right['state'] = NORMAL

    def display_result(self, area=None):
        """
        Displays the area in cm^2 with an option to switch to mm^2 by clicking on the numerical result displayed.

        :param area: The area to display in the 'Leaf Area:'  field.
        :type area: float, 2 bit decimal.
        """
        if (area == None):
            area = round(self.area_green_leaf, 2)

        self.area_green_leaf = area
        self.show_area.config(text='{} cm\u00b2'.format(area))

        # print('Seting a: ', self.a.get())
        self.a.set(self.a.get() + 1)

        if self.a.get() >= self.number_of_images and self.a.get() > 1:
            try:
                self.progress.update_idletasks()
                self.newwin.after(5000, self.newwin.destroy)
                self.root.update_idletasks()

                # Save results
                dataFrameMeasure = pd.DataFrame(self.all_results,
                                                columns=['Sample', 'Area', 'Red Pixels', 'Red Ratio', 'Green Pixels',
                                                         'Dimensions', 'BarCode'])
                dataFrameMeasure.to_csv(os.path.join(os.path.dirname(__file__), 'storedMeasuredValues.csv'))
            except Exception:
                pass

    def documentation(self):
        import webbrowser
        webbrowser.open('file://' + os.path.realpath(os.path.join(os.path.dirname(__file__), 'pyleaf.pdf')))

    def view_results(self):
        '''
        Function to display the recently saved results in a new window.
        Displays results available in storedMeasuredValues.csv data file.
        '''

        self.result_window = Toplevel(self.root)
        storedAreas = pd.read_csv(os.path.join(os.path.dirname(__file__), 'storedMeasuredValues.csv'))

        self.result_frame = Frame(self.result_window)
        self.result_frame.grid(row=0, columnspan=storedAreas.shape[1] + 2)

        Label(self.result_frame, text="Leaf Area Results", font=("Arial", 24), relief='sunken').grid(row=0,
                                                                                                     columnspan=
                                                                                                     storedAreas.shape[
                                                                                                         1] + 2)

        for col, every_col in enumerate(['Sample', 'Area']):
            Label(self.result_frame, text=str(every_col), font=self.font_param, relief='flat', fg='green').grid(row=1,
                                                                                                                column=col + 1)

        for row, (index, every_row) in enumerate(storedAreas.iterrows()):
            for col, every_col in enumerate(['Sample', 'Area']):
                label_ = Label(self.result_frame, text=str(every_row[every_col]), font=self.font_param, relief='flat')
                label_.grid(row=row + 2, column=col + 1, columnspan=1)

        Label(self.result_frame, text="", font=("Arial", 30)).grid(row=storedAreas.shape[0] + 2,
                                                                   columnspan=storedAreas.shape[1] + 2)

    def save_results(self):
        '''
        Function to display the save recent results to location of user choise.
        Displays results available in storedMeasuredValues.csv data file.
        '''
        import shutil

        # storedAreas = pd.read_csv(os.path.join(os.path.dirname(__file__), 'storedMeasuredValues.csv'))
        savePath = filedialog.askdirectory(initialdir=self.default_image_path)

        shutil.copy(os.path.join(os.path.dirname(__file__), 'storedMeasuredValues.csv'), savePath)
        messagebox.showinfo("File Saved", "Success:\n Results Location: " + savePath)

    def change_unit(self, event):
        """
        Function that allows the numerical leaf area result to switch between cm^2 and mm^2.
        The result is displayed in Leaf Area label field.

        :param event: Accept the button click event.
        :type event: Tkinter Button Press 1.
        :return: Return 'NA' back if 'NA' is clicked.
        :rtype: int
        """
        is_cm = True if 'cm' in self.show_area['text'] else False

        if ('NA' in self.show_area['text']):
            return 0

        if (not is_cm):
            area = round(self.area_green_leaf, 2)
            self.show_area.config(text='{} cm\u00b2'.format(area))
        else:
            area = round(self.area_green_leaf * 100, 2)
            self.show_area.config(text='{} mm\u00b2'.format(area))

    def new_winF(self):  # new window definition
        """
        Function that creates a progress window to display progress of leaf analysis with multiple images.
        A new window updates the status with analysis of every leaf in the default_image_folder, and closes automatically when program processes all images.

        The window is positioned to be in the centre of the main window.
        """
        window_height = 150
        window_width = 300

        self.newwin = Toplevel(self.my_frame)
        x_cordinate = int((820 / 2) - (window_width / 2))
        y_cordinate = int((500 / 2) - (window_height / 2))

        self.newwin.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        self.progress = ttk.Progressbar(self.newwin, orient=HORIZONTAL, length=100, mode='determinate')
        self.progress.place(x=50, y=50, height=50, width=200)

        self.prog_label = Label(self.newwin, width=15, text='Processing...', font=self.font_param)
        self.prog_label.place(x=50, y=30, height=15, width=200)

    def change_progress(self):
        """
        Update the progress value in the progress window.
        """
        self.newwin.update_idletasks()
        val = int((self.a.get() / self.number_of_images) * 100)
        self.progress['value'] = val
        # print('Getting a: ', self.a.get())
        # print('Val: ', val)
        self.progress.update()

    def process_all(self):
        """
        Function that is triggered when Batch Process feature is activated by user.
        Iterate over all images one by one from the list of images in default_image_path, and update the Leaf Area and preview panes as the results become available.
        While the operation is in progress, new window is popped that displays dynamic progress of task.
        """
        self.process_clicked = True

        self.list_ = list(filter(lambda x: str(x).lower().__contains__('.jp'), os.listdir(self.default_image_path)))
        self.number_of_images = len(self.list_)

        # print('DF: ', self.default_image_path)
        # print('List_: ', self.list_)

        if (self.was_default_set):
            if (self.number_of_images == 1):
                self.button_left['state'] = DISABLED
                self.button_right['state'] = DISABLED
            else:
                self.button_left['state'] = DISABLED
                self.button_right['state'] = DISABLED
                # print('Setting current page..')
                self.current_page.set(self.number_of_images - 1)
                # print(self.current_page)

            for index, every in enumerate(self.list_):
                # Load original picture
                image = Image.open(os.path.join(self.default_image_path, every))
                image = image.resize((LeafAreaCalculatorGUI.IMAGE_WIDTH, LeafAreaCalculatorGUI.IMAGE_HEIGHT),
                                     Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image)

                self.label1.after(500, self.update_original_preview, photo)
                self.current_image_name = every

                self.button_select['state'] = DISABLED
                self.button_area['state'] = NORMAL

            # print('NOI: ', self.number_of_images)
            self.process_image()
        else:
            messagebox.showwarning("Default Path", "Default Image Path was not set. Use File->Set Default Image Folder")

    def process_image(self, every=None):
        """
        Function that accepts only one image name as input, and performs analysis.
        Updates the Leaf Area and preview panes as the result become available. If no input is provides, iteratively processes all images in the global list_ maintained by class as list of all
        images in the default image path.

        :param every: Image name to process
        :type every: string
        """
        self.process_clicked = True
        self.a = IntVar()
        self.a.set(1)

        if (self.number_of_images == 1):
            every = self.current_image_name
            self.label2.after(100, self.change_result_preview, every)
            self.show_area.after(100, self.display_result)
            self.show_barcode.after(100, self.display_barcode, every)
        else:
            self.new_winF()
            for index, every in enumerate(self.list_):
                self.progress.update_idletasks()
                self.progress.after(5000, self.change_progress)
                self.label2.after(5000, self.change_result_preview, every)
                self.show_area.after(5000, self.display_result)
                self.show_barcode.after(100, self.display_barcode, every)

    def display_barcode(self, filename):
        self.barcode = getBarcode(os.path.join(self.default_image_path, filename))
        self.show_barcode.config(text='{}'.format(self.barcode))

    # Ask the user to select a one or more file names.
    def answer(self, x):
        """
        Allows user to select base image path from where all images in that folder can be polled for batch analysis.
        When user selects the default folder through the dialog box, all images in the selected folder are loaded in the original preview pane.

        :param x: Tkinter Instance of main window or root
        :type x: Tk()
        """
        self.my_frame.update_idletasks()
        # Build a list of tuples for each file type the file dialog should display
        my_filetypes = [('all files', '.*'), ('image files', '.JPG')]

        self.list_ = filedialog.askopenfilenames(parent=x, initialdir=self.default_image_path,
                                                 title="Please select one or more files:",
                                                 filetypes=my_filetypes)

        self.default_image_path = os.path.dirname(self.list_[0])
        self.list_ = [relpath(x, self.default_image_path) for x in self.list_]
        # print(list(self.list_))

        self.number_of_images = len(self.list_)
        # print('NOI: ', self.number_of_images)

        if (self.number_of_images == 1):
            self.button_left['state'] = DISABLED
            self.button_right['state'] = DISABLED
        else:
            # print('Setting current page..')
            self.current_page.set(self.number_of_images - 1)
            # print(self.current_page)

        for index, every in enumerate(self.list_):
            # Load original picture
            image = Image.open(os.path.join(self.default_image_path, every))
            image = image.resize((LeafAreaCalculatorGUI.IMAGE_WIDTH, LeafAreaCalculatorGUI.IMAGE_HEIGHT),
                                 Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)

            self.label1.after(500, self.update_original_preview, photo)
            self.current_image_name = every

            self.button_select['state'] = DISABLED
            self.button_area['state'] = NORMAL
            self.button_right['state'] = DISABLED

        self.my_frame.update_idletasks()
        self.display_this_image(self.current_image_name)

    def reset_workspace(self):
        """
        Resets the workspace to defaults. This provides a fresh GUI configuration to user.
        Clears all images in the default save path directory.
        """
        self.set_grid()
        self.stored_area_dict = dict()
        for every in os.listdir(self.default_save_path):
            os.remove(os.path.join(self.default_save_path, every))

        self.process_clicked = False

    def disable_red_button(self, event):
        """
        Disable the Set Red Button.
        """
        self.set_red_label['state'] = DISABLED
        self.set_red_square['state'] = DISABLED

        self.area_red_square = int(self.set_red_square.get())

    def set_grid(self):
        """
        Creates a blueprint of the various GUI elements in a window of size 820x500.
        Tkinter Frame is creates and place geometry manager is used to position the elements exactly where desired.
        Positions labels ans preview panes in the desired locations, as per the GUI guidelines of this project.
        """
        self.my_frame = Frame(self.root)
        self.my_frame.place(x=0, y=0, height=500, width=820)

        image = Image.open(os.path.join(os.path.dirname(__file__), 'leaf_top.png'))
        image = image.resize((40, 50), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.label_leaf_top = Label(self.my_frame, image=photo,
                                    height=40, width=50,
                                    font=self.font_param)
        self.label_leaf_top.image = photo
        self.label_leaf_top.place(x=0, y=0, height=40, width=50)

        self.label1 = Label(self.my_frame, text='Please upload an image.',
                            height=LeafAreaCalculatorGUI.IMAGE_HEIGHT, width=LeafAreaCalculatorGUI.IMAGE_WIDTH,
                            font=self.font_param)
        self.label1.image = photo  # keep a reference!
        self.label1.place(x=20, y=50, height=300, width=300)

        self.label2 = Label(self.my_frame, text='Processed Image \nPreview appears here.',
                            height=LeafAreaCalculatorGUI.IMAGE_HEIGHT,
                            font=self.font_param, width=LeafAreaCalculatorGUI.IMAGE_WIDTH)
        self.label2.image = photo  # keep a reference!
        self.label2.place(x=500, y=50, height=300, width=300)

        # Pagination
        self.button_left = Button(self.my_frame, text='<', height=1, width=5,
                                  command=self.display_left, font=self.font_param)
        self.button_left.place(x=20, y=400)

        self.page_label = Label(self.my_frame, text='0/0', font=self.font_param)
        self.page_label.place(x=150, y=400, width=60)

        self.button_right = Button(self.my_frame, text='>', height=1, width=5,
                                   command=self.display_right, font=self.font_param, state=DISABLED)
        self.button_right.place(x=270, y=400)

        self.label_image_name = Label(self.my_frame, text='', font=self.font_param)
        self.label_image_name.place(x=20, y=370, width=300)

        self.button_left['state'] = DISABLED
        self.button_right['state'] = DISABLED

        self.button_select = Button(self.my_frame, text='Select Image(s)', height=1, width=15,
                                    command=lambda x=self.root: self.answer(x), font=self.font_param)
        self.button_select.place(x=350, y=100)

        self.button_area = Button(self.my_frame, text='Compute Leaf Area', height=1, width=15,
                                  command=self.process_image, font=self.font_param)

        self.button_area.place(x=350, y=160)
        self.button_area['state'] = DISABLED

        self.text_area = Label(self.my_frame, text='Leaf Area:', width=30, font=self.font_param)
        self.text_area.place(x=450, y=370)

        self.show_area = Label(self.my_frame, text='NA', width=20, font=self.font_param)
        self.show_area.bind("<Button-1>", self.change_unit)
        self.show_area.place(x=600, y=370)

        self.barcode_label = Label(self.my_frame, text='Barcode ID:', width=30, font=self.font_param)
        self.barcode_label.place(x=450, y=390)

        self.show_barcode = Label(self.my_frame, text='NA', width=20, font=self.font_param)
        self.show_barcode.place(x=600, y=390)

        self.reset_button = Button(self.my_frame, text='Reset Workspace', height=1, width=15,
                                   command=self.reset_workspace,
                                   font=self.font_param)

        self.reset_button.place(x=700, y=20)

        self.set_red_label = Button(self.my_frame, text='Set Red Area:', width=12, font=self.font_param)
        self.set_red_label.bind('<Button-1>', self.disable_red_button)
        self.set_red_label.place(x=500, y=20)
        self.set_red_square = Entry(self.my_frame, width=7, font=self.font_param)
        self.set_red_square.place(x=600, y=20)
        self.set_red_square.insert(0, '{}'.format(4))
        # self.set_red_square.bind("<Return>", evaluate)
        self.set_red_square_cm = Label(self.my_frame, width=3, font=self.font_param, text='cm\u00b2')
        self.set_red_square_cm.place(x=630, y=20)
        self.set_red_square.config(justify=LEFT)
        # self.set_red_square.foc
        # self.set_red_square.insert(10, '{} cm\u00b2'.format(4))
        # entry.bind("<Return>", evaluate)


if __name__ == '__main__':
    root = Tk()
    root.title('Leaf Area Calculator')
    root.geometry("820x500")
    root.resizable(False, False)
    leaf_compute = LeafAreaCalculatorGUI(root)

    # leaf_compute.retrain_model()

    root.mainloop()
