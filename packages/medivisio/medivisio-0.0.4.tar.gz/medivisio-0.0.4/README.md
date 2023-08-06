# MediVisio

MediVisio is a Python package designed to facilitate the visualization of 3D DICOM and NII (NIfTI) images. With its intuitive interface and extensive functionality, MediVisio allows users to explore, analyze, and interpret medical imaging data in a convenient and interactive manner.

## Features

- **3D Visualization**: Display DICOM and NII images in a three-dimensional space, enabling a comprehensive view of medical data from various angles and perspectives.
<!-- **Interactive Exploration**: Interact with the 3D images using intuitive navigation controls, such as pan, zoom, and rotate, to examine the data in detail.
- **Multi-Modal Image Support**: MediVisio supports both DICOM (Digital Imaging and Communications in Medicine) and NII (NIfTI) file formats, ensuring compatibility with a wide range of medical imaging data.
- **Cross-Sectional Viewing**: Explore cross-sectional slices of the 3D images along different anatomical planes, providing insights into the internal structures and pathology.
- **Annotations and Measurements**: Annotate regions of interest (ROIs) and perform measurements on the images, enabling quantitative analysis and precise documentation.
- **Customizable Visualizations**: Adjust the visualization settings, such as colormap, opacity, and windowing, to enhance the visual representation and highlight specific features within the images.
- **Integration with Jupyter Notebook**: Utilize MediVisio seamlessly within Jupyter Notebook for interactive data exploration, analysis, and reporting.
-->
## Installation

You can easily install MediVisio using pip, as shown below:

```bash
pip install medivisio


## Getting Started
Please note that MediVisio requires a Python environment with the necessary dependencies, such as NumPy, Matplotlib, and
PyDICOM, Nibabel. 
To get started with MediVisio, you can refer to the provided examples and documentation.

### Usecase 
Data directory path
Patients
    |--PatientID
	|--DICOM
	    |--N 2D Slices
	|--NII
	    |--N 2D Slices or 3D Tensor

'''python
"""src_dir: Patients
img_type: "DICOM" or "NII"
img_label: "DICOM_Labels" or "NII_Labels"
"""
import MediVisio
#Deafault arguments 
#alpha = 0.99, applymask = True 
medivisio = MediVisio(src_dir, img_type, img_label)
'''

Reads and Plots 3D Data. You can scroll slices using your mouse. The first slice shown is the middle slice
'''python
medivisio.read_data()

'''
