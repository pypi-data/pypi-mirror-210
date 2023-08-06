def models(file_number):
    file = open(f"tensorflowAndKeras/{file_number}.txt", "r")
    content = file.read()
    return content
