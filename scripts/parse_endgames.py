import re

# pattern = re.compile('(-\s\d+\s-)\n+.*\n.*\n*.*\n+.*\n*([\+|=]) Z?A?Z?\s*(\d{4,4}\.\d{2,2}\s[a-h]\d[a-h]\d)')
pattern = re.compile('(-\s\d+\s-)')

def main(path):
    with open(path) as f:
        text = f.read()
        endgames = pattern.findall(text)

    if endgames is not None:
        for i, endgame in enumerate(endgames, 1):
            if i != int(endgame.replace('-', '').strip()):
                print(f"{i} != {endgame}")
                break
            else:
                print(i, endgame)

if __name__ == '__main__':
    path = './data/schaakstudiespinsels2_from_docx.txt'
    main(path)