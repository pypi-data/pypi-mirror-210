from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='medivisio',
    version='0.0.4',
    author='Dr. Shakeel Ahmad Sheikh',
    description='This script helps to visualise 3D medical images of type DICOM and NII',
    py_modules=["__init__", "medivisio"],
    package_dir={'': 'src'},
    #packages=find_packages(),
    install_requires=[
	'numpy',
	'pydicom',
	'matplotlib',
	'nibabel',

   ],

   long_description=open('README.md').read(),
   long_description_content_type='text/markdown',

   classifiers=[
	"Programming Language :: Python :: 3.11",
]
)
