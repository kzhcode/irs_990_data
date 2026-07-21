
# Importing libraries
import io
import os
import urllib.parse
import requests
import bs4
import pandas
import pathlib


# 0. Setting IRS and Working directory links
IRS_BASE = "https://www.irs.gov"
IRS_EO_BMF = "https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf"
IRS_990 = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"
DATA_DIR = "/opt/airflow/data"


# 1. Function to set up directories in a volume 
def dir_setup():
    '''Set up directories needed to extract data from the IRS website'''

    # Testing if data folder exists
    if os.path.exists(DATA_DIR):
        print("The data folder already exists, moving forward")
    else:    
        # If the folder doesnt exists, creating one
        os.mkdir(DATA_DIR)
        print("Created the data folder")    

    # Testing if eo_bmf_files folder exists
    if os.path.exists(os.path.join(DATA_DIR, "eo_bmf_files")):
        print("The eo_bmf_files folder already exists, moving forward")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(os.path.join(DATA_DIR, "eo_bmf_files"))
        print("Created the eo_bmf_files folder")

    # Testing if index_files folder exists
    if os.path.exists(os.path.join(DATA_DIR, "index_files")):
        print("The index_files folder already exists, moving forward")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(os.path.join(DATA_DIR, "index_files"))
        print("Created the index_files folder")

    # Testing if batch_files folder exists
    if os.path.exists(os.path.join(DATA_DIR, "batch_files")):
        print("The batch_files folder already exists, moving forward")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(os.path.join(DATA_DIR, "batch_files"))
        print("Created the batch_files folder")


# 2. Function to extract IRS EO BMF
def irs_eo_bmf_extract():
    '''Access IRS website to extract EO BMF for Kansas and Missouri'''

    try:
       
        # Requesting HTML from IRS
        print(f"Requesting HTTP response from the IRS: {IRS_EO_BMF}")
        response_eo_bmf = requests.get(IRS_EO_BMF)
        response_eo_bmf.raise_for_status()
        print("No HTTP errors raised from IRS upon request, moving forward")

        # Parsing requested HTML into beautiful soup
        print(f"Parsing HTTP response as HTML")
        soup = bs4.BeautifulSoup(response_eo_bmf.text, "html.parser")

        # Extracting updated date for logging purposes
        print("Extracting IRS EO BMF updated date")
        for p in soup.find_all("p"):
            if "Updated data posting date" in p.get_text():
                print(p.text)

        # Extracting record count for logging purposes
        print("Extracting IRS EO BMF record count")
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
        print("Constructing download link for Kansas and Missouri EO BMF")
        ks_file_link = urllib.parse.urljoin(IRS_BASE, tag_ks)
        mo_file_link = urllib.parse.urljoin(IRS_BASE, tag_mo)

        # Requesting KS and MO files from the IRS website
        print(f"Requesting HTTP response from the Kansas EO BMF")
        ks_response = requests.get(ks_file_link)
        ks_response.raise_for_status()
        print("No HTTP errors raised when requesting Kansas EO BMF, moving forward")

        print(f"Requesting HTTP response from the Missouri EO BMF")
        mo_response = requests.get(mo_file_link)
        mo_response.raise_for_status()
        print("No HTTP errors raised when requesting Missouri EO BMF, moving forward")

        # Parsing data with Pandas to read CSV and bypass expensive donwload
        data_ks = pandas.read_csv(io.BytesIO(ks_response.content))
        data_mo = pandas.read_csv(io.BytesIO(mo_response.content))

        # Downloading files into folder
        data_ks.to_csv(os.path.join(DATA_DIR, "eo_bmf_files", "ks_eo_bmf.csv"), na_rep="NA", index=False)
        print("Saving Kansas EO BMF data to the volume")

        data_mo.to_csv(os.path.join(DATA_DIR, "eo_bmf_files", "mo_eo_bmf.csv"), na_rep="NA", index=False)
        print("Saving Missouri EO BMF data to the volume")

    # Rasing HTTP Error if triggered
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occured: {http_err}.")
        raise 

    # Raising any Exception Error if triggered
    except Exception as err:
        print(f"Other error occured: {err}.")
        raise 


# 3. Function to extract IRS 990 Index
def irs_990_index_extract():
    '''Extracting 990 Index files from the IRS website'''

    # Creating a dict to save index file names and links
    index_files = {}

    try: 
        
        # Requesting HTML from IRS
        print(f"Requesting HTTP response from the IRS: {IRS_990}")
        response_990_index = requests.get(IRS_990)
        response_990_index.raise_for_status()
        print("No HTTP errors raised from IRS upon request, moving forward")

        # Parsing requested HTML into beautiful soup
        print(f"Parsing HTTP response as HTML")
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
            print("No HTTP errors raised when requesting the download")

            data = pandas.read_csv(io.BytesIO(response_index.content))
            data.to_csv(os.path.join(DATA_DIR, "index_files", f"{key}.csv"), na_rep="NA", index=False)
            print(f"Successfully downloaded: {key}")

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
    '''Extracting IRS 990 batch files'''

    # Creating a list to save file links
    batch_files = list()

    try: 

        # Requesting HTML from IRS
        print(f"Requesting HTTP response from the IRS: {IRS_990}")
        response_990_batch = requests.get(IRS_990)
        response_990_batch.raise_for_status()
        print("No HTTP errors raised from IRS upon request, moving forward")

        # Parsing requested HTML into beautiful soup
        print(f"Parsing HTTP response as HTML")
        soup = bs4.BeautifulSoup(response_990_batch.text, "html.parser")

        print("Searching for IRS Batch files links")
        for a in soup.find_all("a"):
            if "ZIP" in a.get_text():
                batch_files.append(a.get("href"))

        for file in batch_files: 
            file_name = pathlib.Path(file).name

            print(f"Requesting download for: {file_name}")
            response_batch = requests.get(file, stream=True)
            response_batch.raise_for_status()
            print("No HTTP errors raised from IRS upon request, moving forward")
            
            with open(os.path.join(DATA_DIR, "batch_files", f"{file_name}"), "wb") as zip_file:
                for chunk in response_batch.iter_content(chunk_size=8192):
                    zip_file.write(chunk)
                print(f"Successfully downloaded: {file_name}")

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

