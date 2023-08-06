import dateutil.parser
import datetime
import singer

from singer import utils
from google.oauth2 import service_account
from google.cloud import bigquery
from singer import metadata
from macrometa_source_bigquery.sync_bigquery import _build_query, row_to_record, should_sync_column


def fetch_table(conn_info, stream):
    samples = []
    credentials = service_account.Credentials.from_service_account_file(conn_info['credentials_file'])
    client = bigquery.Client(project=conn_info['project'], credentials=credentials)

    start_datetime = None
    if conn_info.get("start_datetime"):
        start_datetime = dateutil.parser.parse(
            conn_info.get("start_datetime")).strftime("%Y-%m-%d %H:%M:%S.%f")

    end_datetime = None
    if conn_info.get("end_datetime"):
        end_datetime = dateutil.parser.parse(
            conn_info.get("end_datetime")).strftime("%Y-%m-%d %H:%M:%S.%f")

    keys = {"table": conn_info["table"],
            "columns": conn_info["columns"],
            "datetime_key": conn_info.get("datetime_key"),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
            }

    query = _build_query(keys, conn_info.get("filters", []),
                         limit=10)
    query_job = client.query(query)
    properties = stream['schema']['properties']
    extract_tstamp = datetime.datetime.utcnow()
    extract_tstamp = extract_tstamp.replace(tzinfo=datetime.timezone.utc)
    for row in query_job:
        record = row_to_record(row, properties, extract_tstamp, use_dict=True)
        rec_msg = singer.RecordMessage(
            stream=stream['stream'],
            record=record,
            version=None,
            time_extracted=utils.now())
        samples.append(rec_msg.record)
    return samples


def fetch_samples(conn_config, stream):
    """
    Fetch samples for the stream.
    """
    md_map = metadata.to_map(stream['metadata'])
    desired_columns = [c for c in stream['schema']['properties'].keys() if should_sync_column(md_map, c)]
    desired_columns.sort()
    if len(desired_columns) == 0:
        # There are no columns selected for stream. So, skipping it.
        return []
    state = fetch_table(conn_config, stream)

    # Appending _ to keys for preserving values of reserved keys in source data
    reserved_keys = ['_key', '_id', '_rev']
    if md_map.get((), {}).get('table-key-properties'):
        key_properties = md_map.get((), {}).get('table-key-properties')
        if key_properties[0] == '_key':
            reserved_keys.remove('_key')
    columns = set(desired_columns)
    if any(key in columns for key in reserved_keys):
        for record in state:
            record = modify_reserved_keys(record, reserved_keys)

    return state


def modify_reserved_keys(record, reserved_keys):
    for reserved_key in reserved_keys:
        if record.get(reserved_key):
            new_key = "_" + reserved_key
            while True:
                if record.get(new_key):
                    new_key = "_" + new_key
                else:
                    break
            record[new_key] = record.pop(reserved_key)
    return record
