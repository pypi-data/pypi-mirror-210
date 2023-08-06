from tkinter import *
from unittest import TestCase

from basefunctions import PROCESS_IMAGE
from leaf_area_calculator_gui import LeafAreaCalculatorGUI


class TestLeafAreaCalculatorGUI(TestCase):

    def test_display_result(self):
        # print('Finding: ',)
        root = Tk()
        root.title('Leaf Area Calculator')
        root.geometry("820x500")
        root.resizable(False, False)
        leaf_compute = LeafAreaCalculatorGUI(root)
        leaf_compute.number_of_images = 1
        leaf_compute.default_image_path = 'limited_test_images/'
        # filedialog.askdirectory(initialdir=leaf_compute.default_image_path)
        leaf_compute.current_image_name = 'SF17-BE-p0019-r1_IMG_7005.JPG'
        leaf_compute.process_image('SF17-BE-p0019-r1_IMG_7005.JPG')
        analysis_info = PROCESS_IMAGE([leaf_compute.current_image_name], leaf_compute.default_image_path)
        leaf_compute.area_green_leaf = round(analysis_info[1], 2)
        self.assertAlmostEqual(leaf_compute.area_green_leaf, 34.53)

        leaf_compute.current_image_name = 'SF17-BE-p0047-r3_IMG_7919.JPG'
        leaf_compute.process_image('SF17-BE-p0047-r3_IMG_7919.JPG')
        analysis_info = PROCESS_IMAGE([leaf_compute.current_image_name], leaf_compute.default_image_path)
        leaf_compute.area_green_leaf = round(analysis_info[1], 2)
        self.assertAlmostEqual(leaf_compute.area_green_leaf, 6.25)
        # self.fail()