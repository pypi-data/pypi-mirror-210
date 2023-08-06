from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyleafarea',
    version='2.3.1',
    packages=['pyleaf'],
    url='',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'tensorflow>=2.2.0',
        'tensorboard>=2.2.0',
        'keras-preprocessing',
        'absl-py',
        'setuptools',
        'pandas',
        'Pillow',
        'opt_einsum',
        'astunparse',
        'protobuf',
        'pyzbar',
        'pyasn1',
        'opencv-python'
    ],
    tests_require=["pytest"],
    include_package_data=True,
    author='Vishal Sonawane, Balasaheb Sonawane, Joseph Crawford',
    author_email='vishalsonawane1515@gmail.com, balasahebsonawane@gmail.com, joseph.crawford@wsu.edu',
    description='Automated Leaf Area Calculator Using Tkinter and Deep Learning Image Classification Model.'
)
