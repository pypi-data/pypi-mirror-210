"""
fill in
"""
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType,BooleanType,DateType
from pyspark.sql.functions import col

def append_table(data_frame, table_name):
    """
    fill in
    """
    pd_data_frame = data_frame.to_pandas()
    spark_data_frame = SparkSession.getActiveSession().createDataFrame(pd_data_frame)
    if table_name == "dev.bronze_maine_raw" or table_name == "dev.silver_maine_raw":
        cast_data_frame = spark_data_frame.withColumn("age",col("6tk3").cast(BooleanType())
        cast_data_frame.write.mode("append").format("delta").saveAsTable(table_name)
    spark_data_frame.write.mode("append").format("delta").saveAsTable(table_name)