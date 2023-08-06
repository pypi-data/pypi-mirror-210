"""
### PyConvertAPI Image Converter

A simple image converter using the ConvertAPI API

ConvertAPI is a simple API that converts files from one format to another. 
It supports over 200 different conversion types, including PDF to Word, JPG to PDF, and many more. 
This package makes it easy to use ConvertAPI in your Python projects.

#### LICENSE: MIT License
"""
__all__ = ['ConvertAPIImageConverter']
__version__ = '0.0.1'
__date__ = ''
__author__ = 'ti-oluwa'
__author_email__ = 'tioluwa.dev@gmail.com'
__description__ = 'A simple image converter using the ConvertAPI API'
__license__ = 'MIT'
__url__ = ''
__title__ = 'convertapi-image-converter'
__keywords__ = 'convertapi image converter'

# Make sure to have `convertapi` installed
# RUN: pip install convertapi
# Create a free account on https://www.convertapi.com/
# Get your convertapi secret key from https://www.convertapi.com/a
from .image_converter import ConvertAPIImageConverter

PyImageConverter = ConvertAPIImageConverter
