"""
fill in
"""
from pyspark.sql import SparkSession


def append_table(data_frame, table_name):
    """
    fill in
    """
    pd_data_frame = data_frame.to_pandas()
    spark_data_frame = SparkSession.getActiveSession().createDataFrame(pd_data_frame)
    spark_data_frame.write.mode("append").format("delta").saveAsTable(table_name)
