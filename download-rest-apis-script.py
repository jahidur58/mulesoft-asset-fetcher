import requests
import os
import re

ANYPOINT_BASE_URL = "https://anypoint.mulesoft.com"

def get_access_token(client_id, client_secret):
    url = f"{ANYPOINT_BASE_URL}/accounts/api/v2/oauth2/token"
    response = requests.post(
        url = url,
        headers = {"Content-Type": "application/json"},
        json = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]

def list_rest_api(access_token, organization_id):
    offset = 0
    limit = 20
    all_assets = []

    while True:
        url = f"{ANYPOINT_BASE_URL}/exchange/api/v2/assets?offset={offset}&limit={limit}&types=rest-api&organizationId={organization_id}"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            print(f"No more data at offset {offset}. Exiting loop.")
            break

        all_assets.extend(data)  
        offset += limit 

    return all_assets


def get_organization_id(access_token):
    url = f"{ANYPOINT_BASE_URL}/accounts/api/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["user"]["organization"]["id"]

def check_asset_files(access_token, group_id, asset_id, version):
    url = f"{ANYPOINT_BASE_URL}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/files"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(f"DEBUG: Response status code: {response.status_code}")
    print(f"DEBUG: Response content: {response.text}")
    #response.raise_for_status()
    # print(f"check asset: {response.json()}")
    return response.json()

def download_file(access_token, download_url, output_path):
    response = requests.get(
        download_url,
        headers={"Authorization": f"Bearer {access_token}"},
        stream=True,
    )
    #response.raise_for_status()
    with open(output_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def sanitize(value):
    return re.sub(r'[^\w\-_]', '_', value)

def get_output_path(asset_id, version, classifier):
    output_dir = "output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    asset_id = sanitize(asset_id)
    version = sanitize(version)
    classifier = sanitize(classifier)

    return f"{output_dir}{asset_id}_{version}.{classifier}.zip"

def main():
    client_id = "####"
    client_secret = "####"
    access_token = get_access_token(client_id, client_secret)
    #organization_id = get_organization_id(access_token)
    organization_id = "####"
    #print(f"access_token: {access_token}")
    #print(f"Organization ID: {organization_id}")
    try:
        rest_apis = list_rest_api(access_token, organization_id);
        if rest_apis:
                print("REST APIs found in the organization:")
                for api in rest_apis:
                    group_id = api.get("groupId")
                    asset_id = api.get("assetId")
                    version = api.get("version")
                    files = api.get("files")

                    if not files:
                        print(f"No files found for {asset_id} (version: {version}).")
                        continue
                    for file_info in files:
                        classifier = file_info.get("classifier")
                        #print(classifier)
                        if classifier in ["rest-api", "raml", "oas"]:
                            download_url = file_info.get("externalLink")
                            #output_path = f"output/{asset_id}_{version}.{classifier}.zip"
                            output_path = get_output_path(asset_id, version, classifier)
                            print(f"Downloading {classifier} file for {asset_id} to {output_path}...")
                            download_file(access_token, download_url, output_path)
                            print(f"Downloaded {classifier} file for {asset_id}.")
                        else:
                            print(f"Unsupported file type: {classifier} for {asset_id}.")    
        else:
            print("No REST APIs found for the specified organization.")
    
    except requests.exceptions.RequestException as e:
            print(f"Failed to check or download files for {asset_id}: {e}")        

if __name__ == "__main__":
    main()
