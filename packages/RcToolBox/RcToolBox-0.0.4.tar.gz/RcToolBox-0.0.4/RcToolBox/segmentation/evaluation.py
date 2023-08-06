import os
import sys
from RcToolBox.segmentation.metric import cal_dice
from RcToolBox.basic_op import *
from RcToolBox.xeon_op import hardcore_process
from RcToolBox.pandas_op import generate_dataframe
from copy import deepcopy
import numpy as np
import pandas as pd



def cal_standard_dataset_dice(patient_id_list,
                              prediction_list,
                              groundtruth_list,
                              num_label,
                              column_name,
                              excel_path,
                              individual_mean=True,
                              dataset_mean=True,
                              additional_info=None,
                              precision=2,
                              num_workers=8):
    """    
    generate a excel file with the dice score of each label

    Args:

        patient_id_list: list of patient id

    """

    assert len(prediction_list) == len(groundtruth_list) == len(patient_id_list),\
        'prediction_list, groundtruth_list and patient_id_list should have the same length'

    if not isinstance(column_name, list):
        raise TypeError('column name should be a list')

    if isinstance(num_label, int):
        num_label_list = [num_label] * len(patient_id_list)

    if additional_info is None:
        additional_info_list = [None] * len(patient_id_list)
    elif isinstance(additional_info, list):
        additional_info_list = additional_info
    else:
        raise TypeError('additional_info should be a list or None')

    res = hardcore_process(cal_dice,
                           patient_id_list,
                           prediction_list,
                           groundtruth_list,
                           num_label_list,
                           additional_info_list,
                           [individual_mean] * len(patient_id_list),
                           num_workers=num_workers)
    
    if individual_mean:
        column_name.insert(num_label+1, 'Mean')

    if dataset_mean:
        if individual_mean:
            _ = np.array(deepcopy(res))[:, 1:num_label+2].astype(np.float32)
        else:
            _ = np.array(deepcopy(res))[:, 1:num_label+1].astype(np.float32)

        mean_ = np.mean(_, axis=0)
        # Add the mean to the first row
        if additional_info is None:
            res = [['Average'] + list(mean_)] + res
        else:
            res = [['Average'] + list(mean_)+['Average']] + res

    generate_dataframe(res,
                       column_name,
                       return_dataframe=False,
                       save_excel=True,
                       excel_path=excel_path,
                       excel_formatting=True,
                       precision=precision)


if __name__ == '__main__':

    pass


