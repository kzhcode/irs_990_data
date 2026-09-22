# IRS 990 Data Pipeline
 
An end-to-end data engineering project that extracts nonprofit financial and organizational data
from IRS Form 990 filings, transforms it with Python, and loads it into PostgreSQL. The pipeline
runs inside Docker and is orchestrated with Apache Airflow.
 
Scope is limited to exempt organizations in the Kansas City metro area (selected Kansas and
Missouri ZIP codes: Downtown, Midtown, East, South, Swope, Northland, Wyandotte County, Overland
Park, Olathe, Independence, Lee's Summit). Coverage of other states can be added later.
 
 
## Tech Stack
 
- Orchestration: Apache Airflow (LocalExecutor)
- Containerization: Docker, Docker Compose
- Database: PostgreSQL 16
- Language: Python
  - requests, beautifulsoup4 (web scraping and downloads)
  - pandas (tabular wrangling)
  - lxml (XML parsing with XPath)
  - zipfile-deflate64 (IRS ZIP archives use Deflate64 compression)
  - SQLAlchemy Core 1.4 + psycopg2 (database loading)
  - python-dotenv (configuration)
  - great-expectations (data quality checks)
 
 
## Project Structure
 
    .
    ├── .env                  # Postgres and Airflow configuration (not committed)
    ├── docker-compose.yml    # Postgres, airflow-init, webserver, scheduler services
    ├── Dockerfile            # Airflow image with project requirements
    ├── requirements.txt      # Python dependencies
    ├── db/
    │   └── init.sql          # Database schema, run on first Postgres start
    └── dags/
        ├── extract.py        # Download stage
        ├── transform.py      # Unzip, filter, and XML parsing stage
        ├── xml_paths.py      # XPath definitions for 990 / 990EZ / 990PF
        └── load.py           # Upsert stage into PostgreSQL
 
 
## Data Sources
 
- Exempt Organizations Business Master File Extract (EO BMF)
  https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
  Used to get the list of registered organizations (EINs) in Kansas and Missouri.
 
- Form 990 Series Downloads
  https://www.irs.gov/charities-non-profits/form-990-series-downloads
  Provides yearly index files (CSV) and batched ZIP archives of e-filed XML returns.
 
 
## Pipeline Stages
 
### 1. Extract (extract.py)
 
Downloads raw data from the IRS website into a Docker volume mounted at /opt/airflow/data.
 
- dir_setup(): creates the ORIGINAL_* folders.
- irs_eo_bmf_extract(): scrapes the EO BMF page and downloads the Kansas and Missouri CSVs.
  Links are located by their data-entity-uuid attributes on the IRS page.
- irs_990_index_extract(): finds every "Index file for ..." link and saves each index CSV.
- irs_990_batch_extract(): finds every ZIP link and streams the batch archives to disk.
 
Output folders:
- ORIGINAL_EO_BMF_FILES/
- ORIGINAL_INDEX_FILES/
- ORIGINAL_990_FILES/
 
### 2. Transform (transform.py)
 
Filters the raw data down to target organizations and parses their XML returns into tables.
 
- dir_setup_edited(): creates the EDITED_* and EXTRACTED_XML_DATA folders.
- unzip_990_files(): extracts each batch ZIP into its own folder named after the batch.
- flatten_nested_990_files(): removes an extra nested folder level some IRS archives contain.
- transform_irs_eo_bmf(): combines KS and MO EO BMF data and filters by target ZIP codes.
- transform_irs_index(df_eo_bmf): filters index files to target EINs and to return types
  990, 990EZ, and 990PF. Normalizes column differences between index years.
- process_irs_index(df_index): normalizes SUB_DATE and splits rows into those with and
  without an XML_BATCH_ID.
- extract_xml_rec_with_id(): locates XML files directly by batch folder + OBJECT_ID.
- build_object_id_lookup() / extract_xml_rec_without_id(): fallback path for rows missing
  XML_BATCH_ID. Walks all unzipped folders once to build an OBJECT_ID -> file path lookup.
- combine_extracted_data(): merges both paths into org_records.csv and officer_records.csv.
- cleanup_edited_xml_dir(): deletes the unzipped XML folder (it can be regenerated from ZIPs).
 
Field mappings live in xml_paths.py, which maps output column names to XPath expressions for
each return type, using the IRS e-file namespace (http://www.irs.gov/efile).
 
Output folders:
- EDITED_EO_BMF_FILES/
- EDITED_INDEX_FILES/
- EXTRACTED_XML_DATA/
 
### 3. Load (load.py)
 
Prepares extracted records and upserts them into PostgreSQL.
 
- prepare_org_records(): cleans text casing, ZIP, phone, and EIN formats; splits records by
  return type; deduplicates organizations, keeping the most recent tax year.
- prepare_officer_records(): splits officer names into first and last names, drops rows with
  unparseable names, and deduplicates on the primary key.
- update_data_psql(): reflects each table with SQLAlchemy Core and runs
  INSERT ... ON CONFLICT DO UPDATE, so re-runs are idempotent. Updated rows are flagged with
  isUpdated, UpdateDate, and UpdateBy.
 
 
## Database Schema (db/init.sql)
 
- tb_organization: one row per organization (PK: OrgEin)
- tb_990_return: full Form 990 financials (PK: OrgEin, ObjectId, TaxYr)
- tb_990ez_return: Form 990-EZ financials (PK: OrgEin, ObjectId, TaxYr)
- tb_990pf_return: Form 990-PF (private foundation) financials (PK: OrgEin, ObjectId, TaxYr)
- tb_officer_salary: officer/director compensation from 990 and 990-EZ
  (PK: OrgEin, ObjectId, OfficerFirstName, OfficerLastName, TaxYr).
  Includes a generated EmployeeId column built from EIN, name, title, and tax year.
 
All return and officer tables reference tb_organization by OrgEin. Every table carries
CreateDate, isUpdated, UpdateDate, and UpdateBy audit columns.
 
 
## Known IRS Data Quirks
 
- Index files for some years (2019, 2020, 2022) lack XML_BATCH_ID values, so a separate
  lookup-based path is used to find those XML files.
- Index files differ in columns and SUB_DATE formats across years.
- Some batch ZIPs contain an extra nested directory.
- IRS ZIP archives use Deflate64 compression, which Python's standard zipfile does not support.
 
 
## Getting Started
 
Prerequisites: Docker and Docker Compose.
 
1. Clone the repository.
2. Create a .env file in the project root with the following variables:
   - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
   - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
   - AIRFLOW__CORE__EXECUTOR=LocalExecutor
   - AIRFLOW__CORE__LOAD_EXAMPLES=False
   - _AIRFLOW_WWW_USER_USERNAME, _AIRFLOW_WWW_USER_PASSWORD
3. Build and start the stack:
       docker compose up -d --build
4. Access services:
   - Airflow UI: http://localhost:8080
   - PostgreSQL: localhost:5433 (mapped to 5432 inside the container)
 
Running the stages manually inside the scheduler container:
 
       docker exec -it <scheduler-container> bash
       cd /opt/airflow/dags
       python extract.py
       python transform.py
       python load.py
 
Note: init.sql only runs when the Postgres volume is first created. To apply schema changes,
remove the postgres_data volume (docker compose down -v) and start again.
 
 
## Project Status
 
- Phase 1: Infrastructure (Docker, PostgreSQL, Airflow) ............ complete
- Phase 2: Core pipeline modules (extract, transform, load) ........ complete
- Phase 3: Airflow DAG orchestration ............................... complete
- Phase 4: Data quality and testing (Great Expectations) ........... complete
 
 
## Author
 
Kirill Zh
GitHub: https://github.com/kzhcode/irs_990_data