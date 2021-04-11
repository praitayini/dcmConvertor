# dcmConvertor

## Contents

* [Overview](#overview)
* [Setup](#getting-started)
* [Command](#command)
* [Input/Ouput](#arguments-and-io)
* [Options](#options)
* [Discussion](#discussion)

## Overview

* **Summary:** Conversion and handling of DICOM MRI data

* **Script performs:** 
    1. Conversion DICOM to JPEG
    1. Conversion DICOM to NIFTI
    1. Binary thresholding on DICOM
    1. Load DICOM 

## Setup

Running the dcmConvertor.py script requires [inputs](#arguments-and-io) folder that holds all DICOM series, packages: pydicom, opencv-python and tools: dcm2niix.

* **Create Virtual Environment and activate**
```
conda create -n dcm_convertor python=3.8
conda activate dcm_convertor
```
* **Packages required**
```
pip install pydicom
pip install opencv-python
```
* **Tool required**

    follow steps in: https://github.com/rordenlab/dcm2niix#build-command-line-version-with-cmake-linux-macos-windows

* **Clone the repo**
```
git clone https://github.com/praitayini/dcmConvertor.git
cd /path/to/repo/dcmConvertor
```
## Command

    python dcmConvertor.py 
    -d /path/to/dicom 
    [options]
    
## Arguments and I/O

* **Input Directory:** 

  * dicom\series# 

	* \<dcm1\>.dcm 
	* \<dcm2\>.dcm 

	* \<dcmn\>.dcm 


* **Output Directory:** Output folders are created based on the [options](#options)

  * The output jpeg are available in the jpeg folder for each series:

    * jpeg/series#/jpeg files

  * The output nifti are available in the nifti folder for each series:

    * nifti/series#/nifti files

  * The output threshold jpeg and dicom are available in the threshold\_dicom threshold\_jpeg resp. for each series:

    * threshold\_jpeg/series#/jpeg files
    * threshold\_dicom/series#/dicom files

## Options

**--dcm2jpg**

Reads all the dicom files in a series and converts it to jpeg image and saves it in jpeg/series# directory


**--dcm2nifti**

Uses dcm2niix tool to convert the given series to nifti data

**--b\_threshold**

Reads all the dicom files in a series, gets the mean intensity, performs binary thresholding and saves the output in threshold\_dicom/series# and threshold\_jpeg/series#

**--load**

Read dicom and loads it into an array

## Discussion

dcm2niix tool was used for nifti generation as it is widely used and most reliable. The most recent realease is recommended. Loading series can be preformed with nifti images as well using nibabel package. For future development of this work, the script can be made into a pip package.
