import logging
import os
import sys

from examples.orchestration import run_training_job

from kumoai.client import KumoClient
from kumoai.datamodel.json_serde import from_json, to_json
from kumoai.datamodel.pquery import Column, PQueryResource, SemanticType

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger(__name__)

kumo_client = KumoClient.from_env()


def save_pquery_as_json_file(pquery_name: str) -> str:
    """
    This example demonstrates how to save full definition of an existing
    PQuery to a json file.  The json file can serve as human reviewable
    archive checked into repository, or server as backup in case of accidental
    deletion or editing of the original PQuery.
    """
    pquery = kumo_client.get_pquery(pquery_name)
    query_json_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), f'{pquery_name}.json')
    with open(query_json_file_path, 'w') as file:
        file.write(to_json(pquery))
    return query_json_file_path


def save_and_load_query_as_json_file():
    """
    This example demonstrates how to save the full definition of an existing
    predictive query "my_predictive_query" as json file for backup. When the
    query gets accidentally deleted, we can upload the json to recreate the
    same query (but untrained).
    """
    # We have already saved a churn prediction query over H&M dataset as
    # "hm_churn.json" file that's checked into the current directory.
    query_json_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'hm_churn.json')

    # Simulate that the query "hm_churn" accidentally got force deleted.
    kumo_client.delete_pquery_if_exists('hm_churn', force_delete_all_jobs=True)

    # We can load the query definition from the json file and recreate it.
    with open(query_json_file_path, 'r') as file:
        pquery_resource = from_json(file.read(), PQueryResource)

    # Now we have re-created the same original PQuery, in an UNTRAINED state.
    kumo_client.create_pquery(pquery_resource)
    # Kick off training on the newly created PQuery.
    run_training_job(pquery_resource.name)


def copy_and_create_new_query():
    """
    This example demonstrates how we can start from an existing predictive
    query, make a few changes, and create a new query.
    """
    # Example 1: reuse the same graph, but write a different query yaml
    query1 = kumo_client.get_pquery('hm_churn')
    query1.name = "hm_ltv"
    query1.query_yaml = """
entity: customers.customer_id\nwhatif: COUNT(transactions_train.*, 0, 90)
 > 0\ntarget: SUM(transactions_train.price, 0, 90) = 0
"""
    # Create the new pquery in Kumo Cloud
    kumo_client.create_pquery(query1)
    run_training_job(query1.name)  # Launch training for the new query!

    # Example 2: reuse the same query yaml but modify the graph/table
    query2 = kumo_client.get_pquery('hm_churn')
    query2.name = 'hm_churn2'
    query2.graph_display_name = 'modified_hm_graph'
    query2.graph.tables['transactions_train'].time_col = 't_dat'
    query2.graph.tables['transactions_train'].cols.append(
        Column(name='t_dat', stype=SemanticType.timestamp))
    # Create the new pquery in Kumo Cloud
    kumo_client.create_pquery(query2)
    run_training_job(query2.name)  # Launch training for the new query!
