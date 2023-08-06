from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
        name = 'comicapi',
        version = '3.0.0',
        description = 'Comic archive (cbr/cbz/cbt) and metadata utilities. Extracted from the comictagger project.',
        author = 'Iris W',
        long_description = long_description, 
        long_description_content_type = 'text/markdown',
        maintainer = "@OzzieIsaacs",
        packages = ['comicapi'],
        install_requires = ['natsort>=8.1.0', "pillow>=4.3.0", "pycountry>=20.7.3", "py7zr>=0.20.0"],
        extras_require = {
            'CBR': ['rarfile>=0.3.2']
        },
        python_requires = '>=3.0.0',
        url = 'https://github.com/OzzieIsaacs/comicapi',
        classifiers = [
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                'License :: OSI Approved :: Apache Software License',
                "Operating System :: OS Independent",
                "Topic :: Utilities"
        ]
)
