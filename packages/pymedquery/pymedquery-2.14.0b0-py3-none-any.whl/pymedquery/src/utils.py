from pymedquery.config.logger import get_logger
from pymedquery.config import config

import numpy as np
from nibabel.nifti1 import Nifti1Header, Nifti1Image
from nibabel.spatialimages import HeaderDataError
from typing import Tuple, Dict, Any, List, Union
from datetime import datetime

log = get_logger(__name__)


def convert2nii(img: np.ndarray, affine: np.ndarray = None, zooms: Tuple[float] = None, is_mask: bool = False) -> Nifti1Image:
    """convert2nii is a utility function that wraps a volume/image in a Nifti1Image object.
    The reason why this is added to pyMedQuery is the need to have medical images wrapped in
    nifti classes for subsequent analyses. There are a lot of legacy software that require
    the images to be wrapped in a nifti.

    Parameters
    ----------
    img : np.ndarray
        img is the 3D medical volume
    affine : np.ndarray
        affine is the 2D 4x4 rotation matrix corresponding to the medical volume
    zooms : Tuple[float]
        zooms are dimensions of the voxel, which are x, y, z in the voxel.
    """
    if not is_mask:
        try:
            header = Nifti1Header()
            header.set_data_dtype(img.dtype)
            header.set_data_shape(img.shape)
            header.set_zooms(zooms)

        except (HeaderDataError, ValueError, TypeError):
            log.error('failed setting values to the nifti header with msg:', exc_info=True)
    else:
        header = None

    try:
        nii_img = Nifti1Image(dataobj=img, affine=affine, header=header)
    except (ValueError, TypeError):
        log.error('failed placing the image, affine and header in the Nifti1Image class:', exc_info=True)

    return nii_img


def make_model_records(
        time_of_upload: datetime,
        model_id: str,
        model_name: str,
        model_type: str,
        project_id: str,
        model_version: str,
        model_weights: Dict[str, Any],
        project_owner: str,
        response_type: str,
        model_owner: str,
        output_metric: str,
        time_of_last_train: datetime,
        min_resolution_required: float = None,
        DICE: float = None,
        AUC: float = None,
        F1: float = None,
        ACC: float = None,
        precision: float = None,
        recall: float = None) -> List[Dict[str, Tuple[Union[str, float], Dict[str, Any]]]]:
    """make_model_records is supportive functions that makes the records ready for model upload with pymedquery.

    Parameters
    ----------
    time_of_upload : datetime
        time_of_upload indicates the actual time of upload. You could use datetime.now() for this.
    model_id : str
        model_id is a model hash that will uniquely identify the model. This value most match the value in the junction_ml_table.
    model_name : str
        model name refers to the architecture.
    model_type : str
        model type refers to which deep learning framework has been used.
    project_id : str
        project id is string that identifies the project the model is associated with.
    model_version : str
        Use semantic versioning to keep track of the model development.
    model_weights : Dict[str, Any]
        model_weights is the state_dict from PyTorch containing the model weights needed to configure the approximated function.
    project_owner : str
        project_owner is you or the person that keeps the strings attatched regarding the model.
    response_type : str
        response_type refers to what kind of target value is used the model development; is it a continuous or classification problem.
    time_of_last_train : datetime
        time_of_last_train specifies the time this specific model version was last recalibrated.
    DICE : float
        DICE score the metric for measuring similarity between e.g. two image.
    AUC : float
        AUC  is the area under the curve and gives you a rough estimate of how well your model is classifying the targer values
    F1 : float
        F1 is the harmonic mean of the precision and recall and will give you a good measure on how well your model is classifying
        the target values regardless if the target values are imbalanced, e.i. there is a clear overweight of one event compared to
        other/s.
    ACC : float
        ACC is the accuracy metric and gives a rough estimate of the model predictive power of a continuous or classification problem.
    precision : float
        precision gives you an understanding of the percentage of how many target values that were correctly predicted in the sample
        that the model made for it's self.
    recall : float
        recall gives you an understanding you the percentage of how many correct target values were included in the sample that the
        model picks out.
    model_owner : str
        model owner lets your team, group or company know who specifically developed the model
    output_metric : str
        specify the metric of the output here. It could e.g. be mililiter, sqcentimeter, centimeter, kilogram etc.
    min_resolution_required : float
    """

    if response_type not in config.RESPONSE_TYPES:
        raise ValueError(f'The response_type must be one of the following: {config.RESPONSE_TYPES}')

    if not isinstance(time_of_upload, datetime) or not isinstance(time_of_last_train, datetime):
        raise ValueError('Make sure that your time stamps are in datetime format')

    model_junction_records = {
        'model_id': (model_id, None),
        'project_id': (project_id, None)
    }

    model_artifacts_records = {
        'time_of_upload': (time_of_upload, None),
        'model_id': (model_id, model_weights),
        'model_name': (model_name, None),
        'model_version': (model_version, None),
        'project_owner': (project_owner, None),
        'response_type': (response_type, None),
        'time_of_last_train': (time_of_last_train, None),
        'DICE': (DICE, None),
        'AUC': (AUC, None),
        'F1': (F1, None),
        'ACC': (ACC, None),
        'precision': (precision, None),
        'recall': (recall, None),
        'model_owner': (model_owner, None),
        'output_metric': (output_metric, None),
        'model_type': (model_type, None),
        'min_resolution_required': (min_resolution_required, None)
    }

    return [model_junction_records, model_artifacts_records]
