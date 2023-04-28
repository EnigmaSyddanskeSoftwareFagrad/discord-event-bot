import json
import string

import discord

def main():
    file = open('token.json')

    data = json.load(file)
    token: string = data["TOKEN"]

    print(token)


if __name__ == "__main__":
    main()