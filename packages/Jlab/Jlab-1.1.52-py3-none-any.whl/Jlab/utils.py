from datetime import timedelta
from retry import retry
from github import Github
from .aes_crypt import AESCrypt
import subprocess
import requests
import pickle
import os
import time
import json
import re


def decrypt_github_file(repo, password, select_file):
    # Get file path
    file_path = get_file_path(repo, select_file)

    # Check if file exists
    if not file_path:
        exit()

    # Create the enc folder if it does not exist
    enc_folder = os.path.join(".", "enc")
    if not os.path.exists(enc_folder):
        os.makedirs(enc_folder)

    # Download and decrypt data from Github
    download_file(
        repo=repo, github_file_path=os.path.join(file_path), download_path=enc_folder,
    )

    # Decrypt data from downloaded file
    with open(os.path.join(enc_folder, select_file), "rb") as f:
        encrypted_data = (f.readline().strip(), f.readline().strip())

    # Decrypt data
    aes = AESCrypt(password)
    decrypted_data = aes.decrypt(encrypted_data)
    return decrypted_data.decode(encoding="utf-8")


def get_file_path(repo, select_file):
    """
    Retrieve the path of the input file from a GitHub repository.
    """
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file_name = re.sub(r"^.+/", "", file_content.path)
            if file_name == select_file:
                return file_content.path

    print(f"File {select_file} not found in the repository.")
    return None


def get_file_list(repo):
    def get_file_names(contents):
        """
        A generator that recursively retrieves file names from a GitHub repository.
        """
        for file_content in contents:
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file_name = re.sub(r"^.+\/", "", file_content.path)
                yield file_name

    all_files = list(get_file_names(repo.get_contents("")))
    return all_files


def get_github_repo(token, repo_name):
    """
    連接 Github API，獲取指定名稱和 Token 的 Github 倉庫對象
    """
    g = Github(token)
    user = g.get_user()
    repo = user.get_repo(repo_name)
    return repo


def get_dataset_df_data(dataset):
    url = f"https://github.com/twfxjjbw/stockinfo/raw/main/{dataset}.bin"
    response = requests.get(url)
    if response.status_code == 200:
        df = pickle.loads(response.content)
        return df
    else:
        raise Exception(f"Error downloading {dataset}: {response.status_code}")


def decrypt_data_from_github(
    filename, my_password, github_token, repo_name, branch=None
):
    repo = get_github_repo(token=github_token, repo_name=repo_name)

    # Create AESCrypt instance
    aes = AESCrypt(my_password)

    # Download encrypted file from Github
    download_file(repo=repo, github_file_path=filename, branch=branch)

    # Read encrypted data from file
    with open(filename, "rb") as f:
        encrypted_data = (f.readline().strip(), f.readline().strip())

    # Decrypt data
    decrypted_data = aes.decrypt(encrypted_data)

    # Deserialize decrypted data into Python object
    data_decrypt = json.loads(decrypted_data.decode("utf-8"))

    return data_decrypt


@retry(exceptions=Exception, tries=3, delay=2, backoff=2)
def download_file(repo, github_file_path, download_path=None, branch=None):
    filename = os.path.basename(github_file_path)
    if not download_path:
        download_path = os.getcwd()

    if branch:
        file_content = repo.get_contents(github_file_path, ref=branch)
    else:
        file_content = repo.get_contents(github_file_path)

    file_content_data = file_content.decoded_content
    mode = "wb" if isinstance(file_content_data, bytes) else "w"
    with open(os.path.join(download_path, filename), mode) as f:
        f.write(file_content_data)
    print(f"{filename} downloaded to {download_path}")


@retry(exceptions=Exception, tries=3, delay=2, backoff=2)
def update_file(repo, filename, branch=None):
    cwd = os.path.abspath(os.getcwd())
    try:
        if branch:
            contents = repo.get_contents(filename, ref=branch)
        else:
            contents = repo.get_contents(filename)
        sha = contents.sha
        print(f"{filename} EXISTS")
    except Exception as e:
        sha = None
        print(f"{filename} DOES NOT EXIST")

    with open(filename, "rb") as f:
        file_content = f.read()

    content = None
    if isinstance(file_content, str):
        with open(os.path.join(cwd, filename), "r") as f:
            content = f.read()
    elif isinstance(file_content, bytes):
        with open(os.path.join(cwd, filename), "rb") as f:
            content = f.read()

    if sha:
        if branch:
            repo.update_file(filename, "committing files", content, sha, branch=branch)
        else:
            repo.update_file(filename, "committing files", content, sha)
        print(f"{filename} UPDATED")
    else:
        if branch:
            repo.create_file(filename, "committing files", content, branch=branch)
        else:
            repo.create_file(filename, "committing files", content)
        print(f"{filename} CREATED")


@retry(exceptions=Exception, tries=3, delay=2, backoff=2)
def delete_file(repo, filename, branch=None):
    """
    刪除指定的 Github 倉庫中的檔案
    """
    all_files = []
    if branch:
        contents = repo.get_contents("", ref=branch)
    else:
        contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            if branch:
                contents.extend(repo.get_contents(file_content.path, ref=branch))
            else:
                contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(file.path)

    # 要刪除的檔案路徑
    git_file = filename

    if git_file in all_files:
        # 如果已存在，刪除檔案
        if branch:
            file = repo.get_contents(git_file, ref=branch)
            repo.delete_file(file.path, "Delete files", file.sha, branch=branch)
        else:
            file = repo.get_contents(git_file)
            repo.delete_file(file.path, "Delete files", file.sha)
        print(f"{git_file} deleted")
    else:
        print(f"{git_file} does not exist.")


def get_execution_time(func):
    """
    裝飾器：計算函數執行時間
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = timedelta(seconds=end_time - start_time)
        ms = int(elapsed_time.total_seconds() * 1000)
        print("Function {} took {} ms to execute.".format(func.__name__, ms))
        return result

    return wrapper

def get_fonts():
    # Run fc-list command and capture output
    output = subprocess.check_output(['fc-list'])

    # Decode output and split into lines
    output = output.decode('utf-8')
    lines = output.split('\n')

    # Extract font names from lines
    fonts = []
    for line in lines:
        if ':' in line:
            font = line.split(':')[0]
            fonts.append(font)

    # Extract font names from lines
    font_names = []
    for font in fonts:
        f = font.split('/')[-1]
        font_names.append(f)

    return font_names
