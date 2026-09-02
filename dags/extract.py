
# Importing libraries
import io
import os
import urllib.parse
import requests
import bs4
import pandas
import pathlib


# 0.0 Setting working directory paths
ROOT_DATA_DIR = "/opt/airflow/data"
IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_EO_BMF_FILES")
IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_INDEX_FILES")
IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_990_FILES")

# 0.1 Setting IRS website paths
IRS_BASE_WEB = "https://www.irs.gov"
IRS_EO_BMF_WEB = "https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf"
IRS_990_WEB = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"


# 1. Function to set up directories in a volume 
def dir_setup():
    '''
    Action: Set up directories needed to extract data from the IRS website.
    '''

    # Testing if root data folder exists
    if os.path.exists(ROOT_DATA_DIR):
        print(f"Directory {ROOT_DATA_DIR.upper()} already exists")
    else:    
        # If the folder doesnt exists, creating one
        os.mkdir(ROOT_DATA_DIR)
        print(f"Created {ROOT_DATA_DIR.upper()} directory")    


    # Testing if eo_bmf_files folder exists
    if os.path.exists(IRS_EO_BMF_DIR):
        print(f"Directory {IRS_EO_BMF_DIR.upper()} already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(IRS_EO_BMF_DIR)
        print(f"Created {IRS_EO_BMF_DIR.upper()} directory")


    # Testing if index_files folder exists
    if os.path.exists(IRS_INDEX_DIR):
        print(f"Directory {IRS_INDEX_DIR.upper()} already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(IRS_INDEX_DIR)
        print(f"Created {IRS_INDEX_DIR.upper()} directory")


    # Testing if batch_files folder exists
    if os.path.exists(IRS_990_DIR):
        print(f"Directory {IRS_990_DIR} already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(IRS_990_DIR)
        print(f"Created {IRS_990_DIR} directory")


# 2. Function to extract IRS EO BMF
def irs_eo_bmf_extract():
    '''
    Action: Access IRS website to extract EO BMF for Kansas and Missouri.
    '''

    try:
       
        # Requesting HTML from IRS
        print(f"Requesting HTTP response from IRS: {IRS_EO_BMF_WEB.upper()}")
        response_eo_bmf = requests.get(IRS_EO_BMF_WEB)
        response_eo_bmf.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing requested HTML into beautiful soup
        soup = bs4.BeautifulSoup(response_eo_bmf.text, "html.parser")
        print(f"Parsed IRS's HTTP response as HTML")

        # Extracting updated date for logging purposes
        print(f"Extracting update date for IRS files in {IRS_EO_BMF_WEB.upper()}")
        for p in soup.find_all("p"):
            if "Updated data posting date" in p.get_text():
                print(p.text)

        # Extracting record count for logging purposes
        print(f"Extracting record count from IRS files in {IRS_EO_BMF_WEB.upper()}")
        for p in soup.find_all("p"):
            if "Record Count" in p.get_text():
                print(p.text)

        # Extracting links for KS and MO filess
        print("Searching for Kansas EO BMF")
        tag_ks = soup.find("a", attrs={"data-entity-type": "media", "data-entity-uuid": "2759d103-b087-4df4-8b23-73c2f480446f"})
        tag_ks = tag_ks["href"]

        print("Searching for Missouri EO BMF")
        tag_mo = soup.find("a", attrs={"data-entity-type": "media", "data-entity-uuid": "77d698f7-03dc-42ab-aa2c-85bf09bc93a1"})
        tag_mo = tag_mo["href"]

        # Constructing full links to KS and MO EO BMF
        ks_file_link = urllib.parse.urljoin(IRS_BASE_WEB, tag_ks)
        mo_file_link = urllib.parse.urljoin(IRS_BASE_WEB, tag_mo)
        print("Constructing download links to Kansas and Missouri EO BMF files")

        # Requesting KS and MO files from the IRS website
        print(f"Requesting HTTP response from the Kansas EO BMF")
        ks_response = requests.get(ks_file_link)
        ks_response.raise_for_status()
        print("No HTTP errors raised when requesting Kansas EO BMF")

        print(f"Requesting HTTP response from the Missouri EO BMF")
        mo_response = requests.get(mo_file_link)
        mo_response.raise_for_status()
        print("No HTTP errors raised when requesting Missouri EO BMF")

        # Parsing data with Pandas to read CSV and bypass expensive donwload
        data_ks = pandas.read_csv(io.BytesIO(ks_response.content))
        data_mo = pandas.read_csv(io.BytesIO(mo_response.content))

        # Downloading files into folder
        data_ks.to_csv(os.path.join(IRS_EO_BMF_DIR, "ks_eo_bmf.csv"), na_rep="NA", index=False)
        print(f"Saved Kansas EO BMF file to {IRS_EO_BMF_DIR.upper()}")

        data_mo.to_csv(os.path.join(IRS_EO_BMF_DIR, "mo_eo_bmf.csv"), na_rep="NA", index=False)
        print(f"Saved Missouri EO BMF file tp {IRS_EO_BMF_DIR.upper()}")

    # Rasing HTTP Error if triggered
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occured: {http_err}")
        raise 

    # Raising any Exception Error if triggered
    except Exception as err:
        print(f"Other error occured: {err}")
        raise 


# 3. Function to extract IRS 990 Index
def irs_990_index_extract():
    '''
    Action: Extracting IRS 990 Index files from the website.
    '''

    # Creating a dict to save index file names and links
    index_files = {}

    try: 
        
        # Requesting HTML from IRS
        print(f"Requesting HTTP response from IRS: {IRS_990_WEB.upper()}")
        response_990_index = requests.get(IRS_990_WEB)
        response_990_index.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing requested HTML into beautiful soup
        print(f"Parsing IRS's HTTP response as HTML")
        soup = bs4.BeautifulSoup(response_990_index.text, "html.parser")

        # Parsing HTML to find index links
        print("Searching for IRS Index files links")
        for p in soup.find_all("p"):
            if "Index file for" in p.get_text():
                text = p.text.strip(u'\u200b')
                index_files[text] = p.find("a")["href"]

        for key, value in index_files.items():
            print(f"Requesting download for {key}: {value}")
            response_index = requests.get(value)
            response_index.raise_for_status()
            print("No HTTP errors raised when requesting file download")

            data = pandas.read_csv(io.BytesIO(response_index.content))
            data.to_csv(os.path.join(IRS_INDEX_DIR, f"{key}.csv"), na_rep="NA", index=False)
            print(f"Successfully downloaded: {str(key).upper()}.CSV")

    # Rasing HTTP Error if triggered
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occured: {http_err}.")
        raise 

    # Raising any Exception Error if triggered
    except Exception as err:
        print(f"Other error occured: {err}.")
        raise 


# 4. Function to extract IRS batch files
def irs_990_batch_extract():
    '''
    Action: Extracting IRS 990 batch files.
    '''

    # Creating a list to save file links
    batch_files = list()

    try: 

        # Requesting HTML from IRS
        print(f"Requesting HTTP response from the IRS: {IRS_990_WEB.upper()}")
        response_990_batch = requests.get(IRS_990_WEB)
        response_990_batch.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing requested HTML into beautiful soup
        print(f"Parsing HTTP response as HTML")
        soup = bs4.BeautifulSoup(response_990_batch.text, "html.parser")

        print("Searching for IRS 990 Batch file links")
        for a in soup.find_all("a"):
            if "ZIP" in a.get_text():
                batch_files.append(a.get("href"))

        for file in batch_files: 
            file_name = pathlib.Path(file).name

            print(f"Requesting download for: {str(file_name).upper()}")
            response_batch = requests.get(file, stream=True)
            response_batch.raise_for_status()
            print("No HTTP errors raised from IRS upon request")
            
            with open(os.path.join(IRS_990_DIR, f"{file_name}"), "wb") as zip_file:
                for chunk in response_batch.iter_content(chunk_size=8192):
                    zip_file.write(chunk)
                print(f"Successfully downloaded: {str(file_name).upper()}")

    # Rasing HTTP Error if triggered
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occured: {http_err}.")
        raise 

    # Raising any Exception Error if triggered
    except Exception as err:
        print(f"Other error occured: {err}.")
        raise


if __name__ == "__main__":
    dir_setup()
    irs_eo_bmf_extract()
    irs_990_index_extract()
    irs_990_batch_extract()

