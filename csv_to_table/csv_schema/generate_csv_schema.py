from tableschema import Table
def get_schema(csv_path):
    table = Table(csv_path)
    schema = table.infer()

    return schema['fields']