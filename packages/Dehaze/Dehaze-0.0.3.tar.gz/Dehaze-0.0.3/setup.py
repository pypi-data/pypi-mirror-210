from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Dehaze',
    version='0.0.3',
    description='A Haze remover using Dark Channel Prior',
    author= 'Paramjit Singh',
    url = 'https://github.com/parmishh',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['Dehazer', 'single image dehazer', 'image-dehazer', 'Dark Channel Prior', 'Foggremover','defogging'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Dehaze'],
    package_dir={'':'src'},
    install_requires = [
        'image_dehazer',
        'Pillow',
        'numpy',
        'opencv-python'
        

    ]
)