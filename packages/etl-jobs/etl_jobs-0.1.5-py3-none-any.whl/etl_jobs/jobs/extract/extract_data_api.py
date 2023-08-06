"""
fill in

"""
from etl_jobs.configuration.api_raw_data.apis import Apis
from etl_jobs.util.extract.api import get_api_data
from etl_jobs.util.load.delta_local import append_table
from etl_jobs.util.transform.polar_bear import transform_machine_bronze


def extract_data_api():
    """
    fill in
    """
    # spark = SparkSession \
    #    .builder \
    #    .appName("Schema App") \
    #    .getOrCreate()
    for api in Apis:
        raw = get_api_data(api.url, "56c5cc10")
        location = "/user/hive/warehouse/dev.db/" + api.name
        if api.name == "bronze_maine_raw":
            transformed = transform_machine_bronze(raw)
            append_table(transformed, location)
        else:
            append_table(raw, location)


if __name__ == "__main__":
    extract_data_api()
