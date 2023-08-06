from pymedquery.pg_crud_handler import CRUD
from pymedquery.minio_data_handler import MinioHandler
from pymedquery.config.logger_object import Logger
from pymedquery.config import config
from pymedquery.config.exceptions import NoRecordsFound, CommitBouncedError
from pymedquery.src.helpers import (batch_maker, encode_payload, make_uid_list, check_batch_size, timer,
                                    str2bool)

import os
import psycopg2
import numpy as np
from minio.error import S3Error
from time import sleep
from typing import Optional, Union, Dict, List, Generator, Any, Tuple, NoReturn
import requests
import importlib.metadata


class PyMedQuery:
    """The MedQuery class is the python client that connects the user
    to MedQuery via global env variables. The connection to the database
    happens during python runtime which enables the user to integrate data
    transaction directly into their code and thus project.

    The aim with publishing the method is to let the users extract and upload data in a simple and
    fast way. Data should be centralized, maintained and offered up by the data engineers such that
    the scientist and analysts dont have to think about it.

    Fast, easy and intuitive is the goal.
    """
    def __init__(self, verbose: bool = False) -> NoReturn:
        self.crud: Any = CRUD(
            user=config.USER,
            password=config.PASSWORD,
            database=config.DATABASE,
            db_port=config.MQPORT,
            host=config.MQHOST,
            _sslmode=config.SSLMODE
        )

        self.mh: Any = MinioHandler(access_key=config.USER,
                                    secret_key=config.PASSWORD,
                                    _secure=str2bool(config.SECURE),
                                    minio_host=config.MINIO_HOST)
        self.log: Any = Logger(__name__)
        if verbose:
            self.__version__ = importlib.metadata.version("pymedquery")
            self.__check_version()  # check version of the client

    def __set_extract_params(
        self,
        get_all: bool,
        get_affines: bool,
        format_params: Dict[str, Union[str, int, float, bool]],
        sql_file_path: str,
        project_id: str,
        include_mask: bool,
        limit: Union[int, str] = None,
    ) -> Union[Dict[str, Union[str, int]], str]:
        """_set_extract_params is a private method that initializes the parameters
        subsequent methods will use for data extraction and upload.

        Parameters
        ----------
        get_all : bool
            Set `get_all` to True if you want to use a default SQL script that extracts
            images and masks from a given project id for you.
        format_params : dict
            format_params is a dict containing parameters to use in the SQL script
        sql_file_path : str
            Set sql_file_path to let the program know where the SQL query file is
        project_id : str
            Specify the `project_id` for the data that you want. Be sure it is exactly the
            project id that is used in the database
        limit : Union[int, str]
            Use `limit` to set a limit on how many rows (patientIDs) to return
        """
        if get_all:
            if not project_id:
                raise ValueError("please specify the project id that corresponds to the requested data")
            if include_mask is None:
                raise ValueError("please specify `include_mask` to true or false")
            sub: str = "subq3" if include_mask else "subq2"
            sql_file_path: os.PathLike = (config.SERIES_MASK_QUERY_DEFAULT
                                          if get_affines else config.SERIES_MASK_AFF_QUERY)
            format_params: Union[Dict[str, str], Dict[any, any]] = {
                "project_id": str(project_id),
                "limit": limit,
                "sub": sub,
            }
        else:
            sql_file_path: os.PathLike = sql_file_path
            format_params: Union[Dict[str, str], Dict[any, any]] = format_params

        if not sql_file_path:
            raise ValueError("please specify the file path to your SQL script")

        return format_params, sql_file_path

    def __pg_extract(
        self,
        sql_file_path: str,
        format_params: Dict[str, Union[str, int, float, bool]],
        verbose: bool,
        reset_connection: bool,
        post_close_connection: bool,
        batch_extract: bool,
    ) -> Tuple[List[str], Union[None, int]]:
        """_pg_extract is the private method that extracts structrual and relational data
        from the RDBMS.

        Parameters
        ----------
        sql_file_path : str
            Set sql_file_path to let the program know where the SQL query file is
        format_params : dict
            format_params is a dict containing parameters to use in the SQL script

        Returns
        -------
        Tuple[List[str], Union[None, int]]
            The tuple returned will consist of all UIDs and the number of UIDs if the extraction is
            batch
        """

        # Extract the image and given records
        # NOTE! we can add the option of passing a string variable
        pg_payload: Dict[Tuple[Any]] = self.crud.read(sql=sql_file_path,
                                                      format_params=format_params,
                                                      verbose=verbose)
        self.crud.commit(reset_connection=reset_connection)
        if post_close_connection:
            self.crud.close_connection()

        # make the list of UIDs which will differ a bit for what kind of extraction you are making
        all_uids = make_uid_list(pg_payload=pg_payload, batch_extract=batch_extract)

        return all_uids, pg_payload

    def __fetch_uids(
        self,
        get_all: bool,
        get_affines: bool,
        format_params: dict,
        sql_file_path: str,
        project_id: str,
        limit: str,
        include_mask: bool,
        verbose: bool,
        reset_connection: bool,
        post_close_connection: bool,
        batch_extract: bool,
    ) -> List[str]:
        """_fetch_uids is the private method that executes the `_set_extract_params`
        and `_pg_extract`.

        Parameters
        ----------
        get_all : bool
             Set `get_all` to True if you want to use a default SQL script that extracts
            images and masks from a given project id for you.
        format_params : dict
            format_params is a dict containing parameters to use in the SQL script
        sql_file_path : str
            Set sql_file_path to let the program know where the SQL query file is
        project_id : str
            Specify the `project_id` for the data that you want. Be sure it is exactly the
        include_mask : bool
            Use include_mask if to specify whether or not you want corresponding masks to your data. The uses should know that the masks exitst,
            or else the return will be empty. This parameter is needed if and only if the get_all is True.

        Returns
        _______
        List[str] | Dict[str, List[str | float | int | bytes]]
        """

        format_params, sql_file_path = self.__set_extract_params(
            get_all=get_all,
            get_affines=get_affines,
            format_params=format_params,
            sql_file_path=sql_file_path,
            project_id=project_id,
            limit=limit,
            include_mask=include_mask,
        )
        all_uids, pg_payload = self.__pg_extract(
            sql_file_path=sql_file_path,
            format_params=format_params,
            verbose=verbose,
            reset_connection=reset_connection,
            post_close_connection=post_close_connection,
            batch_extract=batch_extract,
        )
        if not all_uids[0]:
            self.log.warning("Nothing was returned")

        return all_uids, pg_payload

    def __fetch_columns(self, table_name: str, verbose: bool, post_close_connection: bool) -> List[str]:
        """__fetch_columns will, yes, fetch the column names and return them in list.

        Parameters
        ----------
        table_name : str
            table_name is the, yes, the name of the table you want to know the column names from.

        Returns
        -------
        List[str] e.g. ['series_uid', 'time' ..., 'cancer_type']

        """
        format_params = {"table_name": table_name}
        colnames = self.crud.read(
            sql=config.COL_QUERY_DEFAULT,
            format_params=format_params,
            full_query=False,
            verbose=verbose,
        )
        self.crud.commit()
        if post_close_connection:
            self.crud.close_connection()
        if colnames:
            return colnames
        else:
            self.log.error("I tried to fetch column names but got an empty result. Lordy lord!")
            raise psycopg2.OperationalError()

    @timer
    def extract(
        self,
        get_all: bool,
        get_affines: bool = True,
        project_id: Optional[str] = None,
        limit: Optional[Union[int, str]] = "NULL",
        include_mask: Optional[bool] = None,
        format_params: Optional[dict] = None,
        sql_file_path: Optional[str] = None,
        bucket_name: Optional[str] = "multimodal-images",
        verbose: bool = False,
        image_extraction: bool = True,
        reset_connection: bool = False,
        post_close_connection: bool = False,
    ) -> Union[Dict[str, List[np.ndarray]], Dict[str, List[any]]]:
        """extract is the public method that is exposed to the user for data extraction of small image quantites. The method is
        not suitable for large extractions as it will likely end in a memory allocation error. Extract utilizes the private methods
        for its functionality. The user is expected to use the method after instantiating the class.

        Parameters
        ----------
        get_all : bool
            A default SQL query script will be used if `get_all` is set True. The default SQL query will depend on project id if it is
            set to True. All data belonging to the project id will be extracted.
        get_affines : bool
            Set get_affines to False if you want to include affines in the image extraction. (The default is False)
        project_id : Optional[str]
            The `project_id` must be set in the case where `get_all` is set to True. It is not necessary to set this parameter if the user
            is writing a user-customised SQL qeury.
        limit: Optional[Union[int, str]]
            The `limit` is a LIMIT parameter on the SQL query governing how many rows. The default is NULL which is to fetching all rows.
        include_mask : Optional[bool]
            Use include_mask if to specify whether or not you want corresponding masks to your data. The uses should know that the masks exitst,
            or else the return will be empty. This parameter is needed if and only if the get_all is True.
        format_params : Optional[dict]
            The use can include parameters for the SQL query in the dict `format_params`. This can be very helpful in the case of writing pipelines.
        sql_file_path : Optional[str]
            The `sql_file_path` is expected to be set if the user has written a custom SQL query. A standard filepath will be used in the case where
            the user wants to use the default SQL query.
        bucket_name : Optional[str]
            The standard `bucket_name` for the medical images are already given as default although other specific buckets are likely to be in other
            cases than the very standard one.
        verbose : bool
            The verbose flag will print let you print out your query if it is set to True
        image_extraction : bool
            Specify whether you are extracting images or something else by setting this argument to True or False (default is True)
        reset_connection : bool
            Reset the connection with the database by setting this flag to true
        """
        try:
            # Get the UIDs from the RDBMS
            # NOTE! all_uids is returned as tuple with (all_uids, num_of_uids) The num_of_uids will be used in batch_extract
            all_uids, data_info = self.__fetch_uids(
                get_all=get_all,
                get_affines=get_affines,
                sql_file_path=sql_file_path,
                format_params=format_params,
                project_id=project_id,
                limit=limit,
                include_mask=include_mask,
                verbose=verbose,
                reset_connection=reset_connection,
                post_close_connection=post_close_connection,
                batch_extract=False,
            )
            if not all_uids[0]:
                raise NoRecordsFound(
                    "Your query returned an empty result. Please check your query or projectID")

            if len(all_uids[0]) > 30:
                self.log.warning(f"""
                    To
                    extract {len(all_uids)} 3D images in one go and you might run into a memory
                    allocation error. Consider using batch_extract with a specific batch size to mitigate
                    potential problems.
                    """)
                sleep(5)

            if isinstance(all_uids[0], list) and len(all_uids[0]) > 1:
                # extract the images by using the MinioHandler class method
                blobs: Dict[str, List[np.ndarray]] = self.mh.get_blobs(
                    bucket_name=bucket_name,
                    blob_list=all_uids[0],
                    image_extraction=image_extraction,
                    verbose=verbose
                )
            else:
                # if the all_uids is a string then use it directly in the client
                # if the all uids is not str then extract the string from the list
                all_uids = all_uids if isinstance(all_uids[0], str) else all_uids[0]
                blobs: Dict[str, List[np.ndarray]] = self.mh.get_blobs(
                    bucket_name=bucket_name,
                    blob_name=all_uids[0],
                    image_extraction=image_extraction,
                    verbose=verbose
                )
            # merge the two dicts
            payload = blobs | data_info if image_extraction and isinstance(blobs, dict) else (blobs, data_info)
            if post_close_connection:
                self.crud.close_connection()

            return payload
        except (AttributeError, S3Error, psycopg2.Error) as e:
            self.log.error(f"failed to extract data with uids {all_uids} and error: {e}")

    def batch_extract(
        self,
        get_all: bool,
        get_affines: bool = True,
        sql_file_path: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: Optional[Union[int, str]] = "NULL",
        include_mask: Optional[bool] = None,
        format_params: Optional[dict] = None,
        batch_size: Optional[int] = 14,
        bucket_name: Optional[str] = "multimodal-images",
        verbose: bool = True,
        image_extraction: bool = True,
        reset_connection: bool = False,
        post_close_connection: bool = False,
    ) -> Generator[np.ndarray, None, None]:
        """batch_extract is a method that is very much alike `extract` although you can use it for batch extraction
        and by that avoid the memory allocation error.

        Pseudo code for illustration purposes
        >>>>
        sampler = batch_extract(...)

        for batch in sampler:
            series_list = [s for s in batch if s.startswith('series_list')]
            affine_list = [s for s in batch if s.startswith('affine')]
            for series, affine in zip(series_list, affine_list):
                raw_series_img = batch[series]
                affine_array = batch[affine]
                # process the series image and affine as you wish
                # do more stuff
                # save images in an open file

        structured_data = sample.data_info
        # save structured data in the same open file or separate file
        >>>>



        Parameters
        ----------
        get_all : bool
            see `extract` doctstring
        sql_file_path : Optional[str]
            see `extract` doctstring
        project_id : Optional[str]
            see `extract` doctstring
        limit : Optional[Union[int, str]
            see `extract` doctstring
        include_mask : Optinal[bool]
            see `extract` doctstring
        format_params : Optional[dict]
            see `extract` doctstring
        batch_size : Optional[int]
            The user can specify themselves how large the `batch_size` in the extraction iteration should be. The defualt
            is 14 and is estimated to take ca. 6-8GiB memory.
            Please make sure that your size is equal or larger than 3 if you are extracting 3 UID blobs. Also note that
            if you are setting the batch size as 2 and you are doing a 2 UID blob extraction (for example series and affien),
            then you will in effect only as get one image at the time as the affine will count for the second blob in the batch.
        bucket_name : Optional[str]
            see `extract` doctstring
        verbose : bool
            see `extract` doctstring
        image_extraction: bool
            see `extract` doctstring
        reset_connection: bool
            see `extract` doctstring

        Returns
        -------
        Generator[np.ndarray, None, None]
            The output is generator that you need to place in a loop or similar to get concrete results from. See example.
        """
        try:
            # get the UIDs from the RDBMS
            all_uids, self.data_info = self.__fetch_uids(
                get_all=get_all,
                get_affines=get_affines,
                sql_file_path=sql_file_path,
                format_params=format_params,
                project_id=project_id,
                limit=limit,
                include_mask=include_mask,
                verbose=verbose,
                reset_connection=reset_connection,
                post_close_connection=post_close_connection,
                batch_extract=True,
            )

            if all_uids[1] > 1:
                if not check_batch_size(num_of_uids=all_uids[1], batch_size=batch_size):
                    raise ValueError(
                        f"You are batch processing {all_uids[1]} UIDs but your batch {batch_size} does not let you return it in a set of {all_uids[1]}"
                    )

            # create the sample to batch from
            sample: Generator[List[str], None, None] = batch_maker(iterable=all_uids[0],
                                                                   batch_size=batch_size)

            # run bathes out of the sample and yield them one at the time
            for _batch in sample:
                # extract the images by using the MinioHandler class method
                blobby: Dict[str, List[np.ndarray]] = self.mh.get_blobs(
                    bucket_name=bucket_name,
                    blob_list=_batch,
                    image_extraction=image_extraction,
                )
                yield blobby
        except (AttributeError, psycopg2.Error, S3Error) as e:
            self.log.error(f"failed to extract the following uids {all_uids} with the error: {e}")

    @timer
    def upload(
        self,
        records: Dict[Union[str, int, float], Any],
        table_name: str,
        verbose: bool = False,
        meta: Union[Dict[str, str], None] = None,
        bucket_name: str = config.BUCKET_NAME,
        post_close_connection: bool = False,
        ignore_conflict: bool = False,
        close_conn: bool = True
    ) -> NoReturn:
        """upload is the method that allows users to upload data to MedQuery without having to deal with
        two wrappers. You simply specify the name of the table you are writing to and include the data as
        records in a dict. You can decide which bucket to store the blobs in, if you have blobs.

        Example of a dictionary with records
        >>>>
        {
        'series_213fds#323': np.ndarray,
        'mask_213fds#323': np.ndarray,
        'model_dmksf3322': None,
        datetime.datetime(0, 1900, 1): None
        }

        The structure is such that the keys are the records values to insert into a table and
        the values are records blobs that you insert into the object storage. The sorting of the keys
        need to follow the sorting in the table.

        Parameters
        ----------
        records : Dict[Union[str, int, float], Any]
            records is the dictionary containing the records you want to insert into MedQuery. The structure of the dict
            matters so please see the example if you are unsure.
        table_name : str
            table_name is simply the name of the table you are inserting into
        verbose : bool
            set verbose to true if you want to have some additional information about your upload
        meta : Union[Dict[str, str], None]
            The meta data will automatically be filled out if your data is np.ndarray
        bucket_name : str
            the bucke name specifies which bucket in the obejct storage you want to use for your data. (mulitmodal_images is the default)
        ignore_conflict : bool
            set ignore conflict to True if you just want to update the table

        Returns
        -------
        NoReturn

        """
        # Fetch the column names from the given table
        col_names = self.__fetch_columns(
            table_name=table_name,
            verbose=verbose,
            post_close_connection=post_close_connection,
        )

        for rec in records.values():
            if len(rec) != 2:
                raise ValueError(
                    f"I expected a dict value as tuple with lenght 2 corresponding to (record_value, blob | None), but got {rec}"
                )

        # create the tuple of records that will be uploaded to the RDBMS
        record_values = tuple(item[0] for item in records.values())

        if verbose:
            self.log.info(f"""
            Top of the morning! Here is friendly reminder:

            please make sure that the order of your dictionary keys follows the table structure:

            Your structure: {record_values}
            {table_name} structure: {col_names}

            Its all love if the values correspond correctly to the column name <3
            """)

        self.log.info(f"Uploading records to {table_name} in MedQuery")
        try:
            self.crud.insert(
                columns=col_names,
                records=[record_values],
                table=table_name,
                ignore_conflict=ignore_conflict,
            )
            self.crud.commit()
            if self.crud.log.error_log:
                self.crud.rollback()
                raise CommitBouncedError(f"Rolling back the database operation. Failed with: {self.crud.log.error_log}")
            # the index 1 in the tuple is supposed to be where the blob shoud be entered by the client
            for record_key, record_tuple in records.items():
                if record_tuple[1] is not None:
                    record_value, record_blob = record_tuple
                    if isinstance(record_blob, np.ndarray):
                        meta: Dict[str, str] = {
                            "img_shape": str(record_blob.shape),
                            "dtype": str(record_blob.dtype),
                        }
                    payload, payload_size = encode_payload(payload=record_blob)

                    # Make sure that the bytes reading starts from the beginning
                    if hasattr(payload, "getbuffer"):
                        payload.seek(0)
                    else:
                        raise ValueError("payload is not a IO object")

                    # NOTE! we need to make sure that the multimodal bucket dose not get cluttered with
                    # processed data, modelfiles and such. The mask from the models are fine.
                    self.mh.blob_upload(
                        bucket_name=bucket_name,
                        blob_name=record_value,
                        blob_file=payload,
                        size=payload_size,
                        meta=meta,
                    )
            self.log.success("Your upload is completed!")
            if close_conn:
                self.crud.close_connection()

        except (ValueError, psycopg2.Error, S3Error) as e:
            self.log.error(
                f"I tried to connect to the MedQuery but failed to upload the record values {record_values} with the traceback: {e}"
            )

    def __check_version(self) -> NoReturn:
        """__check_version is a method that checks the version of the client against the latest version on PyPI


        Returns
        -------
        NoReturn

        Raises
        ------
        requests.exceptions.HTTPError: Failed to fetch the latest version number from PyPI.
        """
        try:
            response = requests.get(config.PYPIMETADATA, timeout=5)
            response.raise_for_status()
            latest_version = response.json()["info"]["version"]

            # Compare the version number to the latest version on PyPI
            if str(self.__version__) != str(latest_version):
                message = f"A new version of PyMedQuery is available! {self.__version__} => {latest_version}"
                self.log.warning(message)
        except requests.exceptions.HTTPError as e:
            self.log.error(f"Failed to fetch the latest version number from PyPI with the error: {e}")
