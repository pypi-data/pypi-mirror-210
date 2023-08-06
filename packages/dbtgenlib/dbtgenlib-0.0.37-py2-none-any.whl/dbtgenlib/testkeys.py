import json
import click

from dbtgenlib import genyml

with open('manifest.json') as manifest_file:
        manifest_data = json.load(manifest_file)

def find_keys():
    keys_dict = {}
    for node,data in manifest_data['nodes'].items():
        if 'unrendered_config' in data.keys():
            for keys, value in data['unrendered_config'].items():
                node = node.split('.')[-1]
                if 'unique_key' in keys:
                    keys_dict[node] = value.strip()
    return keys_dict

def check_skeys():
    model_keys = genyml.dbtdocgen()
    skeys = find_keys()
    non_unique_keys = {}

    flag = True

    for model_key in model_keys:
        for model_name, skey in skeys.items():
            if skey.strip() == model_key.strip():
                pass
            else:
                non_unique_keys[model_name] = skey.strip()
                flag = False

    if flag == False:
        # print("The test has failed!")
        click.echo("The test has failed!")
        for model_name, skey in non_unique_keys.items():
            # print(f"For the model: {model_name}, the key: {skey} is not unique!")
            click.echo(f"For the model: {model_name}, the key: {skey} is not unique!")
    else:
        click.echo("The test has been successful!")
        # print("The test has been successful!")

if __name__ == '__main__':
    check_skeys()