import json 
import click
import yaml

@click.command()
@click.option('--select', type=str)
def dbdoc_gen(select):
    
    with open(r"target/catalog.json") as file:
        catalog_data = json.load(file)
        
    with open(r"dbt_project.yml") as file:
        dbtproject = yaml.safe_load(file)

    tables = {}
    dbdiagram_string = ""

    for model, data in catalog_data['nodes'].items():
        if ('fct' in model or 'dim' in model) and dbtproject['name'] == model.split('.')[1]:
                columns_datatypes = {}
                for col_name, col_metadata in data['columns'].items():
                    columns_datatypes[col_name] = col_metadata['type']
                tables[model] = columns_datatypes

    with open("dbdiagram_string.txt", "w") as f:

        for table, cols in tables.items():
            if dbtproject['name'] == table.split('.')[1]:
                dbdiagram_string = dbdiagram_string + "Table " + f'"{table}"' + " {\n"
                for col, dtype in cols.items():
                    dbdiagram_string = dbdiagram_string + f'"{col}"' + " " + f'"{dtype}"' + "\n"
                dbdiagram_string = dbdiagram_string + "}\n"

        print(dbdiagram_string, file=f)

        duplicates = []
        for from_table, from_cols in tables.items():
            for from_col in from_cols.keys():
                for to_table, to_cols in tables.items():
                    if from_table != to_table:
                        for to_col in to_cols.keys():
                            if to_col == from_col and (('id' in to_col.lower() or 'id' in from_col.lower()) or ('skey' in to_col.lower() or 'skey' in from_col.lower())):
                                if ''.join([from_table,from_col,to_table,to_col]) not in duplicates:
                                    print(f"Ref: "f'"{from_table}"'"."f'"{from_col}"' " - " f'"{to_table}"'"."f'"{to_col}"', file=f)
                                    duplicates.extend([''.join([from_table,from_col,to_table,to_col]),''.join([to_table,to_col,from_table,from_col])])

    f.close()
    
if __name__ == '__main__':
    dbdoc_gen()
    
    
