from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
import sys 

# Vérifie l’existence d’une table dans Snowflake via INFORMATION_SCHEMA
# Retourne un booléen (True si la table existe, sinon False)
# .collect() → exécute la requête et renvoie une liste de lignes
# [0] → récupère la première ligne du résultat
# ["TABLE_EXISTS"] → extrait la colonne contenant le booléen
def table_exists(session, schema='', tname=''):
    exists = session.sql("""
                SELECT EXISTS (
                    SELECT * 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = '{}'
                    AND TABLE_NAME = '{}'
                )
                AS TABLE_EXISTS
            """.format(schema, tname)).collect()[0]['TABLE_EXISTS']

    return exists

    exists = session.sql("SELECT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}') AS TABLE_EXISTS".format(schema, name)).collect()[0]['TABLE_EXISTS']


def create_orders_table(session):
    _ = session.sql("""
            CREATE TABLE IF NOT EXISTS HARMONIZED.ORDERS 
            LIKE HARMONIZED.POS_FLATTENED_V
        """).collect()
    
    _ = session.sql("""
            ALTER TABLE HARMONIZED.ORDERS 
            ADD COLUMN META_UPDATED_AT TIMESTAMP
        """).collect()

def create_orders_stream(session):
    _ = session.sql("""
            CREATE OR REPLACE STREAM HARMONIZED.ORDERS_STREAMS
            ON TABLE HARMONIZED.ORDERS
        """).collect()

def merge_orders_updates(session):
    _ = session.sql("""
            ALTER WAREHOUSE HOL_WH 
            SET WAREHOUSE_SIZE = XLARGE
            WAIT_FOR_COMPLETION = TRUE 
    """)

    source = session.table("HARMONIZED.POS_FLATTENED_V_STREAM")
    target = session.table("HARMONIZED.ORDERS")

    cols_to_update = {
        c: source[c]
        for c in source.schema.names
        if "METADATA" not in c
    }
    metadata_col_to_update = { "META_UPDATED_AT": F.current_timestamp()}
    updates = {**cols_to_update, **metadata_col_to_update}

    # Syntax : target.merge(source, condition, actions)
    target.merge(
        source,
        target["ORDER_DETAIL_ID"] == source["ORDER_DETAIL_ID"],
        [
            F.when_matched().update(updates),
            F.when_not_matched().insert(updates)
        ]
    )

    _ = session.sql("""
            ALTER WAREHOUSE HOL_WH 
            SET WAREHOUSE_SIZE = XSMAL
            WAIT_FOR_COMPLETION = TRUE 
    """)

def stored_procedure(session):

    if not table_exists(session, schema='HARMONIZED', tname='ORDERS'):
        create_orders_table(session)
        create_orders_stream(session)

    merge_orders_updates(session)

    return "Successfully processed ORDERS"

# For local debugging
if __name__ == "__main__":

    with Session.builder.getOrCreate() as session:

        session.use_database("HOL_DB")
        session.use_schema("HARMONIZED")

        if len(sys.argv) == 1:
            result = stored_procedure(session)
            print(result)
        else:
            print("Usage: python procedure.py")

