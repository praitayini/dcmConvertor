import os
import cv2
import glob
import pydicom
import struct
import argparse
import subprocess
import numpy as np

DESCRIPTION = """What is the script doing :
Takes in a DICOM folder with DICOM series
    (Eg DICOM folder sturcture: dicom/37978.000000-T2reg-73187/)
Performs the following operations:
    1.  write the data out as jpeg images
    2.  write DICOM series out in nifti format
    3.  binary thresholding operation to DICOM series and  write out the thresholded volumes in DICOM and jpeg format
    4.  load DICOM series

Examples:
   *Convert DICOM series to JPEG:
        python dcmConvertor.py -d DICOM_DIR --dcm2jpg
   *Convert DICOM series to NIFTI:
        python dcmConvertor.py -d DICOM_DIR --dcm2nifti
   *Binary thresholding on DICOM series:
        python dcmConvertor.py -d DICOM_DIR -t
   *Load DICOM series:
        python dcmConvertor.py -d DICOM_DIR -l
       """

def dcm2jpg(dcm_dir):
    """
    Method to convert dicom to jpeg
    :param dcm_dir: dicom directory 
    """
    print('*****************************************')
    print('*** dcmConvertor: DICOM TO JPEG  *******')
    print('***************************************\n')

    cur_dir = os.getcwd()
    jpeg_dir = os.path.join(cur_dir,'jpeg')
    for series in os.listdir(dcm_dir):
        print('Converting series %s to jpeg' %(series))
        dcm_series = os.path.join(dcm_dir,series)
        dcm_files = [os.path.basename(x) for x in glob.glob(dcm_series + '/*.dcm')]
        jpeg_series = os.path.join(jpeg_dir,series)
        if not os.path.exists(jpeg_series):
            os.makedirs(jpeg_series)
        for f in dcm_files:
            ds = pydicom.dcmread(os.path.join(dcm_series,f)) 
            pixel_array = ds.pixel_array 
            jpeg_file = f.replace('.dcm', '.jpg')
            print('\t -Writing the data %s out to %s' %(f, os.path.join(jpeg_series, jpeg_file)))
            cv2.imwrite(os.path.join(jpeg_series, jpeg_file), pixel_array)

    print('*************************************************')
    print('*** dcmConvertor: FINISHED DICOM TO JPEG  *******')
    print('************************************************\n')

def dcm2nifti(dcm_dir):
    """
    Method to convert dicom to nii
    :param dcm_dir: dicom directory 
    """
    print('*****************************************')
    print('*** dcmConvertor: DICOM TO NIFTI  *******')
    print('***************************************\n')

    cur_dir = os.getcwd()
    nii_dir = os.path.join(cur_dir,'nifti')
    for series in os.listdir(dcm_dir):
        dcm_series = os.path.join(dcm_dir,series)
        nii_series = os.path.join(nii_dir,series)
        if not os.path.exists(nii_series):
            os.makedirs(nii_series)
        print('Converting %s series as nii images and saved to %s' %(series, nii_series))
        bashCommand="dcm2niix -z y -f %p_%t_%s -o " + nii_series +" "+ dcm_series
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print('dcm2niix stdout:',output)

    print('**********************************************')
    print('*** dcmConvertor: FINISHED DICOM TO NIFTI  ***')
    print('********************************************\n')

