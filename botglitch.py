import random

ZALGO_CHARS = [chr(i) for i in range(0x0300, 0x036F + 1)]


def glitch(text: str) -> str:
    result = ""
    for char in text:
        result += char
        for _ in range(random.randint(1, 5)):
            result += random.choice(ZALGO_CHARS)
    return result


if __name__ == '__main__':
    print(glitch('just a test'))
