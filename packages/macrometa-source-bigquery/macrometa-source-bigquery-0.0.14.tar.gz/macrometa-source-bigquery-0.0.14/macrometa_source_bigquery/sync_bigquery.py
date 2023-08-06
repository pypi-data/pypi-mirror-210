import datetime, json, time
import dateutil.parser
from decimal import Decimal

import singer
import singer.metrics as metrics
import uuid

from google.oauth2 import service_account
from google.cloud import bigquery
from pathlib import Path
from typing import Dict

import getschema


LOGGER = singer.get_logger("macrometa_source_bigquery")

# StitchData compatible timestamp meta data
#  https://www.stitchdata.com/docs/data-structure/system-tables-and-columns
# The timestamp of the record extracted from the source
EXTRACT_TIMESTAMP = "_sdc_extracted_at"

BOOKMARK_KEY_NAME = "last_update"


def _build_query(keys, filters=[], inclusive_start=True, limit=None):
    columns = ",".join(keys["columns"])
    if keys.get("datetime_key"):
        if "*" not in columns and keys["datetime_key"] not in columns:
            columns = columns + "," + keys["datetime_key"]
    keys["columns"] = columns

    query = "SELECT {columns} FROM {table} WHERE 1=1".format(**keys)

    if filters:
        for f in filters:
            query = query + " AND " + f

    if keys.get("datetime_key") and keys.get("start_datetime"):
        if inclusive_start:
            query = (query +
                     (" AND datetime '{start_datetime}' <= " +
                      "CAST({datetime_key} as datetime)").format(**keys))
        else:
            query = (query +
                     (" AND datetime '{start_datetime}' < " +
                      "CAST({datetime_key} as datetime)").format(**keys))

    if keys.get("datetime_key") and keys.get("end_datetime"):
        query = (query +
                 (" AND CAST({datetime_key} as datetime) < " +
                  "datetime '{end_datetime}'").format(**keys))
    if keys.get("datetime_key"):
        query = (query + " ORDER BY {datetime_key}".format(**keys))

    if limit is not None:
        query = query + " LIMIT %d" % int(limit)

    return query


def do_discover(config, stream, output_schema_file=None,
                add_timestamp=False):
    credentials = service_account.Credentials.from_service_account_file(config['credentials_file'])
    client = bigquery.Client(project=config['project'], credentials=credentials)

    start_datetime = None
    if config.get("start_datetime"):
        start_datetime = dateutil.parser.parse(
            config.get("start_datetime")).strftime("%Y-%m-%d %H:%M:%S.%f")

    end_datetime = None
    if config.get("end_datetime"):
        end_datetime = dateutil.parser.parse(
            config.get("end_datetime")).strftime("%Y-%m-%d %H:%M:%S.%f")

    keys = {"table": stream["table"],
            "columns": stream["columns"],
            "datetime_key": stream.get("datetime_key"),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
            }
    limit = config.get("limit", 100)
    query = _build_query(keys, stream.get("filters"), limit=limit)

    LOGGER.info("Running query:\n    " + query)

    query_job = client.query(query)
    results = query_job.result()  # Waits for job to complete.

    data = []
    # Read everything upfront
    for row in results:
        record = {}
        for key in row.keys():
            record[key] = row[key]
        data.append(record)

    if not data:
        raise Exception("Cannot infer schema: No record returned.")

    schema = getschema.infer_schema(data)
    if add_timestamp:
        timestamp_format = {"type": ["null", "string"],
                            "format": "date-time"}
        schema["properties"][EXTRACT_TIMESTAMP] = timestamp_format

    if output_schema_file:
        with open(output_schema_file, "w") as f:
            json.dump(schema, f, indent=2)

    stream_metadata = [{
        "metadata": {
            "selected": True,
            "table": stream["table"],
            "columns": stream["columns"],
            "filters": stream.get("filters", []),
            "datetime_key": stream.get("datetime_key"),
            "table-key-properties": [config.get("primary_key")]
            # "inclusion": "available",
            # "valid-replication-keys": ["date_modified"],
            # "schema-name": "users"
            },
        "breadcrumb": []
        }]

    # Unique primary key provided by user
    key_properties = []
    if config.get("primary_key"):
        key_properties = [config.get("primary_key")]

    catalog = {"selected": True,
               "type": "object",
               "stream": stream["name"],
               "key_properties": key_properties,
               "properties": schema["properties"]
               }

    return stream_metadata, key_properties, catalog


