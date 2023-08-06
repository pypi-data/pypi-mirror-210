import os
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from pymedquery.src.helpers import nested_dict

# Paths
ROOT: str = os.getcwd()
# Get the package path
data_path: str = pkg_resources.path("pymedquery.sql.default", "image_default_query.sql")
data_path_col: str = pkg_resources.path("pymedquery.sql.default", "col_query.sql")
data_path_aff: str = pkg_resources.path(
    "pymedquery.sql.default", "image_affine_default_query.sql"
)
sh_path: str = pkg_resources.path("pymedquery", "medqueryInit.sh")
with data_path as sql, data_path_col as col_query_sql, sh_path as sh, data_path_aff as affine_sql:
    SERIES_MASK_QUERY_DEFAULT = str(sql)
    SERIES_MASK_AFF_QUERY = str(affine_sql)
    COL_QUERY_DEFAULT = str(col_query_sql)
    SHPATH = str(sh)

MOD_FILE_PATH: os.PathLike = os.path.join(ROOT, "tests/data/modelw_v1.1.0.pkl")
# postgres and storage params
DATABASE_TMP: str = "medquery_dev"

# uids that exist in across the whole MedQuery infrastructure
BLOB_UIDS: List[str] = [
    "series_uid",
    "mask_uid",
    "affine_uid",
    "model_id",
    "pmask_uid",
    "version_uid",
    "report_uid",
]

STORAGE_NAME: str = "medical_imaging_storage"
BUCKET_NAME: str = "multimodal-images"
TEST_BUCKET: str = "test-bucket"
bucket_dict: Dict[str, List[str]] = defaultdict(list)
blob_dict: Dict[str, np.ndarray] = {}
nested_blob_dict: Dict[str, Dict[str, any]] = nested_dict()
BUCKET_KEYS: List[str] = ["bucket_name", "creation_date"]
# NOTE! naming conventions tend to change between MinIO versions. Be aware!
IMG_META = "X-Amz-Meta-Img_shape"
DTYPE_META = "X-Amz-Meta-Dtype"

# [TEST CONF]
TEST_TABLE: str = "test_table"
PRIMARY_KEY: List[str] = ["series_uid"]
NEW_COL_VALS: str = "new_name"
COL_TO_CHANGE: str = "protocol_names"
COLS: List[str] = ["series_uid", "pixel_spacing", "series_number", "protocol_names"]
RECORDS: List[Tuple[str, List[float], int, str]] = [
    ("series_666", [0.431, 0.233], 32, "i_am_a_protocol")
]
SQL_FILE_PATH: os.PathLike = os.path.join(ROOT, "pymedquery/data/sql/test.sql")

USELESS_SERIES: str = "mask_24489d87e68ce46b13dcaad73087d69326c5fe8035cbf41d7ef61a21d21ff3b350db4c351dbe2fec2ad76f74bec3"
TEST_SQL_FILE: os.PathLike = os.path.join(ROOT, "pymedquery/data/sql/create.sql")
TEST_SQL_FILEPATH_FULL: os.PathLike = os.path.join(
    ROOT, "pymedquery/sql/default/image_default_query.sql"
)
TEST_SQL_FILE_MODELW: os.PathLike = os.path.join(
    ROOT, "tests/data/sql/model_w_extract.sql"
)
TEST_DATA_FILEPATH: os.PathLike = os.path.join(ROOT, "tests/data/np.npy")
TEST_WEIGHTS_FILEPATH: os.PathLike = os.path.join(
    ROOT, "tests/data/model_weights_v010.h5"
)
TEST_BATCH_FILEPATH: os.PathLike = os.path.join(
    ROOT, "tests/data/sql/batch_extract.sql"
)
TEST_GENERIC_SQL: os.PathLike = os.path.join(ROOT, "tests/data/sql/generic.sql")

BLOB_NAME_I = "img_666"
BLOB_NAME_W = "mod_weights_666"

BLOBS: List[str] = [BLOB_NAME_I, BLOB_NAME_W]

UPDATE_ON_PRIMARY_KEY: str = "series_666"

# Extensions
EXT_READTYPE_DICT: Dict[str, str] = {
    "pkl": "rb",
    "pickle": "r",
    "json": "r",
    "csv": "r",
    "gz": "rb",
}

# MedQuery credentials for the userfriendly version
USER: str = os.environ.get("MQUSER")
PASSWORD: str = os.environ.get("MQPWD")
DATABASE: str = os.environ.get("DATABASE")
MQHOST: str = os.environ.get("MQHOST", "medquery.medical-database.com")
MQPORT: int = os.environ.get("MQPORT", 7775)
SSLMODE: str = os.environ.get("SSLMODE", "verify-full")
SECURE: str = os.environ.get("SECURE", "True")
MINIO_HOST: str = os.environ.get("MINIO_HOST", "storage.medical-database.com")

# utils configs
RESPONSE_TYPES = ["binary", "multilabel", "multiclass", "continuous"]

# pypi
PYPIMETADATA = "https://pypi.org/pypi/pymedquery/json"