def binary_threshold(dcm_dir):
    """
    Method to threshold dicom files
    :param dcm_dir: dicom directory
    """
    print('**********************************************')
    print('*** dcmConvertor: BINARY THRESHOLDING  *******')
    print('**********************************************\n')
    cur_dir = os.getcwd()
    threshold_jpeg_dir = os.path.join(cur_dir,'threshold_jpeg')
    threshold_dcm_dir = os.path.join(cur_dir,'threshold_dicom')
    for series in os.listdir(dcm_dir):
        print('Binary thresholding for series %s' %(series))
        dcm_series = os.path.join(dcm_dir,series)
        dcm_files = [os.path.basename(x) for x in glob.glob(dcm_series + '/*.dcm')] 
        t_dcm_series = os.path.join(threshold_dcm_dir,series)
        t_jpeg_series = os.path.join(threshold_jpeg_dir,series)
        if not os.path.exists(t_dcm_series):
            os.makedirs(t_dcm_series)
        if not os.path.exists(t_jpeg_series):
            os.makedirs(t_jpeg_series)
        for f in dcm_files:
            ds = pydicom.dcmread(os.path.join(dcm_series,f))
            pixel_array = ds.pixel_array
            mean = np.mean(pixel_array)
            p_threshold = np.where(pixel_array > mean, 1, 0)
            p_threshold_jpg = np.where(pixel_array > mean, 1, 255)
            p_threshold = p_threshold.astype('uint16')
            ds.PixelData = p_threshold.tobytes()
            ds.Rows, ds.Columns = pixel_array.shape
            print('\t Writing dcm threshold volumes for file %s to %s' %(f, os.path.join(t_dcm_series,f)))
            ds.save_as(os.path.join(t_dcm_series,f))
            jpeg_file = f.replace('.dcm', '.jpg')
            print('\t Writting jpeg threshold volumes for file %s to %s' %(f, os.path.join(t_jpeg_series, jpeg_file)))
            cv2.imwrite(os.path.join(t_jpeg_series, jpeg_file), p_threshold_jpg)
    print('**************************************************')
    print('*** dcmConvertor: FINISHED BINARY THRESHOLDING  ***')
    print('**************************************************\n')

def load_dicom(dcm_dir):
    """
    Method to threshold load dicom files
    :param dcm_dir: dicom directory
    """
    print('***********************************')
    print('*** dcmConvertor: LOADING DCM   ***')
    print('***********************************\n')
    for series in os.listdir(dcm_dir):
        print('Loading series %s ' %(series))
        dcm_series = os.path.join(dcm_dir,series)
        dcm_files = [os.path.basename(x) for x in glob.glob(dcm_series + '/*.dcm')]
        ref_dcm = pydicom.read_file(os.path.join(dcm_dir,series,dcm_files[0]))
        const_pixel_dims = (int(ref_dcm.Rows), int(ref_dcm.Columns), len(dcm_files))
        const_pixel_spacing = (float(ref_dcm.PixelSpacing[0]), float(ref_dcm.PixelSpacing[1]), float(ref_dcm.SliceThickness))
        array_dcm = np.zeros(const_pixel_dims, dtype=ref_dcm.pixel_array.dtype)
        for f in dcm_files:
            ds = pydicom.read_file(os.path.join(dcm_series,f))
            array_dcm[:, :, dcm_files.index(f)] = ds.pixel_array
    print('******************************************')
    print('*** dcmConvertor: FINISHED LOADING DCM ***')
    print('******************************************\n')

def add_parser_args():
    """
    Method to parse all the arguments for the tool on ArgumentParser
    :return: parser object
    """
    argp = argparse.ArgumentParser(description=DESCRIPTION, usage='use "%(prog)s --help" for more information',
                                   formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument('-d', '--dcmdir', dest='dcmdir', required=True,
                      help='Input dir with dicom series')
    argp.add_argument("--dcm2jpg",dest="dcm2jpg", action="store_true" , \
                      help="Convert from dcm to jpg")
    argp.add_argument("--dcm2nifti",dest="dcm2nifti", action="store_true" , \
                      help="Convert from dcm to nifti")
    argp.add_argument("-t",'--b_threshold',dest="b_threshold", action="store_true" , \
                      help="Convert from dcm to nifti")
    argp.add_argument("-l",'--load',dest="load", action="store_true" , \
                      help="Convert from dcm to nifti")
    return argp

if __name__ == "__main__":
    parser = add_parser_args()
    options = parser.parse_args()
    print('***********************************')
    print('***   dcmConvertor: STARTING    ***')
    print('***********************************\n')
    if not (options.dcm2jpg or options.dcm2nifti or options.b_threshold or options.load):
        print("ERORR: choose atleast one operations. Arguments required: --dcm2jpg, --dcm2nifti, --b_threshold / -t, or --load / -l")
        exit()
    if options.dcm2jpg:
        dcm2jpg(options.dcmdir)
    if options.dcm2nifti:
        dcm2nifti(options.dcmdir)
    if options.b_threshold:
        binary_threshold(options.dcmdir)
    if options.load:
        load_dicom(options.dcmdir)
    print('***********************************')
    print('***   dcmConvertor: DONE        ***')
    print('***********************************\n')


