# /usr/bin/env python
import os
import glob
import numpy as np
from RcToolBox.nifti_op import load_nifti, get_mask_bbox
from RcToolBox.xeon_op import hardcore_process
from RcToolBox.pandas_op import generate_dataframe
from RcToolBox.basic_op import *
import warnings
warnings.filterwarnings("ignore")

# calculate file size, return in MB
def get_file_size(file_path):
    """
    Args:
        file_path: file path
    Returns:
        file size
    """
    file_size = os.path.getsize(file_path) / 1024 / 1024
    if file_size > 1:
        return round(file_size)
    else:
        return round(file_size, 2)


def get_nifti_img_file_info(file_path):
    """
    Args:
        file_path: file path
    Returns:
        file size, file dimension, file spacing
    """
    patient_id = os.path.basename(file_path)[:-7]

    if "_0000" in patient_id:
        patient_id.replace("_0000", "")

    img_npy, img_origin, img_spacing, img_direction = load_nifti(
        file_path, load_info=True)

    img_min, img_max = np.min(img_npy), np.max(img_npy)
    img_file_size = get_file_size(file_path)

    return patient_id, img_min, img_max, img_npy.shape[0],  img_npy.shape[1], img_npy.shape[2], \
img_spacing[0], img_spacing[1], img_spacing[2], str(img_npy.dtype), str(img_file_size)+'MB'


def get_nifti_img_mask_info(img_path, mask_path, label_name):
    """
    Args:
        file_path: file path
    Returns:
        file size, file dimension, file spacing
    """

    img_npy, img_origin, img_spacing, img_direction = load_nifti(
        img_path, load_info=True)
    mask_npy = load_nifti(mask_path, load_info=False)

    if img_npy.shape != mask_npy.shape:
        raise ValueError("Image and mask shape not match")
    if img_spacing[0] != img_spacing[1]:
        raise ValueError("Spacing is not equal in x and y direction")

    patient_id = os.path.basename(img_path)[:-7]

    if "_0000" in patient_id:
        patient_id = patient_id.replace("_0000", "")

    img_min, img_max = np.min(img_npy), np.max(img_npy)

    foreground_ratio = (np.sum(mask_npy > 0) / np.prod(mask_npy.shape)) * 100

    mean_value = []
    volume = []
    for i in range(len(label_name)):
        # it is possible that some label is not in the mask
        # if so, the mean value will be nan
        mean_value.append(np.mean(img_npy[mask_npy == i + 1]))
        volume.append(
            np.sum(mask_npy == i + 1) * img_spacing[0] * img_spacing[1] *
            img_spacing[2])

    img_file_size = get_file_size(img_path)

    label_num = len(np.unique(mask_npy)) - 1

    foreground_coord = get_mask_bbox(mask_npy,
                                           return_mask=False,
                                           return_coord=True)
    bbox_z, bbox_h, bbox_w = foreground_coord[1] - foreground_coord[0], foreground_coord[3] - foreground_coord[2],\
                            foreground_coord[5] - foreground_coord[4]

    if len(label_name) == 1:
        return patient_id, img_min, img_max, label_num,  str(round(foreground_ratio,2))+"%",\
        mean_value[0], volume[0], bbox_z, bbox_h, bbox_w,\
        img_npy.shape[0], img_npy.shape[1], img_npy.shape[2], img_spacing[2],img_spacing[1], img_spacing[0],\
        str(img_npy.dtype), str(img_file_size)+'MB'

    elif len(label_name) == 2:
        return patient_id, img_min, img_max, label_num,  str(round(foreground_ratio,2))+"%",\
            mean_value[0], mean_value[1], volume[0], volume[1], bbox_z, bbox_h, bbox_w,\
            img_npy.shape[0], img_npy.shape[1], img_npy.shape[2], img_spacing[2],img_spacing[1], img_spacing[0],\
                str(img_npy.dtype), str(img_file_size)+'MB'

    elif len(label_name) == 3:
        return patient_id, img_min, img_max, label_num,  str(round(foreground_ratio,2))+"%",\
            mean_value[0], mean_value[1], mean_value[2], volume[0], volume[1], volume[2], bbox_z, bbox_h, bbox_w,\
                img_npy.shape[0], img_npy.shape[1], img_npy.shape[2], img_spacing[2],img_spacing[1], img_spacing[0],\
                    str(img_npy.dtype), str(img_file_size)+'MB'

    elif len(label_name) == 4:
        return patient_id, img_min, img_max, label_num,  str(round(foreground_ratio,2))+"%",\
            mean_value[0], mean_value[1], mean_value[2], mean_value[3], volume[0], volume[1], volume[2], volume[3], bbox_z, bbox_h, bbox_w,\
                img_npy.shape[0], img_npy.shape[1], img_npy.shape[2], img_spacing[2],img_spacing[1], img_spacing[0],\
                    str(img_npy.dtype), str(img_file_size)+'MB'

    else:
        raise ValueError("label number should be less than 5")


def get_nifti_dataset_info(img_list,
                           mask_list=None,
                           label_name=None,
                           excel_path=None,
                           num_workers=8):
    """ get nifti dataset information

    Parameters
    ----------
    img_list : list
    mask_list : list, optional
    excel_path : str, optional
    num_workers : int, optional
    """

    if excel_path is None:
        excel_path = 'dataset_info.xlsx'

    if mask_list is not None:

        assert label_name is not None, "please provide label name"

        label_mean_list = [i + '_mean' for i in label_name]
        label_volume_list = [i + '_volume' for i in label_name]
        res = hardcore_process(get_nifti_img_mask_info,
                               img_list,
                               mask_list, [label_name] * len(img_list),
                               num_workers=num_workers)

        generate_dataframe(
            res,
            column_name=['Patient_id', 'Min', 'Max', 'Label', 'FG_Ratio'] +
            label_mean_list + label_volume_list + [
                'BBox_Z',
                'BBox_H',
                'BBox_W',
                'Z',
                'H',
                'W',
                'Z_spacing',
                'H_spacing',
                'W_spacing',
                'Type',
                'Size',
            ],
            save_excel=True,
            excel_path=excel_path)

    else:
        res = hardcore_process(get_nifti_img_file_info,
                               img_list,
                               num_workers=num_workers)
        generate_dataframe(res,
                           column_name=[
                               'Patient_id', 'Min', 'Max', 'Z', 'H', 'W',
                               'Z_spacing', 'H_spacing', 'W_spacing', 'Type',
                               'Size'
                           ],
                           save_excel=True,
                           excel_path=excel_path)


if __name__ == '__main__':

    pass