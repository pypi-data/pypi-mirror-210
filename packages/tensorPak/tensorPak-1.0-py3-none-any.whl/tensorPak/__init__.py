import pkg_resources

def models(file_number):
    file_path = pkg_resources.resource_filename('tensorPak', f'{file_number}.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    return content
