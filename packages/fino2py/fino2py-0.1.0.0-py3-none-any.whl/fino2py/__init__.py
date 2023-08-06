##Import all functions from the submodules

# The ingesting modules
from .ingesting.read_raw_finometer_data import read_raw_finometer_data
from .ingesting.read_raw_demographics import read_raw_demographics

# the data cleaning modules
from .cleaning.merge_split_data import merge_split_data


# The reshaping modules
from .reshaping.minute_by_minute import minute_by_minute
from .reshaping.minute_by_minute_from_folder import minute_by_minute_from_folder
from .reshaping.create_chunk import create_chunk
from .reshaping.generate_protocol_averages import generate_protocol_averages

# The times modules
from .times.convert_partial_time import convert_partial_time
from .times.convert_fino_time import convert_fino_time
from .times.convert_timestamp_time import convert_timestamp_time
from .times.import_protocol_times import import_protocol_times


__all__ = [
    'read_raw_finometer_data',
    'read_raw_demographics',
    'generate_protocol_averages',
    'create_chunk',
    'merge_split_data',
    'minute_by_minute',
    'minute_by_minute_from_folder',
    'convert_partial_time',
    'convert_fino_time',
    'convert_timestamp_time',
    'import_protocol_times'
]