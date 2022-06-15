import os, json, io, requests

# Pull "safe" conifgurations
from dotenv import load_dotenv
load_dotenv()
ALGOD_TOKEN = os.environ.get("ALGOD_TOKEN")
ALGOD_URL = os.environ.get("ALGOD_URL")
CREATOR_MNEMONIC = os.environ.get("TOKEN_MNEMONIC")
PINATA_API_KEY = os.environ.get("PINATA_API_KEY")
PINATA_API_SECERT = os.environ.get("PINATA_API_SECERT")

def img_pinning(image_name, img):
    headers = {        
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_API_SECERT     
    }

    ipfs_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG", quality=100)
            image_binary.seek(0)
            files = {"file": (f"{image_name}.png", image_binary, "image/png")}
            response: requests.Response = requests.post(url=ipfs_url, files=files, headers=headers)
    if response.status_code == 200:
        return response.json()["IpfsHash"]
    else:
        print("BOOOOOOO!!! Not pinned :(")
        print(response.content)

def json_pinning(json_data: json):
    headers = {        
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECERT,
        "Content-Type": "application/json"   
    }

    ipfs_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    payload = {"pinataContent": json_data}
    
    response: requests.Response = requests.post(url=ipfs_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["IpfsHash"]
    else:
        print("BOOOOOOO!!! Not pinned :(")
        print(response.content)