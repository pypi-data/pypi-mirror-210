import singer
import macrometa_source_snowflake.sync_strategies.common as common
from singer.schema import Schema

LOGGER = singer.get_logger('macrometa_source_snowflake')

BOOKMARK_KEYS = {'replication_key', 'replication_key_value', 'version'}


def sync_table(snowflake_conn, catalog_entry, state, columns, replication_method):
    """Sync table using CDC-like approach"""
    common.whitelist_bookmark_keys(
        BOOKMARK_KEYS, catalog_entry.tap_stream_id, state)

    stream_version = common.get_stream_version(
        catalog_entry.tap_stream_id, state)
    state = singer.write_bookmark(state,
                                  catalog_entry.tap_stream_id,
                                  'version',
                                  stream_version)

    activate_version_message = singer.ActivateVersionMessage(
        stream=catalog_entry.stream,
        version=stream_version
    )

    singer.write_message(activate_version_message)

    # Call generate_dynamic_create_stream_query to get the query and stream_name
    create_stream_query, stream_name = common.create_stream(catalog_entry)

    # Execute the create_stream_query before defining insert_sql
    with snowflake_conn.connect_with_backoff() as open_conn:
        with open_conn.cursor() as cur:
            cur.execute(create_stream_query)

    select_sql = common.generate_select_sql(catalog_entry, columns)
    select_stream_sql = common.select_all_from_stream_query(
        catalog_entry, stream_name, columns)

    params = {}
    with snowflake_conn.connect_with_backoff() as open_conn:
        # Call sync_query for select_sql (data insertion)
        with open_conn.cursor() as cur:
            common.sync_query(cur,
                              catalog_entry,
                              state,
                              select_sql,
                              columns,
                              stream_version,
                              params,
                              replication_method,
                              snowflake_conn)

        # Call sync_query for select_stream_sql (LOG_BASED/CDC)
        schema = Schema(inclusion='available')
        schema.type = ['null', 'string']
        schema.format = 'date-time'
        catalog_entry.schema.properties['_sdc_deleted_at'] = schema
        common.write_schema_message(catalog_entry)

        while True:
            with open_conn.cursor() as cur:
                common.sync_query(cur,
                                  catalog_entry,
                                  state,
                                  select_stream_sql,
                                  columns,
                                  stream_version,
                                  params,
                                  replication_method,
                                  snowflake_conn)
