
# Importing libraries
import io
import os
import urllib.parse
import requests
import bs4
import pandas
import pathlib


# 0.1 Setting IRS links
IRS_BASE = "https://www.irs.gov"
IRS_EO_BMF = "https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf"
IRS_990 = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"

# 0.2 Setting working directories
ROOT_DATA_DIR = "/opt/airflow/data"

IRS_EO_BMF_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_EO_BMF_FILES")
IRS_INDEX_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_INDEX_FILES")
IRS_990_DIR = os.path.join(ROOT_DATA_DIR, "ORIGINAL_990_FILES")

# 0.3 Setting timeouts in seconds for every HTTP request
REQUEST_TIMEOUT = (10, 300)


# 1. Function to set up directories in a volume 
def dir_setup():
    '''
    Action: This function sets up directories needed for data extraction from IRS website.
    '''

    # Testing if ORIGINAL_EO_BMF_FILES directory exists
    if os.path.exists(IRS_EO_BMF_DIR):
        print(f"{IRS_EO_BMF_DIR} directory already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(IRS_EO_BMF_DIR)
        print(f"Created {IRS_EO_BMF_DIR} directory")

    # Testing if ORIGINAL_INDEX_FILES directory exists
    if os.path.exists(IRS_INDEX_DIR):
        print(f"{IRS_INDEX_DIR} directory already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(IRS_INDEX_DIR)
        print(f"Created {IRS_INDEX_DIR} directory")

    # Testing if ORIGINAL_990_FILES directiry exists
    if os.path.exists(IRS_990_DIR):
        print(f"{IRS_990_DIR} directory already exists")
    else:
        # If the folder doesnt exists, creating one
        os.mkdir(IRS_990_DIR)
        print(f"Created {IRS_990_DIR} directory")


# 2. Function to extract IRS EO BMF
def irs_eo_bmf_extract():
    '''
    Action: This function accesses IRS website to extract EO BMF for Kansas and Missori states only. Other states functionality 
    could be added in the future. 
    '''

    try:
       
        # Requesting HTML from IRS
        response_eo_bmf = requests.get(IRS_EO_BMF, timeout=REQUEST_TIMEOUT)
        print(f"Requested HTTP response from IRS: {IRS_EO_BMF.upper()}")
        response_eo_bmf.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing requested HTML into beautiful soup
        soup = bs4.BeautifulSoup(response_eo_bmf.text, "html.parser")
        print(f"Parsed IRS's HTTP response as HTML")

        # Extracting updated date for logging purposes
        print("Determining IRS EO BMF files updated date")
        for p in soup.find_all("p"):
            if "Updated data posting date" in p.get_text():
                print(p.text)

        # Extracting record count for logging purposes
        print("Determining IRS EO BMF files record count")
        for p in soup.find_all("p"):
            if "Record Count" in p.get_text():
                print(p.text)

        # Extracting links for KS and MO filess
        tag_ks = soup.find("a", attrs={"data-entity-type": "media", "data-entity-uuid": "2759d103-b087-4df4-8b23-73c2f480446f"})
        print("Found EO BMF for Kansas on IRS website")
        tag_ks = tag_ks["href"]

        tag_mo = soup.find("a", attrs={"data-entity-type": "media", "data-entity-uuid": "77d698f7-03dc-42ab-aa2c-85bf09bc93a1"})
        print("Found EO BMF for Missouri on IRS website")
        tag_mo = tag_mo["href"]

        # Constructing full links to KS and MO EO BMF
        ks_file_link = urllib.parse.urljoin(IRS_BASE, tag_ks)
        mo_file_link = urllib.parse.urljoin(IRS_BASE, tag_mo)
        print("Constructed download EO BMF links for Kansas and Missouri")

        # Requesting KS and MO files from the IRS website
        ks_response = requests.get(ks_file_link, timeout=REQUEST_TIMEOUT)
        print(f"Requested HTTP response from IRS to download Kansas EO BMF")
        ks_response.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        mo_response = requests.get(mo_file_link, timeout=REQUEST_TIMEOUT)
        print(f"Requested HTTP response from IRS to download Missouri EO BMF")
        mo_response.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing data with Pandas to read CSV and bypass expensive donwload
        data_ks = pandas.read_csv(io.BytesIO(ks_response.content))
        print("Parsed downloaded Kansas EO BMF data as CSV")
        data_mo = pandas.read_csv(io.BytesIO(mo_response.content))
        print("Parsed downloaded Missouri EO BMF data as CSV")

        # Downloading files into ORIGINAL_EO_BMF_FILES directory
        data_ks.to_csv(os.path.join(IRS_EO_BMF_DIR, "ks_eo_bmf.csv"), na_rep="NA", index=False)
        print(f"Saved Kansas EO BMF data to {IRS_EO_BMF_DIR}")

        data_mo.to_csv(os.path.join(IRS_EO_BMF_DIR, "mo_eo_bmf.csv"), na_rep="NA", index=False)
        print(f"Saved Missouri EO BMF data to {IRS_EO_BMF_DIR}")

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
    Action: This function accesses IRS website to extract 990 index files. These files are needed to reference 990 return locations.
    '''

    # Creating a dict to save index file names and links
    index_files = {}

    try: 
        
        # Requesting HTML from IRS
        response_990_index = requests.get(IRS_990, timeout=REQUEST_TIMEOUT)
        print(f"Requested HTTP response from IRS: {IRS_990.upper()}")
        response_990_index.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing requested HTML into beautiful soup
        soup = bs4.BeautifulSoup(response_990_index.text, "html.parser")
        print(f"Parsed IRS's HTTP response as HTML")


        # Parsing HTML to find index links
        print("Locating IRS index files links")
        for p in soup.find_all("p"):
            if "Index file for" in p.get_text():
                text = p.text.strip(u'\u200b')
                index_files[text] = p.find("a")["href"]

        # requesting index files from IRS website
        for key, value in index_files.items():
            response_index = requests.get(value, timeout=REQUEST_TIMEOUT)
            print(f"Requested download for {str(key).upper()}: {str(value).upper()}")
            response_index.raise_for_status()
            print("No HTTP errors raised from IRS upon request")

            # saving index files to ORIGINAL_INDEX_FILES directory
            data = pandas.read_csv(io.BytesIO(response_index.content))
            print(f"Parsed downloaded {str(key).upper()} as CSV")
            data.to_csv(os.path.join(IRS_INDEX_DIR, f"{key}.csv"), na_rep="NA", index=False)
            print(f"Downloaded {str(key).upper()} file to {IRS_INDEX_DIR}")

    # Rasing HTTP Error if triggered
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occured: {http_err}.")
        raise 

    # Raising any Exception Error if triggered
    except Exception as err:
        print(f"Other error occured: {err}.")
        raise 


# 4. This function reads a remote file size without downloading it
def remote_file_size(url: str):
    '''
    Action: This function sends a HEAD request and returns the Content-Length header as an int, or None if the
    server does not report it or the request fails.
    '''

    try:
        response_head = requests.head(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        response_head.raise_for_status()
        size = response_head.headers.get("Content-Length")
        return int(size) if size is not None else None

    except requests.exceptions.RequestException as err:
        print(f"Could not determine remote size for {url}: {err}")
        return None


# 5. Function to extract IRS batch files
def irs_990_batch_extract():
    '''
    Action: This function accesses IRS website to extract zipped 990 files.
    '''

    # Creating a list to save file links
    batch_files = list()

    try: 

        # Requesting HTML from IRS
        response_990_batch = requests.get(IRS_990, timeout=REQUEST_TIMEOUT)
        print(f"Requested HTTP response from IRS: {IRS_990.upper()}")
        response_990_batch.raise_for_status()
        print("No HTTP errors raised from IRS upon request")

        # Parsing requested HTML into beautiful soup
        soup = bs4.BeautifulSoup(response_990_batch.text, "html.parser")
        print(f"Parsed IRS's HTTP response as HTML")

        print("Locating IRS 990 zipped files")
        for a in soup.find_all("a"):
            if "ZIP" in a.get_text():
                batch_files.append(a.get("href"))

        # processing found zipped 990 files
        for file in batch_files: 
            file_name = pathlib.Path(file).name
            final_path = os.path.join(IRS_990_DIR, file_name)
            temp_path = f"{final_path}.part"

            # asking the server how big the file is
            remote_size = remote_file_size(file)

            # skipping downloaded files
            if os.path.exists(final_path):
                local_size = os.path.getsize(final_path)

                if remote_size is None:
                    print(f"{file_name.upper()} already exists and remote size is unknown, skipping download")
                    continue

                if local_size == remote_size:
                    print(f"{file_name.upper()} already exists with matching size ({local_size} bytes), skipping download")
                    continue

                print(f"{file_name.upper()} size mismatch ( local {local_size} vs remote {remote_size}), re-downloading")

            # removing leftovers of a previously interrupted download
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Removed stale partial download {temp_path}")

            try:
                with requests.get(file, stream=True, timeout=REQUEST_TIMEOUT) as response_batch:
                    print(f"Requested download for {str(file_name).upper()}")
                    response_batch.raise_for_status()
                    print("No HTTP errors raised from IRS upon request")

                    # streaming into temporary file
                    with open(temp_path, "wb") as zip_file:
                        for chunk in response_batch.iter_content(chunk_size=1024*1024):
                            zip_file.write(chunk)

                # verifying the download is complete before publishing it under the final name
                downloaded_size = os.path.getsize(temp_path)
                if remote_size is not None and downloaded_size != remote_size:
                    raise IOError(f"Incomplete download for {file_name}: got {downloaded_size} of {remote_size} bytes")

                # atomic rename: the final name only ever points to a complete file
                os.replace(temp_path, final_path)
                print(f"Downloaded {str(file_name).upper()} to {IRS_990_DIR}")

            except Exception:
                # never leave a partial file behind
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
                

    # Rasing HTTP Error if triggered
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occured: {http_err}")
        raise 

    # Raising any Exception Error if triggered
    except Exception as err:
        print(f"Other error occured: {err}")
        raise


if __name__ == "__main__":
    dir_setup()
    irs_eo_bmf_extract()
    irs_990_index_extract()
    irs_990_batch_extract()

