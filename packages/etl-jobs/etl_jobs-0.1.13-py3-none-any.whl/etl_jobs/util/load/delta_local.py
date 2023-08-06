"""
fill in
"""

from deltalake.writer import write_deltalake


def append_table(data_frame, location):
    """
    fill in
    :param data_frame:
    :param location:
    :return:
    """
    pd_data_frame = data_frame.to_pandas()
    write_deltalake(location, pd_data_frame, mode="append")
