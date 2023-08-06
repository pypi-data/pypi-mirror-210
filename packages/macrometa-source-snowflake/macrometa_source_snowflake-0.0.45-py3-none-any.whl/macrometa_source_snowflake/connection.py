#!/usr/bin/env python3
import uuid
from typing import Union, List, Dict
from pathlib import Path

import singer
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import snowflake.connector

LOGGER = singer.get_logger('macrometa_source_snowflake')


class TooManyRecordsException(Exception):
    """Exception to raise when query returns more records than max_records"""


def validate_config(config):
    """Validate configuration dictionary"""
    errors = []
    required_config_keys = [
        'account',
        'dbname',
        'user',
        'warehouse',
        'table'
    ]

    # Check if mandatory keys exist
    for k in required_config_keys:
        if not config.get(k, None):
            errors.append(f'Required key is missing from config: [{k}]')

    possible_authentication_keys = [
        'password',
        'private_key_path'
    ]
    if not any(config.get(k, None) for k in possible_authentication_keys):
        errors.append(
            f'Required authentication key missing. Existing methods: {",".join(possible_authentication_keys)}')

    return errors

# PRIVATE KEY PATH


def create_private_key_file(config: Dict) -> Dict:
    path_uuid = uuid.uuid4().hex
    try:
        if config.get('private_key_path'):
            path = f"/opt/snowflake/{path_uuid}/rsa_key.p8"
            private_key = Path(path)
            private_key.parent.mkdir(exist_ok=True, parents=True)
            private_key.write_text(
                create_private_key_string(config['private_key_path']))
            config['private_key_path'] = path
            LOGGER.info(f"Private key file created at: {path}")

    except Exception as e:
        LOGGER.warn(
            f'Failed to create private key: /opt/snowflake/{path_uuid}/rsa_key.p8')

    return config


def delete_private_key_file(config: Dict) -> None:
    try:
        private_key = None
        if config.get('private_key_path'):
            path = config['private_key_path']
            private_key = Path(path)
            config['private_key_path'] = private_key.read_text()
            private_key.unlink()
            LOGGER.info(f"Private key file deleted from: {path}")

        if private_key is not None:
            private_key.parent.rmdir()
    except Exception as e:
        LOGGER.warn(f"Failed to delete private key file: {e}")


def create_private_key_string(private_key_string: str) -> str:
    private_key_list = []
    split_string = private_key_string.split("-----")
    if len(split_string) < 4:
        raise Exception("Invalid PEM format for private key.")
    for i in range(len(split_string)):
        if ((i % 2) == 1):
            private_key_list.extend(("-----", split_string[i], "-----"))
        else:
            private_key_list.append(split_string[i].replace(' ', '\n'))

    return ''.join(private_key_list)


class SnowflakeConnection:
    """Class to manage connection to snowflake data warehouse"""

    def __init__(self, connection_config):
        """
        connection_config:      Snowflake connection details
        """
        self.connection_config = connection_config
        config_errors = validate_config(connection_config)
        if len(config_errors) == 0:
            self.connection_config = connection_config
        else:
            LOGGER.error('Invalid configuration:\n   * %s',
                         '\n   * '.join(config_errors))
            sys.exit(1)

    def get_private_key(self):
        """
        Get private key from the right location
        """
        if self.connection_config.get('private_key_path'):
            try:
                encoded_passphrase = self.connection_config['private_key_passphrase'].encode(
                )
            except KeyError:
                encoded_passphrase = None

            with open(self.connection_config['private_key_path'], 'rb') as key:
                p_key = serialization.load_pem_private_key(
                    key.read(),
                    password=encoded_passphrase,
                    backend=default_backend()
                )

            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())
            return pkb

        return None

    def open_connection(self):
        """Connect to snowflake database"""
        return snowflake.connector.connect(
            user=self.connection_config['user'],
            password=self.connection_config.get('password', None),
            private_key=self.get_private_key(),
            account=self.connection_config['account'],
            database=self.connection_config['dbname'],
            warehouse=self.connection_config['warehouse'],
            role=self.connection_config.get('role', None),
            insecure_mode=self.connection_config.get('insecure_mode', False)
            # Use insecure mode to avoid "Failed to get OCSP response" warnings
            # insecure_mode=True
        )

    # Retry logic has been removed as we were experiencing some issues
    # TODO: Revisit the retry logic which was implemented using backoff
    def connect_with_backoff(self):
        """Connect to snowflake database and retry automatically a few times if fails"""
        return self.open_connection()

    def query(self, query: Union[List[str], str], params: Dict = None, max_records=0):
        """Run a query in snowflake"""
        result = []

        if params is None:
            params = {}
        else:
            if 'LAST_QID' in params:
                LOGGER.warning('LAST_QID is a reserved prepared statement parameter name, '
                               'it will be overridden with each executed query!')

        with self.connect_with_backoff() as connection:
            with connection.cursor(snowflake.connector.DictCursor) as cur:

                # Run every query in one transaction if query is a list of SQL
                if isinstance(query, list):
                    cur.execute('START TRANSACTION')
                    queries = query
                else:
                    queries = [query]

                qid = None

                for sql in queries:
                    LOGGER.debug('Running query: %s', sql)

                    # update the LAST_QID
                    params['LAST_QID'] = qid

                    cur.execute(sql, params)
                    qid = cur.sfqid

                    # Raise exception if returned rows greater than max allowed records
                    if 0 < max_records < cur.rowcount:
                        raise TooManyRecordsException(
                            f'Query returned too many records. This query can return max {max_records} records')

                    if cur.rowcount > 0:
                        result = cur.fetchall()

        return result
