import copy
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

    stream_exists = True
    while stream_exists:
        # Call generate_dynamic_create_stream_query to get the query and stream_name
        create_stream_query, stream_name, stream_exists_query = common.create_stream(catalog_entry)

        # Execute the create_stream_query before defining insert_sql
        with snowflake_conn.connect_with_backoff() as open_conn:
            with open_conn.cursor() as cur:
                cur.execute(stream_exists_query)
                stream_exists = cur.fetchone() is not None
                if not stream_exists:
                    cur.execute(create_stream_query)

    select_sql = common.generate_select_sql(catalog_entry, columns)
    stream_columns = copy.copy(columns)
    stream_columns.append('METADATA$ACTION')
    stream_columns.append('METADATA$ISUPDATE')
    select_stream_sql = common.generate_select_sql(catalog_entry, stream_columns)
    select_stream_sql = stream_name.join(select_stream_sql.rsplit(f'"{catalog_entry.table}"', 1))

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
                              replication_method)

        # Call sync_query for select_stream_sql (LOG_BASED/CDC)
        schema_sdc_deleted_at = Schema(inclusion='available')
        schema_sdc_deleted_at.type = ['null', 'string']
        schema_sdc_deleted_at.format = 'date-time'
        catalog_entry.schema.properties['_sdc_deleted_at'] = schema_sdc_deleted_at
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
                                  stream_name=stream_name)
