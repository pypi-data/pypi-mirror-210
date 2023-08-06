from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='pyleafarea',
    version='2.3',
    packages=['pyleaf'],
    url='',
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
    	'absl-py>=0.7.0',
    	'setuptools>=41.0.0',
    	'keras-preprocessing<1.2,>=1.1.1',
        'numpy<1.19.0,>=1.16.0',
        'pandas>=0.23.0',
        'Pillow>=5.3.0',
        'opt_einsum',
        'astunparse',
        'tensorflow>=2.2.0',
        'tensorboard>=2.2.0',
        'protobuf==3.8.0',
        'pyzbar',
        'pyasn1<0.5.0,>=0.4.6',
        'opencv-python'
        ],
    tests_require=["pytest"],
    include_package_data=True,
    author='Vishal Sonawane, Balasaheb Sonawane, Joseph Crawford',
    author_email='vishalsonawane1515@gmail.com, balasahebsonawane@gmail.com, joseph.crawford@wsu.edu',
    description='Automated Leaf Area Calculator Using Tkinter and Deep Learning Image Classification Model.'
)