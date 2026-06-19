# Snowpark est le framework de transformation de données de Snowflake, 
#Snowpark est une bibliothèque Python de Snowflake qui permet de faire des transformations de données directement dans la plateforme, en utilisant une API type DataFrame.

# Et la Session est l’objet qui permet de se connecter à Snowflake et dexécuter ces transformations via Python.
# La Session Snowpark est l’objet principal qui représente la connexion à Snowflake et permet d’exécuter du SQL et des transformations de données via l’API Snowpark.

from snowflake.snowpark import Session

POS_TABLES = [
    "country",
    "franchise",
    "location",
    "menu",
    "truck",
    "order_header",
    "order_detail"
]

CUSTOMER_TABLES = ["customer_loyalty"]

TABLE_DICT = {
    "pos": {
        "schema": "HOL_DB.RAW_POS",
        "tables": POS_TABLES
    },
    "customer": {
        "schema": "HOL_DB.RAW_CUSTOMER",
        "tables": CUSTOMER_TABLES
    }
}


def load_raw_table(session, tname, s3dir=None, year=None, schema=None):
    session.use_schema(schema)
    if year is None:
        location = "@external.frostbyte_raw_stage/{}/{}/".format(s3dir, tname)
    else: 
        print("\tLoading year {}".format(year))
        location = "@external.frostbyte_raw_stage/{}/{}/year={}".format(s3dir, tname, year)

    # we can infer schema using the parquet read option
    df = session.read.option("compression", "snappy").parquet(location)
    df.copy_into_table("{}".format(tname))


def load_all_raw_tables(session):
    # WAIT_FOR_COMPLETION = TRUE 👉 signifie : “attends que le changement de taille soit terminé avant de continuer” ✔ important pour éviter les erreurs
    # .collect() sert de déclencheur 👉 force l’exécution 👉 Ça dit : “OK Snowflake, exécute vraiment cette commande SQL maintenant”
    _ = session.sql("ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = 'XLARGE' WAIT_FOR_COMPLETION = TRUE").collect()


    for s3dir, data in TABLE_DICT.items():
        schema = data["schema"]
        tnames = data["tables"]
        for tname in tnames:
            print("Loading table {} from S3 dir {}".format(tname, s3dir))
            # Only load the first 3 years of data for the order tables at this point
            # We will load the 2022 data later in the lab
            if tname in ["order_header", "order_detail"]:
                for year in [2019, 2020, 2021]:
                    load_raw_table(session, tname, s3dir=s3dir, year=year, schema=schema)
            else:
                load_raw_table(session, tname, s3dir=s3dir, schema=schema)

    _= session.sql("ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = 'SMALL' WAIT_FOR_COMPLETION = TRUE").collect()

def validate_raw_table(session):
    for tname in POS_TABLES:
        print("{}: \n\t{}\n".format(tname, session.table("RAW_POS.{}".format(tname)).columns))
    for tname in CUSTOMER_TABLES:
        print("{}: \n\t{}\n".format(tname, session.table("RAW_CUSTOMER.{}".format(tname)).columns))



# For local debugging
if __name__ =="__main__":
    # Create a local Snowpark session
    # 👉 with ouvre et gère automatiquement la ressource qui suit (fichier, session, connexion…)
    # ➡ il ouvre une SESSION Snowpark, donc une connexion active à Snowflake
    with Session.builder.getOrCreate() as session: 
        load_all_raw_tables(session)
        #validate_raw_table(session)