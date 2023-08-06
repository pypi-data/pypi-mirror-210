import click
import json
import os
import yaml as yml

@click.command()
@click.option('--select', type=str)

def dbtdocgen(select):
    
    with open(r"target\manifest.json") as file:
        manifest_data = json.load(file)
        
    with open(r"dbt_project.yml") as file:
        dbtproject = yml.safe_load(file)
 
    names_set = set()

    if '\\' in manifest_data['nodes'][list(manifest_data['nodes'].keys())[0]]['original_file_path']:
        select = select.replace('/','\\')
    else:
        select = select.replace('\\','/')

    for node, data in manifest_data['nodes'].items():
        if 'unique_key' in data['unrendered_config']:
            names = str(data['fqn'][-2])
            names_set.add(names)

    distinct_names = list(names_set)

    for name in distinct_names:
        yaml = '\nversion: 2\n\nmodels:\n\n'

        for node, data in sorted(list(manifest_data['nodes'].items()), key=lambda x: x[1]['fqn'][-1]):
            if str(select) in data['original_file_path']:
                if name in data['fqn'][-2]:
                    if 'unique_key' in data['unrendered_config'] and len(data['fqn']) != 0 and dbtproject['name'] == data['fqn'][0]:
                        yaml += f"- name: {data['fqn'][-1]}\n"
                        yaml += "  description: This is a table in staging\n"
                        yaml += "  columns:\n"
                        yaml += f"   - name: {data['unrendered_config']['unique_key']}\n"
                        yaml += "     description: This is a surrogate key\n"
                        yaml += "     tests:\n"
                        yaml += f"      - not_null\n"
                        yaml += f"      - unique\n"
                        yaml += f"      \n"
                        file_name = f"_{name}_doc.yml"  # Use the name as the file name
                        file_path = os.path.join("\\".join(data['original_file_path'].split('\\')[:-1]), file_name)  # Specify the output folder path

                    else:
                        continue
                
                    with open(file_path, 'w') as file:
                        file.write(yaml)

if __name__ == '__main__':
    print("running this bad boi brb")
    dbtdocgen()
    print("Done! Please check in each model/submodel for your new yml files")

    
dbtdocgen


