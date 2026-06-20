from urllib.parse import urlencode

base = "https://www.volleyscores.be/index.php"

params = {
    "v": "2",
    "ss": "0",
    "isActiveSeason": "1",
    "t": "Ploeg (NAT1H) Mendo Booischot A",
    "a": "t",
    "se": "13",
    "ti": "101645",
    "lng": "nl",
}

url = f"{base}?{urlencode(params)}"

if __name__ == "__main__":
    print(url)