### Instructions found here: https://docs.astronomer.io/learn/xcom-backend-tutorial

from airflow.models.xcom import BaseXCom
from airflow.providers.google.cloud.hooks.gcs import GCSHook
import pandas as pd
import json
import uuid
import os

class CustomXComBackendPandas(BaseXCom):
    PREFIX = "xcom_gcs://"
    BUCKET_NAME = "xcom_gcs_fpl"

    @staticmethod
    def serialize_value(
        value,
        key=None,
        task_id=None,
        dag_id=None,
        run_id=None,
        map_index= None,
        **kwargs
    ):

        hook = GCSHook(gcp_conn_id="google-cloud-default")
        
        # added serialization method if the value passed is a Pandas dataframe
        # the contents are written to a local temporary csv file
        if isinstance(value, pd.DataFrame):
            filename = "data_" + str(uuid.uuid4()) + ".csv"
            gs_key = f"{run_id}/{task_id}/{filename}"

            value.to_csv(filename)

        # if the value passed is not a Pandas dataframe, attempt to use
        # JSON serialization
        else:
            filename = "data_" + str(uuid.uuid4()) + ".json"
            gs_key = f"{run_id}/{task_id}/{filename}"

            with open(filename, 'a+') as f:
                json.dump(value, f)

        hook.upload(
            filename=filename,
            object_name=gs_key,
            bucket_name=CustomXComBackendPandas.BUCKET_NAME,
        )

        # remove the local temporary file
        os.remove(filename)

        reference_string = CustomXComBackendPandas.PREFIX + gs_key

        return BaseXCom.serialize_value(value=reference_string)

    @staticmethod
    def deserialize_value(result):
        result = BaseXCom.deserialize_value(result)

        hook = GCSHook(gcp_conn_id="google-cloud-default")
        gs_key = result.replace(CustomXComBackendPandas.PREFIX, "")

        filename = hook.download(
            object_name=gs_key,
            bucket_name=CustomXComBackendPandas.BUCKET_NAME,
            filename="my_xcom.csv"
        )

        # added deserialization option to convert a CSV back to a dataframe
        if gs_key.split(".")[-1] == "csv":
            output = pd.read_csv(filename)
        # if the key does not end in 'csv' use JSON deserialization
        else:
            with open(filename, 'r') as f:
                output = json.load(f)

        # remove the local temporary file
        os.remove(filename)

        return output