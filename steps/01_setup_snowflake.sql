
-- ----------------------------------------------------------------------------
-- Step #2: Create the account level objects
-- ----------------------------------------------------------------------------

-- ACCOUNTADMIN : Administration totale du compte Snowflake   
USE ROLE ACCOUNTADMIN;

-- Roles
-- Stocke l'utilisateur courant dans une variable
-- Crée (ou recrée) le rôle HOL_ROLE
-- Permet à SYSADMIN d'hériter des privilèges de HOL_ROLE
-- Attribue HOL_ROLE à l'utilisateur courant
SET MY_USER = CURRENT_USER();
CREATE OR REPLACE ROLE HOL_ROLE;
GRANT ROLE HOL_ROLE TO ROLE SYSADMIN;
GRANT ROLE HOL_ROLE TO USER IDENTIFIER($MY_USER);


-- Autorise le rôle à exécuter des Tasks Snowflake
-- Autorise le rôle à consulter l'état et l'historique des exécutions
-- Donne accès aux vues système de la base SNOWFLAKE -- (ACCOUNT_USAGE, QUERY_HISTORY, etc.)
GRANT EXECUTE TASK ON ACCOUNT TO ROLE HOL_ROLE;
GRANT MONITOR EXECUTION ON ACCOUNT TO ROLE HOL_ROLE;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE HOL_ROLE;

--Databases
CREATE OR REPLACE DATABASE HOL_DB;
GRANT OWNERSHIP ON DATABASE HOL_DB TO ROLE HOL_ROLE;

--Warhouses
CREATE OR REPLACE WAREHOUSE HOL_WH WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

GRANT OWNERSHIP ON WAREHOUSE HOL_WH TO ROLE HOL_ROLE;

-- ----------------------------------------------------------------------------
-- Step #3: Create the database level objects
-- ----------------------------------------------------------------------------
CREATE OR REPLACE SCHEMA HOL_DB.EXTERNAL;
CREATE OR REPLACE SCHEMA HOL_DB.RAW_POS;
CREATE OR REPLACE SCHEMA HOL_DB.HARMONIZED;
CREATE OR REPLACE SCHEMA HOL_DB.RAW_CUSTOMER;
CREATE OR REPLACE SCHEMA HOL_DB.ANALYTICS;

USE SCHEMA HOL_DB.EXTERNAL;

CREATE OR REPLACE FILE FORMAT HOL_DB.EXTERNAL.PARQUET_FORMAT
    TYPE = 'PARQUET' -- un format de fichier colonnes (columnar)
    COMPRESSION = 'SNAPPY'; -- méthode de compression;

-- Un stage Snowflake est un objet qui pointe vers un stockage externe comme S3, permettant de charger des fichiers dans Snowflake sans les importer manuellemen
CREATE OR REPLACE STAGE HOL_DB.EXTERNAL.FROSTBYTE_RAW_STAGE
    URL = 's3://sfquickstarts/data-engineering-with-snowpark-python/';


USE SCHEMA HOL_DB.ANALYTICS;

-- User Defined Function (UDF) : sert à : convertir des pouces (inch) en millimètres (mm)
-- INCH : nom du paramètre d'entrée de la fonction
-- NUMBER(35,4)) : type de données du paramètre d'entrée (nombre avec 35 chiffres dont 4 après la virgule)  
CREATE OR REPLACE FUNCTION HOL_DB.ANALYTICS.INCH_TO_MILLIMETER_UDF(INCH NUMBER(35,4)) 
RETURNS NUMBER(35,4)
    AS
$$
    inch * 25.4
$$; 


-- This will be added in step 5
--CREATE OR REPLACE FUNCTION ANALYTICS.FAHRENHEIT_TO_CELSIUS_UDF(TEMP_F NUMBER(35,4))
--RETURNS NUMBER(35,4)
--AS
--$$
--    (temp_f - 32) * (5/9)
--$$;

