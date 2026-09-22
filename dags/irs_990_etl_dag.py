

"""
IRS 990 ETL DAG
 
Orchestrates extract.py -> transform.py -> load.py.
 
Design notes:
- Pipeline modules are imported INSIDE each task, not at the top of this file.
  The scheduler re-parses this file every ~30s; importing load.py at the top
  would execute its module-level read_csv calls on every parse.
- Tasks hand off file paths (small strings) via XCom, never DataFrames.
- Load runs as a single task so tb_organization is always written before the
  tables that reference it via foreign keys.
"""
 
from datetime import timedelta
import os
 
import pendulum
from airflow.decorators import dag, task, task_group
 
 
default_args = {
    "owner": "KMZ",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}
 
 
@dag(
    dag_id="irs_990_etl",
    description="Extract IRS EO BMF, index, and 990 XML data for KC metro nonprofits; transform; load to Postgres",
    schedule="@monthly",
    start_date=pendulum.datetime(2026, 9, 1, tz="America/Chicago"),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["irs_990", "etl"],
)
def irs_990_etl():
 
    # ------------------------------------------------------------------ #
    # EXTRACT
    # ------------------------------------------------------------------ #
    @task_group(group_id="extract")
    def extract_group():
 
        @task
        def setup_raw_dirs():
            import extract
            extract.dir_setup()
 
        @task
        def extract_eo_bmf():
            import extract
            extract.irs_eo_bmf_extract()
            return extract.IRS_EO_BMF_DIR
 
        @task
        def extract_index_files():
            import extract
            extract.irs_990_index_extract()
            return extract.IRS_INDEX_DIR
 
        @task(execution_timeout=timedelta(hours=6))
        def extract_990_batches():
            import extract
            extract.irs_990_batch_extract()
            return extract.IRS_990_DIR
 
        dirs = setup_raw_dirs()
        eo_bmf = extract_eo_bmf()
        index = extract_index_files()
        batches = extract_990_batches()
 
        # the three downloads are independent of each other
        dirs >> [eo_bmf, index, batches]
 
        return {"eo_bmf": eo_bmf, "index": index, "batches": batches}
 
    # ------------------------------------------------------------------ #
    # TRANSFORM
    # ------------------------------------------------------------------ #
    @task_group(group_id="transform")
    def transform_group(raw):
 
        @task
        def setup_edited_dirs():
            import transform
            transform.dir_setup_edited()
 
        @task(execution_timeout=timedelta(hours=3))
        def unzip_and_flatten(batches_dir: str):
            import transform
            print(f"Unzipping batches from {batches_dir}")
            transform.unzip_990_files()
            return transform.EDITED_IRS_990_DIR
 
        @task
        def build_filtered_index(eo_bmf_dir: str, index_dir: str):
            import transform
            print(f"Using EO BMF from {eo_bmf_dir} and index files from {index_dir}")
            df_eo_bmf = transform.transform_irs_eo_bmf()
            df_index = transform.transform_irs_index(df_eo_bmf)
            transform.process_irs_index(df_index)  # writes df_index_not_na.csv / df_index_na.csv
 
            return {
                "not_na": os.path.join(transform.EDITED_IRS_INDEX_DIR, "df_index_not_na.csv"),
                "na": os.path.join(transform.EDITED_IRS_INDEX_DIR, "df_index_na.csv"),
            }
 
        @task(execution_timeout=timedelta(hours=3))
        def extract_xml_records(index_paths: dict, xml_dir: str):
            import pandas
            import transform
            from xml_paths import NS
 
            print(f"Parsing XML files under {xml_dir}")
 
            # dtype=str keeps EINs / OBJECT_IDs as strings (leading zeros, long ids)
            df_index_not_na = pandas.read_csv(index_paths["not_na"], dtype=str)
            df_index_na = pandas.read_csv(index_paths["na"], dtype=str)
 
            object_id_lookup = transform.build_object_id_lookup()
            org_with, off_with = transform.extract_xml_rec_with_id(df_index_not_na, NS)
            org_without, off_without = transform.extract_xml_rec_without_id(df_index_na, object_id_lookup)
            transform.combine_extracted_data(org_with, off_with, org_without, off_without)
 
            return {
                "org": os.path.join(transform.EXTRACTED_XML_DATA, "org_records.csv"),
                "officer": os.path.join(transform.EXTRACTED_XML_DATA, "officer_records.csv"),
            }
 
        @task
        def cleanup_unzipped_xml():
            import transform
            transform.cleanup_edited_xml_dir()
 
        dirs = setup_edited_dirs()
        xml_dir = unzip_and_flatten(raw["batches"])
        index_paths = build_filtered_index(raw["eo_bmf"], raw["index"])
        dirs >> [xml_dir, index_paths]
 
        records = extract_xml_records(index_paths, xml_dir)
 
        # unzipped XML is only needed by extract_xml_records; load reads the CSVs
        records >> cleanup_unzipped_xml()
 
        return records
 
    # ------------------------------------------------------------------ #
    # LOAD
    # ------------------------------------------------------------------ #
    @task
    def load_to_postgres(record_paths: dict):
        # importing load here (at run time) is what triggers its module-level
        # read_csv of org_records.csv / officer_records.csv
        import load
 
        print(f"Loading {record_paths['org']} and {record_paths['officer']}")
 
        tb_organization, tb_990, tb_990ez, tb_990pf = load.prepare_org_records(load.org_records)
        tb_officer_salary = load.prepare_officer_records(load.officer_records, load.org_records)
 
        engine, metadata = load.psql_engine(
            "postgresql", "psycopg2",
            load.pg_user, load.pg_pass, "postgres", load.pg_port, load.pg_db,
        )
 
        # parent table first, then children (FK order)
        load.update_data_psql(engine, metadata, "tb_organization", tb_organization, "KMZ")
        load.update_data_psql(engine, metadata, "tb_990_return", tb_990, "KMZ")
        load.update_data_psql(engine, metadata, "tb_990ez_return", tb_990ez, "KMZ")
        load.update_data_psql(engine, metadata, "tb_990pf_return", tb_990pf, "KMZ")
        load.update_data_psql(engine, metadata, "tb_officer_salary", tb_officer_salary, "KMZ")
 
        engine.dispose()
 
    # ------------------------------------------------------------------ #
    # WIRING
    # ------------------------------------------------------------------ #
    raw = extract_group()
    records = transform_group(raw)
    load_to_postgres(records)
 
 
irs_990_etl()