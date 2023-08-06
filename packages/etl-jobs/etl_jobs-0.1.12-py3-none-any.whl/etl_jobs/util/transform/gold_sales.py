"""
fill in
"""
from pyspark.sql.functions import avg, sum, col


def transform_gold_sales(data_frame):
    return data_frame.select(avg("SALE").alias("AVG"),col("CUSTOMERNAME"),sum("SALE").alias("TOTAL"))