def do_sync(config, state, stream):
    singer.set_currently_syncing(state, stream.tap_stream_id)
    singer.write_state(state)

    credentials = service_account.Credentials.from_service_account_file(config['credentials_file'])
    client = bigquery.Client(project=config['project'], credentials=credentials)
    metadata = stream.metadata[0]["metadata"]
    tap_stream_id = stream.tap_stream_id

    inclusive_start = True
    start_datetime = singer.get_bookmark(state, tap_stream_id,
                                         BOOKMARK_KEY_NAME)
    if start_datetime:
        if not config.get("start_always_inclusive"):
            inclusive_start = False
    else:
        start_datetime = config.get("start_datetime")
    if start_datetime:
        start_datetime = dateutil.parser.parse(start_datetime).strftime(
            "%Y-%m-%d %H:%M:%S.%f")

    if config.get("end_datetime"):
        end_datetime = dateutil.parser.parse(
            config.get("end_datetime")).strftime("%Y-%m-%d %H:%M:%S.%f")

    singer.write_schema(tap_stream_id, stream.schema.to_dict(),
                        stream.key_properties)

    keys = {"table": metadata["table"],
            "columns": metadata["columns"],
            "datetime_key": metadata.get("datetime_key"),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
            }

    limit = config.get("limit", None)
    query = _build_query(keys, metadata.get("filters", []), inclusive_start,
                         limit=limit)
    query_job = client.query(query)

    properties = stream.schema.properties
    last_update = start_datetime

    LOGGER.info("Running query:\n    %s" % query)

    extract_tstamp = datetime.datetime.utcnow()
    extract_tstamp = extract_tstamp.replace(tzinfo=datetime.timezone.utc)

    with metrics.record_counter(tap_stream_id) as counter:
        for row in query_job:
            record = row_to_record(row, properties, extract_tstamp)

            singer.write_record(stream.stream, record)

            last_update = record[keys["datetime_key"]] if "datetime_key" in keys and keys["datetime_key"] else ""
            counter.increment()

    state = singer.write_bookmark(state, tap_stream_id, BOOKMARK_KEY_NAME,
                                  last_update)

    singer.write_state(state)


def row_to_record(row, properties, extract_tstamp, use_dict=False):
    record = {}
    for key in properties.keys():
        prop = properties[key]

        if key == EXTRACT_TIMESTAMP:
            continue

        if row[key] is None:
            if (prop['type'][0] if use_dict else prop.type[0]) != "null":
                raise ValueError("NULL value not allowed by the schema")
            else:
                record[key] = None
        elif (prop.get('format') if use_dict else prop.format) == "date-time":
            if type(row[key]) == str:
                r = dateutil.parser.parse(row[key])
            elif type(row[key]) == datetime.date:
                r = datetime.datetime(year=row[key].year, month=row[key].month, day=row[key].day)
            elif type(row[key]) == datetime.datetime:
                r = row[key]
            record[key] = r.isoformat()
        elif (prop['type'][1] if use_dict else prop.type[1]) == "string":
            record[key] = str(row[key])
        elif (prop['type'][1] if use_dict else prop.type[1]) == "number":
            record[key] = Decimal(row[key])
        elif (prop['type'][1] if use_dict else prop.type[1]) == "integer":
            record[key] = int(row[key])
        else:
            record[key] = row[key]

    if EXTRACT_TIMESTAMP in properties.keys():
        record[EXTRACT_TIMESTAMP] = extract_tstamp.isoformat()

    return record


def should_sync_column(md_map, field_name):
    field_metadata = md_map.get(('properties', field_name), {})
    return singer.should_sync_field(field_metadata.get('inclusion'),
                                    field_metadata.get('selected'),
                                    True)


def create_credentials_file(config: Dict) -> Dict:
    path_uuid = uuid.uuid4().hex
    try:
        if config.get('credentials_file'):
            path = f"/opt/bigquery/{path_uuid}/client_secrets.json"
            client_secrets = Path(path)
            client_secrets.parent.mkdir(exist_ok=True, parents=True)
            client_secrets.write_text(config['credentials_file'])
            config['credentials_file'] = client_secrets
            LOGGER.info(f"Client credentials file created at: {path}")
    except Exception as e:
        LOGGER.warn(f"Failed to client credentials file: /opt/bigquery/{path_uuid}/. {e}")
    return config


def delete_credentials_file(config: Dict) -> None:
    try:
        if config.get('credentials_file'):
            path = config['credentials_file']
            client_secrets = Path(path)
            config['credentials_file'] = client_secrets.read_text()
            client_secrets.unlink()
            LOGGER.info(f"Client credentials file deleted from: {path}")
            client_secrets.parent.rmdir()
    except Exception as e:
        LOGGER.warn(f"Failed to delete client credentials file: {e}")
