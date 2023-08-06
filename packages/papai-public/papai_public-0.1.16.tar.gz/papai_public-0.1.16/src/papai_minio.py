from typing import List

import pyarrow as pa
import pyarrow.parquet as pq
from object_storage_client import ObjectStorageClient


def get_bucket_from_step_name(step_name: str, list_buckets: List[dict]):
    for bucket in list_buckets:
        if bucket["step_name"] == step_name:
            return bucket


def get_dataset_path_from_step_name(step_name: str, list_parquets: List[dict]):
    for parquet in list_parquets:
        if parquet["step_name"] == step_name:
            return parquet["bucket_name"], parquet["object_name"]


def get_artefacts_path_from_registry_name(registry_name: str, list_registries: List[dict]):
    for registry in list_registries:
        if registry["registry_name"] == registry_name:
            return registry


def read_from_bucket_to_file(bucket_name: str, object_name: str, list_buckets: List[dict], client):
    try:
        bucket_config = get_bucket_from_step_name(bucket_name, list_buckets)
        bucket_name = bucket_config["bucket_name"]
        object_storage_client = ObjectStorageClient(bucket_config, client)
        return object_storage_client.read_from_bucket_to_file(bucket_name, object_name)
    except Exception as ex:
        raise Exception("Not able to read the object / " + str(ex))


def write_file_in_bucket(bucket_name: str, file_name: str, data, list_buckets: List[dict], client):
    try:
        bucket_config = get_bucket_from_step_name(bucket_name, list_buckets)
        bucket_name = bucket_config["bucket_name"]
        object_storage_client = ObjectStorageClient(bucket_config, client)
        object_storage_client.write_file_in_bucket(bucket_name, file_name, data)
    except Exception as ex:
        raise Exception("Not able to write the file / " + str(ex))


def import_dataset(dataset_name: str, list_parquets: List[dict], client, s3):
    try:
        bucket_name, path = get_dataset_path_from_step_name(dataset_name, list_parquets)
        bucket = client.bucket_exists(bucket_name)
        if bucket:
            df = pq.ParquetDataset(f"{bucket_name}/{path}", filesystem=s3).read_pandas().to_pandas()
            return df
        else:
            raise Exception("Bucket" + bucket_name + "does not exist")
    except Exception as ex:
        raise Exception("Not able to get data from minio bucket / " + str(ex))


def export_dataset(dataset, dataset_step_name, list_parquets, client, s3):
    try:
        bucket_name, path = get_dataset_path_from_step_name(dataset_step_name, list_parquets)
        bucket = client.bucket_exists(bucket_name)
        if bucket:
            table = pa.Table.from_pandas(dataset, preserve_index=False)
            pq.write_table(table, f"{bucket_name}/{path}", filesystem=s3, compression="snappy")
            return True
        else:
            raise Exception("Bucket" + bucket_name + "does not exist")
    except Exception as ex:
        raise Exception("Not able to save data into minio bucket / " + str(ex))


def get_model_artefact(registry_name: str, artefact_path: str, registries_inputs: List[dict], client, run_id: str = None):
    try:
        registry = get_artefacts_path_from_registry_name(registry_name, registries_inputs)
        object_storage_client = ObjectStorageClient(registry, client)
        artefacts_folder = registry['artefacts_path']
        if run_id:
            artefacts_folder = "/".join(artefacts_folder.split("/")[:-1]) + "/" + run_id
        return object_storage_client.read_from_bucket_to_file(
            registry["bucket_name"],
            f"{artefacts_folder}/{artefact_path}"
        )
    except Exception as ex:
        raise Exception("Not able to read the artefact {artefact_path} of registry {registry_name} / " + str(ex))


def save_model_artefact(registry_name: str, artefact_path: str, data, registries_inputs: List[dict], client, run_id: str = None):
    try:
        registry = get_artefacts_path_from_registry_name(registry_name, registries_inputs)
        object_storage_client = ObjectStorageClient(registry, client)
        artefacts_folder = registry['artefacts_path']
        if run_id:
            artefacts_folder = "/".join(artefacts_folder.split("/")[:-1]) + "/" + run_id
        object_storage_client.write_file_in_bucket(
            registry["bucket_name"],
            f"{artefacts_folder}/{artefact_path}",
            data
        )
    except Exception as ex:
        raise Exception("Not able to write the artefact file / " + str(ex))
