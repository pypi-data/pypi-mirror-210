import requests
import hashlib
from uquake.core.logging import logger
from tqdm import tqdm


# def verify_model_identity(model_url, local_model_path):
#     # Download the model from the URL
#     response = requests.get(model_url)
#     model_bytes = response.content
#
#     # Calculate the MD5 checksum of the downloaded model
#     downloaded_md5 = hashlib.md5(model_bytes).hexdigest()
#
#     # Calculate the MD5 checksum of the local model file
#     with open(local_model_path, 'rb') as f:
#         local_model_bytes = f.read()
#     local_md5 = hashlib.md5(local_model_bytes).hexdigest()
#
#     # Compare the two checksums
#     if downloaded_md5 == local_md5:
#         print("The two files are identical.")
#     else:
#         print("The two files are different.")


def verify_model_identity(model_url, local_model_path):
    # Calculate the MD5 checksum of the remote file
    response = requests.get(model_url, stream=True)
    remote_md5 = hashlib.md5()
    with tqdm(total=int(response.headers.get('content-length', 0)),
              desc="Downloading", unit="B", unit_scale=True) as progress_bar:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                remote_md5.update(chunk)
                progress_bar.update(len(chunk))

    # Calculate the MD5 checksum of the local file
    with open(local_model_path, 'rb') as f:
        local_md5 = hashlib.md5(f.read()).hexdigest()

    # Compare the two checksums
    if remote_md5.hexdigest() == local_md5:
        print("The two files are identical.")
    else:
        print("The two files are different.")


import requests
from tqdm import tqdm

import requests
from tqdm import tqdm

def download_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive and saves it to the specified destination.
    """
    URL = "https://drive.google.com/uc?id=" + file_id
    session = requests.Session()
    response = session.get(URL, stream=True)

    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    CHUNK_SIZE = 65536
    total_size = int(response.headers.get("content-length", 0))
    with open(destination, "wb") as f:
        with tqdm(total=total_size, desc="Downloading", unit="B",
                  unit_scale=True) as progress_bar:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))


import gdown

def download_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive and saves it to the specified destination.
    """
    url = "https://drive.google.com/uc?id=" + file_id
    gdown.download(url, destination, quiet=False)

import gdown
import hashlib

def verify_file_identity(file_id, local_path):
    """
    Downloads a file from Google Drive and verifies its MD5 checksum against the local file.
    """
    url = "https://drive.google.com/uc?id=" + file_id
    md5_remote = hashlib.md5(gdown.cached_download(url)).hexdigest()

    with open(local_path, "rb") as f:
        md5_local = hashlib.md5(f.read()).hexdigest()

    if md5_remote == md5_local:
        print("The two files are identical.")
    else:
        print("The two files are different.")


import requests
import hashlib

def get_md5_checksum_from_url(url):
    """
    Calculates the MD5 checksum of a file hosted on Google Drive, given its public URL.
    """
    response = requests.get(url, stream=True)
    md5 = hashlib.md5()

    for chunk in response.iter_content(chunk_size=8192):
        md5.update(chunk)

    return md5.hexdigest()


def compare_md5_checksums(link, local_path):
    """
    Compares the MD5 checksum of a file from a public link and a local file.
    """
    md5_remote = get_md5_checksum_from_url(link)

    with open(local_path, "rb") as f:
        md5_local = hashlib.md5(f.read()).hexdigest()

    if md5_remote == md5_local:
        print("The two files have identical MD5 checksums.")
    else:
        print("The two files have different MD5 checksums.")



