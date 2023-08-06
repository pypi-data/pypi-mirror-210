import os


def format_filename(filename):
    wrong_chars = [" ", ":", "/", ".", "-", "(", ")", "!", "?"]
    name = filename
    for wrong_char in wrong_chars:
        name = name.replace(wrong_char, "_")
    return name


def get_py_text_content(img_names):
    text = ""
    for img_name in img_names:
        text += f"{format_filename(img_name)} = '{img_name}'\n"
    return text


def main():
    resources_path = os.path.join(os.getcwd(), "resources")
    img_raw_names = os.listdir(resources_path)
    img_names = list(map(lambda x: "".join(x.split(".")[:-1]), img_raw_names))
    tagsFile = os.path.join(os.getcwd(), "src/tags.py")
    file_content = get_py_text_content(img_names)
    print(file_content)
    with open(tagsFile, "w") as tag:
        tag.write(file_content)
