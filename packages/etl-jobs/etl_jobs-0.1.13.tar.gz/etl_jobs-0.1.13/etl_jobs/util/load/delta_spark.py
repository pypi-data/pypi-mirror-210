"""
fill in
"""
from pyspark.sql import SparkSession
from pyspark.sql.types import BooleanType, IntegerType
from pyspark.sql.functions import col


def to_spark_data_frame(data_frame):
    pd_data_frame = data_frame.to_pandas()
    return SparkSession.getActiveSession().getActiveSession().createDataFrame(pd_data_frame)


def append_table(data_frame, table_name, database_name):
    """
    fill in
    """
    if "machine_raw" in table_name:
        cast_data_frame = data_frame.withColumn("6tk3_new", col("6tk3").cast(BooleanType())).drop(
            "6tk3").withColumnRenamed("6tk3_new", "6tk3")
        cast_data_frame.write.mode("append").format("delta").saveAsTable(database_name + "." + table_name)
    elif "bronze_sales" in table_name:
        cast_data_frame = data_frame.withColumn("ORDERNUMBER_new", col("ORDERNUMBER").cast(IntegerType())).drop(
            "ORDERNUMBER").withColumnRenamed("ORDERNUMBER_new", "ORDERNUMBER").withColumn("STATUS_new",
                                                                                          col("STATUS").cast(
                                                                                              BooleanType())).drop(
            "STATUS").withColumnRenamed("STATUS_new", "STATUS")
        cast_data_frame.write.mode("append").format("delta").saveAsTable(database_name + "." + table_name)
    else:
        data_frame.write.mode("append").format("delta").saveAsTable(database_name + "." + table_name)
