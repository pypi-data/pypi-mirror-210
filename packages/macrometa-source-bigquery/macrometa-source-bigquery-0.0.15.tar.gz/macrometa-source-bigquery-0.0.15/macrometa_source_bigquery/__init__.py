#!/usr/bin/env python3
import argparse, datetime, os
import pkg_resources
import simplejson as json

from c8connector import (
    C8Connector, ConfigProperty, Sample, Schema,
    ConfigAttributeType, SchemaAttributeType, SchemaAttribute)
import singer
from singer import utils as singer_utils
from singer import metadata
from singer.catalog import Catalog

from macrometa_source_bigquery.sample_data import fetch_samples, modify_reserved_keys
from macrometa_source_bigquery import sync_bigquery as source


REQUIRED_CONFIG_KEYS = ["table", "credentials_file", "project"]

LOGGER = singer.get_logger("macrometa_source_bigquery")


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


# Load schemas from schemas folder
def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas


def discover(config):
    streams = []

    # Restructuring streams
    configs = [
        {
            "name": config['table'],
            "table": config['table']
        }
    ]

    if config.get('datetime_key'):
        configs[0]['datetime_key'] = config['datetime_key']
    if config.get('filters'):
        filters = config['filters'].split(',')
        for item in filters:
            item.strip()
        configs[0]['filters'] = filters
    if config.get('columns', '*'):
        columns = config['columns'].split(',')
        for item in columns:
            item.strip()
        configs[0]['columns'] = columns

    add_timestamp = config.get('add_extracted_timestamp', False)
    for stream in configs:
        stream_metadata, stream_key_properties, schema = source.do_discover(
            config,
            stream,
            add_timestamp)

        # create and add catalog entry
        catalog_entry = {
            'stream': stream["name"],
            'tap_stream_id': stream["name"],
            'schema': schema,
            'metadata': stream_metadata,
            'key_properties': stream_key_properties
        }
        streams.append(catalog_entry)

    return {'streams': streams}


def _get_selected_streams(catalog):
    '''
    Gets selected streams.  Checks schema's 'selected' first (legacy)
    and then checks metadata (current), looking for an empty breadcrumb
    and mdata with a 'selected' entry
    '''
    selected_streams = []
    for stream in catalog.streams:
        stream_metadata = metadata.to_map(stream.metadata)
        # stream metadata will have an empty breadcrumb
        if metadata.get(stream_metadata, (), "selected"):
            selected_streams.append(stream.tap_stream_id)

    return selected_streams


def sync(config, state, catalog):
    selected_stream_ids = _get_selected_streams(catalog)
    # Loop over streams in catalog
    for stream in catalog.streams:
        stream_id = stream.tap_stream_id
        stream_schema = stream.schema
        if stream_id in selected_stream_ids:
            source.do_sync(config, state, stream)
            LOGGER.info('Syncing stream:' + stream_id)
    return


