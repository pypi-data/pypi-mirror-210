"""Schema and singer message funtionalities"""
from typing import Dict, List

from datetime import datetime
from decimal import Decimal
from dateutil import parser
from dateutil.parser import ParserError
from decimal import Decimal
from datetime import datetime, date
from singer import get_logger

from macrometa_target_bigquery.exceptions import UnexpectedValueTypeException

LOGGER = get_logger('macrometa_target_bigquery')

# max timestamp/datetime supported in BQ, used to reset all invalid dates that are beyond this value
MAX_TIMESTAMP = datetime.strptime('9999-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

# max time supported in BQ, used to reset all invalid times that are beyond this value
MAX_TIME = (datetime.strptime('23:59:59.999999','%H:%M:%S.%f') - datetime.min)


def get_schema_names_from_config(config: Dict) -> List:
    """Get list of target schema name from config"""
    target_schema = config.get('target_schema')
    schema_names = []

    if target_schema:
        schema_names.append(target_schema)

    return schema_names


def adjust_timestamps_in_record(record: Dict, schema: Dict) -> None:
    """
    Goes through every field that is of type date/datetime/time and if its value is out of range,
    resets it to MAX value accordingly
    Args:
        record: record containing properties and values
        schema: json schema that has types of each property
    """

    # creating this internal function to avoid duplicating code and too many nested blocks.
    def reset_new_value(record: Dict, key: str, _format: str):
        if not isinstance(record[key], str):
            raise UnexpectedValueTypeException(
                f'Value {record[key]} of key "{key}" is not a string.')

        try:
            if _format == 'time':
                record[key] = parser.parse(record[key]).time()
            elif _format == 'date':
                record[key] = parser.parse(record[key]).date()
            else:
                record[key] = parser.parse(record[key])
        except ParserError:
            LOGGER.warning('Parsing the %s "%s" in key "%s" has failed, thus defaulting to max '
                           'acceptable value of %s in BigQuery', _format, record[key], key, _format)
            record[key] = MAX_TIMESTAMP if _format != 'time' else MAX_TIME

    # traverse the schema looking for properties of some date type
    for key, value in record.items():
        if value is not None and key in schema['properties']:
            if 'anyOf' in schema['properties'][key]:
                for type_dict in schema['properties'][key]['anyOf']:
                    if 'string' in type_dict['type'] and type_dict.get('format', None) in {'date-time', 'time', 'date'}:
                        reset_new_value(record, key, type_dict['format'])
                        break
            else:
                if 'string' in schema['properties'][key]['type'] and \
                        schema['properties'][key].get('format', None) in {'date-time', 'time', 'date'}:
                    reset_new_value(record, key, schema['properties'][key]['format'])


def float_to_decimal(value):
    """Walk the given data structure and turn all instances of float into double."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, list):
        return [float_to_decimal(child) for child in value]
    if isinstance(value, dict):
        return {k: float_to_decimal(v) for k, v in value.items()}
    return value


def add_metadata_values_to_record(record_message):
    """Populate metadata _sdc columns from incoming record message
    The location of the required attributes are fixed in the stream
    """
    def parse_datetime(dt):
        try:
            # TODO: figure out why we can get _sdc_deleted_at as both datetime and string objects
            if isinstance(dt, date):
                return dt

            return parser.parse(dt)
        except TypeError:
            return None

    extended_record = record_message['record']
    extended_record['_sdc_extracted_at'] = parse_datetime(record_message.get('time_extracted', datetime.now()))
    extended_record['_sdc_batched_at'] = datetime.now()
    extended_record['_sdc_deleted_at'] = parse_datetime(record_message.get('record', {}).get('_sdc_deleted_at'))

    return extended_record
