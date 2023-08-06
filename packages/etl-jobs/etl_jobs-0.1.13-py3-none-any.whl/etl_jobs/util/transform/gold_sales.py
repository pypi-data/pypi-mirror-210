"""
fill in
"""

from pyspark.sql.functions import avg, sum, col

from etl_jobs.util.load.delta_spark import to_spark_data_frame


def transform_gold_sales(data_frame):
    return to_spark_data_frame(data_frame).groupBy("CUSTOMERNAME").agg(avg("SALE").alias("AVG"), sum("SALE").alias("TOTAL"))
