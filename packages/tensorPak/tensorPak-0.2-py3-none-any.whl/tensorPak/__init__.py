def models(file_number):
    file = open(f"tensorPak/{file_number}.txt", "r")
    content = file.read()
    return content
