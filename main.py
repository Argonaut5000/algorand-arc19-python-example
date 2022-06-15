import multihash, hashlib

from algorand_utils import *
from helper_methods import *

from hmac import digest
from PIL import Image
from algosdk import encoding, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn

from cid import make_cid

# https://developer.algorand.org/docs/get-details/asa/ Used for examples and code
# https://github.com/algorand/docs/blob/master/examples/assets/v2/python/asset_example.py
# https://github.com/algokittens/algoNFTs

"""
Author @Argonaut5000

With Help from @gabrielkuettel, @algokittens THANK YOU!
"""

def test_arc19_mint_asset(algod_token, algod_address, creator_mnemonic, arc19_hash, unit_name, asset_name, metadata):
    creator_account = {}    
    creator_account["pk"] = mnemonic.to_public_key(creator_mnemonic)
    creator_account['sk'] = mnemonic.to_private_key(creator_mnemonic)
    
    headers = {
       "X-API-Key": algod_token,
    }    
    algod_client = algod.AlgodClient(algod_token, algod_address, headers);    

    # Get network params for transactions before every transaction.
    params = algod_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True
    
    txn = AssetConfigTxn(
        sender=creator_account["pk"],
        sp=params,
        total= 1,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name, 
        manager=creator_account["pk"],
        reserve=encoding.encode_address(arc19_hash),
        freeze=None,
        clawback=creator_account["pk"],
        strict_empty_address_check=False,
        url="template-ipfs://{ipfscid:0:dag-pb:reserve:sha2-256}",
        metadata_hash= "",
        note=metadata.encode(),
        decimals=0)
    
    # Sign with secret key of creator
    stxn = txn.sign(creator_account['sk'])
    
    # Send the transaction to the network and retrieve the txid.
    txid = algod_client.send_transaction(stxn)
    print(txid)
    
    # Wait for the transaction to be confirmed
    wait_for_confirmation(algod_client,txid)
    
    ptx = algod_client.pending_transaction_info(txid)
    asset_id = ptx["asset-index"]
    print_asset_holding(algod_client, creator_account['pk'], asset_id)

    return asset_id

def test_arc19_update_reserve(algod_token, algod_address, creator_mnemonic, asset_id, arc19_hash):
    creator_account = {}    
    creator_account["pk"] = mnemonic.to_public_key(creator_mnemonic)
    creator_account['sk'] = mnemonic.to_private_key(creator_mnemonic)
    
    headers = {
       "X-API-Key": algod_token,
    }    
    algod_client = algod.AlgodClient(algod_token, algod_address, headers); 
    params = algod_client.suggested_params()

    params.fee = 1000
    params.flat_fee = True
    txn = AssetConfigTxn(
        sender=creator_account["pk"],
        sp=params,
        index=asset_id, 
        manager=creator_account["pk"],
        reserve=encoding.encode_address(arc19_hash),
        freeze=None,
        clawback=None,
        strict_empty_address_check=False)

    stxn = txn.sign(creator_account["sk"])

    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   
    except Exception as err:
        print(err)
        return False
    
    return True

def mint_arc19_nft():
    img = Image.open("./egg.png").crop((107,0,533,426)).resize((500,500))
    hash = img_pinning("egg", img)
    
    ipfs_url = f"ipfs://{hash}"

    # Define 
    metadata = {
        "name": "Python Example ARC19",
        "description": "An Example NFT minted with ARC19, in python!",
        "image": ipfs_url,
        "image_mimetype": "image/png",
        "image_integrity": "sha256-" + str(hashlib.sha256(img.tobytes()).digest()),
        "external_url":
        "https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0019.md",
        "properties": {
            "Tester": "@argonaut5000",
            "Status": "Fresh",
            "Background": "White Void",
        },
    }

    hash = json_pinning(metadata)
    digest = multihash.decode(make_cid(hash).multihash).digest
    hashed_string = digest
    print(hashed_string)

    asset_name = f"Argo's Arc 19 Test NFT"
    unit_name = "ARGOTEST"
    asset_id = test_arc19_mint_asset(ALGOD_TOKEN, ALGOD_URL, CREATOR_MNEMONIC, hashed_string, unit_name, asset_name, "{}")
    print(f"Minted asset: {asset_id}")
    return asset_id

def update_arc19_nft(asset_id):
    img = Image.open("./cooked.png").resize((500,500))
    hash = img_pinning("cooked", img)
    
    ipfs_url = f"ipfs://{hash}"

    # Define 
    metadata = {
        "name": "Python Example ARC19",
        "description": "An Example NFT minted with ARC19, in python!",
        "image": ipfs_url,
        "image_mimetype": "image/png",
        "image_integrity": "sha256-" + str(hashlib.sha256(img.tobytes()).digest()),
        "external_url":
        "https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0019.md",
        "properties": {
            "Tester": "@argonaut5000",
            "Status": "Cooked",
            "Background": "Pan",
            "New Additional Attribute": "Eggs are yummy"
        },
    }

    hash = json_pinning(metadata)
    digest = multihash.decode(make_cid(hash).multihash).digest
    hashed_string = digest
    print(hashed_string)

    test_arc19_update_reserve(ALGOD_TOKEN, ALGOD_URL, CREATOR_MNEMONIC, asset_id, hashed_string)
    print(f"Updated asset: {asset_id}")


# Run Stuff Here
mint_arc19_nft()

#update_arc19_nft("778667165")