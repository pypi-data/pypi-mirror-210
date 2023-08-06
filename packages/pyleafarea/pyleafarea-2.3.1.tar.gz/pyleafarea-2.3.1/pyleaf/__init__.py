from tkinter import *
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.insert(0,file_dir)
from .leaf_area_calculator_gui import LeafAreaCalculatorGUI

root = Tk()
root.title('Leaf Area Calculator')
root.geometry("820x500")
root.resizable(False, False)
leaf_compute = LeafAreaCalculatorGUI(root)

root.mainloop()
