import os
import sys
import numpy as np
from RcToolBox.nifti_op import load_nifti

# From https://github.com/frankkramer-lab/miseval/blob/master/miseval/dice.py
def cal_dice(patient_id, prediction, groundtruth, num_label, 
             additional_info=None,individual_mean=False):
    """_summary_

    Parameters
    ----------
    patient_id : str
    prediction : nifti path, np.ndarray
    groundtruth : nifti path, np.ndarray
    num_label : int
    uid : Any type, optional
        in case want to add sth like seed, by default None
    individual_mean : bool, optional

    """
    if not isinstance(prediction, np.ndarray) or not isinstance(groundtruth, np.ndarray):
        try:
            prediction = load_nifti(prediction, load_info=False)
            groundtruth = load_nifti(groundtruth, load_info=False)
        except Exception as err:
            print(err)
    
    if isinstance(prediction, np.ndarray) and isinstance(groundtruth, np.ndarray):
        
        res_list = [patient_id]
        dice_sum = 0
                
        for label in range(1, num_label+1):
            pd = np.equal(prediction, label)
            gt = np.equal(groundtruth, label)
            
            if gt.sum() == 0 and pd.sum() == 0:
                dice = 1.0
            elif (gt.sum()+ pd.sum()) != 0:
                dice = 2.0 * np.logical_and(gt, pd).sum() / (gt.sum() + pd.sum())
            else:
                dice = 0.0
            
            dice_sum += dice
            res_list.append(dice)
        
        if individual_mean:
            res_list.append(dice_sum/num_label)

        if additional_info is not None:
            res_list.append(additional_info)
        
        return res_list