def parse_args():
    ''' This is to replace singer's default singer_utils.parse_args()
    https://github.com/singer-io/singer-python/blob/master/singer/utils.py

    Parse standard command-line args.
    Parses the command-line arguments mentioned in the SPEC and the
    BEST_PRACTICES documents:
    -c,--config     Config file
    -s,--state      State file
    -d,--discover   Run in discover mode
    --catalog       Catalog file
    Returns the parsed args object from argparse. For each argument that
    point to JSON files (config, state, properties), we will automatically
    load and parse the JSON file.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-s', '--state',
        help='State file')

    parser.add_argument(
        '-p', '--properties',
        help='Property selections: DEPRECATED, Please use --catalog instead')

    parser.add_argument(
        '--catalog',
        help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')

    # Capture additional args
    parser.add_argument(
        "--start_datetime", type=str,
        help="Inclusive start date time in ISO8601-Date-String format: 2019-04-11T00:00:00Z")
    parser.add_argument(
        "--end_datetime", type=str,
        help="Exclusive end date time in ISO8601-Date-String format: 2019-04-12T00:00:00Z")

    args = parser.parse_args()
    if args.config:
        args.config = singer_utils.load_json(args.config)
    if args.state:
        args.state = singer_utils.load_json(args.state)
    else:
        args.state = {}
    if args.properties:
        args.properties = singer_utils.load_json(args.properties)
    if args.catalog:
        args.catalog = Catalog.load(args.catalog)

    return args


def main_impl():
    args = singer_utils.parse_args(REQUIRED_CONFIG_KEYS)
    conn_config = {}
    conn_config.update(args.config)

    # Overwrite config specs with commandline args
    args_dict = args.__dict__
    for arg in args_dict.keys():
        if arg in conn_config.keys() and args_dict[arg] is None:
            continue
        conn_config[arg] = args_dict[arg]

    if not conn_config.get("end_datetime"):
        conn_config["end_datetime"] = datetime.datetime.utcnow().isoformat()

    try:
        conn_config = source.create_credentials_file(conn_config)
        # if not conn_config.get("start_datetime") and not conn_config.get("state"):
        #     LOGGER.error("state or start_datetime must be specified")
        #     return

        # If discover flag was passed, run discovery mode and dump output to stdout
        if args.discover:
            catalog = discover(conn_config)
            print(json.dumps(catalog, indent=2))
        # Otherwise run in sync mode
        elif args.catalog:
            catalog = args.catalog
            sync(conn_config, args.state, catalog)
        else:
            LOGGER.critical("Catalog file not specified")
    except Exception as e:
        LOGGER.warn("Exception raised: %s", e)
        source.delete_credentials_file(conn_config)
        raise e
    source.delete_credentials_file(conn_config)
    return


class BigQuerySourceConnector(C8Connector):
    """BigQuerySourceConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "BigQuery"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-source-bigquery"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution('macrometa_source_bigquery').version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "source"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Source data from a BigQuery table."

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        config = self.get_config(integration)
        try:
            config = source.create_credentials_file(config)
            discover(config)
        except Exception as e:
            LOGGER.warn("Exception raised: %s", e)
            source.delete_credentials_file(config)
            raise e
        source.delete_credentials_file(config)

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the provided configurations."""
        config = self.get_config(integration)
        try:
            config = source.create_credentials_file(config)
            streams = discover(config)['streams']
            results = []
            for stream in streams:
                s_attribs = []
                s_schema = stream['schema']

                data = fetch_samples(config, stream)[:10]
                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                if stream['metadata'][0]['metadata'].get('table-key-properties'):
                    key_properties = stream['metadata'][0]['metadata'].get('table-key-properties')
                    if key_properties[0] == '_key':
                        reserved_keys.remove('_key')
                s_schema['properties'] = modify_reserved_keys(s_schema['properties'], reserved_keys)

                for k, v in s_schema['properties'].items():
                    t = v['type'][-1]
                    s_attribs.append(SchemaAttribute(k, self.get_attribute_type(t)))
                schema = Schema(stream['stream'], s_attribs)
                results.append(Sample(
                    schema=schema,
                    data=data)
                )
        except Exception as e:
            LOGGER.warn("Exception raised: %s", e)
            source.delete_credentials_file(config)
            raise e
        source.delete_credentials_file(config)
        return results

    def schemas(self, integration: dict) -> list[Schema]:
        """Get supported schemas using the given configurations."""
        config = self.get_config(integration)
        try:
            config = source.create_credentials_file(config)
            streams = discover(config)['streams']
            results = []
            for stream in streams:
                s_attribs = []
                s_schema = stream['schema']

                # Appending _ to keys for preserving values of reserved keys in source data
                reserved_keys = ['_key', '_id', '_rev']
                if stream['metadata'][0]['metadata'].get('table-key-properties'):
                    key_properties = stream['metadata'][0]['metadata'].get('table-key-properties')
                    if key_properties[0] == '_key':
                        reserved_keys.remove('_key')
                s_schema['properties'] = modify_reserved_keys(s_schema['properties'], reserved_keys)

                for k, v in s_schema['properties'].items():
                    t = v['type'][-1]
                    s_attribs.append(SchemaAttribute(k, self.get_attribute_type(t)))
                results.append(Schema(stream['stream'], s_attribs))
        except Exception as e:
            LOGGER.warn("Exception raised: %s", e)
            source.delete_credentials_file(config)
            raise e
        source.delete_credentials_file(config)
        return results

    def reserved_keys(self) -> list[str]:
        """List of reserved keys for the connector."""
        return []

    @staticmethod
    def get_attribute_type(source_type: str) -> SchemaAttributeType:
        if source_type == 'string':
            return SchemaAttributeType.STRING
        elif source_type == 'integer':
            return SchemaAttributeType.LONG
        elif source_type == 'boolean':
            return SchemaAttributeType.BOOLEAN
        elif source_type == 'number':
            return SchemaAttributeType.DOUBLE
        else:
            return SchemaAttributeType.OBJECT

    def config(self) -> list[ConfigProperty]:
        """Get configuration parameters for the connector."""
        return [
            ConfigProperty('project', 'Project ID', ConfigAttributeType.STRING, True, False,
                           description='Your BigQuery project ID.',
                           placeholder_value='my_project_id'),
            ConfigProperty('table', 'Table', ConfigAttributeType.STRING, True, True,
                           description='Fully qualified table name in BigQuery, with format '
                                       '<project>.<dataset>.<table>',
                           placeholder_value='my_project.my_dataset.my_table'),
            ConfigProperty('credentials_file', 'Credentials JSON file', ConfigAttributeType.FILE, True, False,
                           description='Content of the credentials.json file for your service account. '
                                       'See the "Activate the Google BigQuery API" section of the repository\'s'
                                       'README and https://cloud.google.com/docs/authentication/production.',
                           placeholder_value='credentials.json contents'),
            ConfigProperty('columns', 'Columns', ConfigAttributeType.STRING, False, True,
                           description='Comma-separated list of columns to be selected. Use "*" to select all columns',
                           default_value='*'),
            ConfigProperty('primary_key', 'Unique Primary Key (to be used as _key for the collection)',
                           ConfigAttributeType.STRING, False, True,
                           description='A unique primary key from the bigquery table which needs be used as _key for '
                                       'the collection.'
                                       ' If the columns does not have any column with unique values then do not '
                                       'specify anything here,'
                                       ' _key for the collection will be autogenerated in this case. Primary key is '
                                       'case sensitive.',
                           placeholder_value='my_primary_key'),
            ConfigProperty('filters', 'Filters', ConfigAttributeType.STRING, False, True,
                           description='Comma-separated list of WHERE clauses to filter extracted data, '
                                       'e.g. "column=\'value\'".',
                           placeholder_value='my_filters'),
            ConfigProperty('add_extracted_timestamp', 'Add Extracted Timestamp', ConfigAttributeType.BOOLEAN,
                           False, False,
                           description='If true adds metadata `_sdc_extracted_at`. The timestamp of the record'
                                       ' when it was extracted from the source.',
                           default_value='false'),
            ConfigProperty('limit', 'Limit', ConfigAttributeType.INT, False, False,
                           description='Limits the number of records returned, applied as a limit in the query.',
                           placeholder_value='1000')
        ]

    def capabilities(self) -> list[str]:
        """Return the capabilities[1] of the connector.
        [1] https://docs.meltano.com/contribute/plugins#how-to-test-a-tap
        """
        return ['catalog', 'discover', 'state']

    @staticmethod
    def get_config(integration: dict) -> dict:
        try:
            return {
                # Required config keys
                'project': integration['project'],
                'table': integration['table'],
                'credentials_file': integration['credentials_file'],
                # Optional config keys
                'columns': integration.get('columns', '*'),
                'primary_key': integration.get('primary_key'),
                'datetime_key': integration.get('datetime_key'),
                'filters': integration.get('filters'),
                'start_datetime': integration.get('start_datetime'),
                'end_datetime': integration.get('end_datetime'),
                'add_extracted_timestamp': integration.get('add_extracted_timestamp', False),
                'limit': integration.get('limit'),
                'start_always_inclusive': integration.get('start_always_inclusive', True),
            }
        except KeyError as e:
            raise KeyError(f'Integration property `{e}` not found.')


def main():
    """
    main
    """
    try:
        main_impl()
    except Exception as exc:
        LOGGER.critical(exc)
        raise exc
