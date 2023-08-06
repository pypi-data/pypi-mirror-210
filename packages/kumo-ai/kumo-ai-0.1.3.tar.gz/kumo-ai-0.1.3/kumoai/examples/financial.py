import logging
import os
import sys
from typing import Dict

from kumoai.client import KumoClient
from kumoai.datamodel.data_source import (DataSourceType,
                                          SnowflakeConnectorArgs,
                                          SnowflakeConnectorResourceConfig,
                                          UsernamePassword)
from kumoai.datamodel.json_serde import to_json
from kumoai.datamodel.pquery import (ColumnKey, ColumnKeyGroup,
                                     GraphDefinition, PQueryResource,
                                     SourceTableInfo, TableName)

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger(__name__)

kumo_client = KumoClient.from_env()


# List FINANCIAL source tables from snowflake.
def _financial_source_tables_snowflake() -> Dict[TableName, SourceTableInfo]:
    connector = SnowflakeConnectorArgs(
        config=SnowflakeConnectorResourceConfig(
            name='snowflake_connector',
            account='xva19026',
            warehouse='WH_XS',
            database='KUMO',
            schema_name='FINANCIAL',
        ),
        credentials=UsernamePassword(
            username=os.environ['SNOWFLAKE_USER'],
            password=os.environ['SNOWFLAKE_PASSWORD']),
    )
    # Create the connector if it doesn't exist.
    existing_connector = kumo_client.get_snowflake_connector_if_exists(
        connector.config.name)
    if not existing_connector:
        kumo_client.create_snowflake_connector(connector)
    else:
        # Or if it exists, ensure it's the same connector.
        assert existing_connector.config == connector.config

    source_table_list = kumo_client.list_snowflake_source_tables(
        connector.config.name)
    return {t.source_table.table: t for t in source_table_list}


# List FINANCIAL source tables from S3.
def _financial_source_tables_s3() -> Dict[TableName, SourceTableInfo]:
    source_table_list = kumo_client.list_s3_source_tables(
        s3_dir='s3://kumo-public-datasets/financial/parquet')
    return {t.source_table.table: t for t in source_table_list}


# Make a Predictive Query to run binary classification on FINANCIAL data graph
def make_financial_pquery(data_source_type: DataSourceType) -> str:
    pquery_name = f'financial_binary_classify_{data_source_type}'
    if data_source_type == DataSourceType.SNOWFLAKE:
        tables = _financial_source_tables_snowflake()
    elif data_source_type == DataSourceType.S3:
        tables = _financial_source_tables_s3()
    else:
        raise Exception(f'Unsupported data source type: {data_source_type}')

    graph = GraphDefinition(tables={}, col_groups=[])
    graph.tables['DISTRICT'] = tables['DISTRICT'].as_dim_table('DISTRICT_ID')
    graph.tables['TRANS'] = tables['TRANS'].as_fact_table(pkey_col='TRANS_ID')
    graph.tables['LOAN'] = tables['LOAN'].as_fact_table(pkey_col='LOAN_ID')
    graph.tables['ORDERS'] = tables['ORDERS'].as_dim_table('ORDERS_ID')
    graph.tables['CLIENT'] = tables['CLIENT'].as_dim_table('CLIENT_ID')
    graph.tables['DISP'] = tables['DISP'].as_dim_table('DISP_ID')
    graph.tables['CARD'] = tables['CARD'].as_dim_table('CARD_ID')
    graph.tables['ACCOUNT'] = tables['ACCOUNT'].as_dim_table('ACCOUNT_ID')
    graph.col_groups.append(
        ColumnKeyGroup(columns=[
            ColumnKey(table_name='DISTRICT', col_name='DISTRICT_ID'),
            ColumnKey(table_name='ACCOUNT', col_name='DISTRICT_ID'),
            ColumnKey(table_name='CLIENT', col_name='DISTRICT_ID')
        ]))
    graph.col_groups.append(
        ColumnKeyGroup(columns=[
            ColumnKey(table_name='CLIENT', col_name='CLIENT_ID'),
            ColumnKey(table_name='DISP', col_name='CLIENT_ID')
        ]))
    graph.col_groups.append(
        ColumnKeyGroup(columns=[
            ColumnKey(table_name='ACCOUNT', col_name='ACCOUNT_ID'),
            ColumnKey(table_name='DISP', col_name='ACCOUNT_ID'),
            ColumnKey(table_name='LOAN', col_name='ACCOUNT_ID'),
            ColumnKey(table_name='ORDERS', col_name='ACCOUNT_ID'),
            ColumnKey(table_name='TRANS', col_name='ACCOUNT_ID'),
        ]))
    pquery = PQueryResource(
        name=pquery_name,
        graph=graph,
        graph_display_name=f'financial_graph_{data_source_type}',
        query_yaml="entity: TRANS.TRANS_ID\ntarget: TRANS.K_SYMBOL = 'DUCHOD'")

    query_json_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), f'{pquery.name}.json')
    with open(query_json_file_path, 'w') as file:
        file.write(to_json(pquery))
        logger.info('Saved %s to file: %s', pquery.name, query_json_file_path)

    kumo_client.create_pquery(pquery)
    return pquery_name
