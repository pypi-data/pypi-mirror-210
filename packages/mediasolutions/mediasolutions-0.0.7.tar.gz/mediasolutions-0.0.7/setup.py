from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.7'
DESCRIPTION = 'A ML Library'

# Setting up
setup(
    name="mediasolutions",
    version=VERSION,
    author="Jaswanth",
    author_email="jaswanthmadiya@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['opencv-python', 'pyautogui'],
    keywords=['python', 'mediapipe'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)