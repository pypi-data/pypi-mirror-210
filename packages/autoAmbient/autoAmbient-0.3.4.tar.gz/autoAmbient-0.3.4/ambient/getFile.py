import sys
import requests


def getExtension(path):
    return path.split("?")[0].split(".")[-1]


def main():
    if len(sys.argv) < 3:
        return sys.stderr.write("está faltando um parametro")
    path = sys.argv[1]
    adjustedPath = path.replace("github.com", "raw.githubusercontent.com")
    adjustedPath = adjustedPath.replace("/blob/", "/")
    print("obterndo arquivo de", adjustedPath)
    file_name = sys.argv[2]
    content = requests.get(adjustedPath, stream=True).content
    if content == "404: Not Found":
        return sys.stderr.write("arquivo não encontrado")
    with open(f"{file_name}.{getExtension(adjustedPath)}", "wb") as f:
        f.write(content)
    print("arquivo salvo com sucesso")
