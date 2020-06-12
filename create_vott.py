import os
import json
import base64
import binascii
from Crypto.Cipher import AES


def pad(s):
    return s + (16 - len(s) % 16) * '\t'


def encrypt(message: str, secret: str, iv: str):
    secret = base64.b64decode(secret)
    iv_bytes = bytes.fromhex(iv)
    crypt = AES.new(secret, AES.MODE_CBC, iv_bytes[:16])
    message = pad(message)
    message = message.encode('utf8')
    message = crypt.encrypt(message)
    encrypted_json = {"ciphertext": str(binascii.hexlify(message), 'utf-8'),
                      "iv": iv, }
    encrypted_json = json.dumps(encrypted_json)
    return base64.b64encode(encrypted_json.encode('utf-8'))


def decrypt(message: str, secret: str):
    b64decoded_message = base64.b64decode(message)
    encrypted_obj = json.loads(b64decoded_message)
    iv = encrypted_obj['iv']
    iv_bytes = bytes.fromhex(iv)
    cipher_text = bytes.fromhex(encrypted_obj['ciphertext'])
    secret = base64.b64decode(secret)
    crypt = AES.new(secret, AES.MODE_CBC, iv_bytes[:16])
    path = crypt.decrypt(cipher_text).strip(b'\x07')
    path = str(path, 'utf-8').strip()
    return path, iv


def main():
    name = 'ui test'
    token = 'test_vott Token'
    target_path = "{\"folderPath\":\"D:\\\\ui_dataset\\\\ui\\\\test_vott_changed\"}"
    key = "PiP30DXbt0Ou/d3DpVwWgrLhTgpR8xN3UGiwn7/J42U="

    encrypted_original = 'eyJjaXBoZXJ0ZXh0IjoiOWEwMmU4YWI4NDk5NWU0NDNiZDQwZjY5N2E5NjU0ODk2NzE3NGMzNzM1YmQ4ZDUyOTFjMGMwN2FkMTM3ZTZkMDRlMWNmZWUzODYxZDIyNTc2Zjg3YWY0MGNhZjY4ODZjNzJlZTA1NjI4YzU5MzQxZjdlNzliMTVmY2JmYjlmMmFmODRhM2RhZDhmOWRhMGZmMWZkZDY0ZDUzOTAzOWEwOTIwMGYyZmVlMzA2MDY4OWQzNTI2MmM2ZmZlZjhiOTY1IiwiaXYiOiI0NGYyMjU4YWFkYmU0ODNhOWYxYzg2OTdhOTAwMGRiYWEzZGMzNDI3OGY0ZDc4MjUifQ=='
    src_path_string, iv_str = decrypt(encrypted_original, key)

    original_path = json.loads(src_path_string)['folderPath']
    print('changing path from {} to {}'.format(original_path, target_path))
    # original_path = '/home/kimberly/projects/ui_data_v2/ui_dataset/ui/test_vott'
    encrypted_new = encrypt(target_path, key, iv_str).decode('utf-8')
    print('new encrypted information')
    print(encrypted_new)
    assets = {}
    for file_name in os.listdir(original_path):
        with open(os.path.join(original_path, file_name)) as f:
            annotation = json.load(f)
            try:
                id = annotation['asset']['id']
                vott_name = id + '-asset.json'
                if not vott_name == file_name:
                    raise Exception('vott name and file name does not match!')
                assets[id] = annotation['asset']
            except:
                print(file_name)

    format_path = './test_vott.json'
    with open(format_path) as f:
        vott = json.load(f)
        for connection in ['sourceConnection', 'targetConnection']:
            vott[connection]['name'] = name
            vott[connection]['description'] = name
            vott[connection]['providerOptions']['encrypted'] = encrypted_new
        vott['exportFormat']['providerOptions']['encrypted'] = encrypted_new
        vott['lastVisitedAssetId'] = list(assets.keys())[0]
        vott['assets'] = assets
    with open(os.path.join(target_path, '/home/kimberly/projects/ui_data_v2/ui_dataset/ui/test_vott_changed.vott'),
              'w') as f:
        json.dump(vott, f, indent=4)


if __name__ == '__main__':
    main()
