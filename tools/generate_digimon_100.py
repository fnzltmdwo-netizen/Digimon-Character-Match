import csv
import re
import time
import random
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "frontend" / "images"
CSV_PATH = ROOT / "backend" / "digimon.csv"

API_URL = "https://digimon.fandom.com/api.php"

DIGIMON_NAMES = [
    "Agumon","Gabumon","Patamon","Tentomon","Palmon","Gatomon","Greymon","Garurumon","Angemon","Devimon",
    "WarGreymon","MetalGarurumon","Omnimon","Veemon","Guilmon","Renamon","Impmon","Terriermon","Angewomon","LadyDevimon",
    "Koromon","Tsunomon","Tokomon","Motimon","Tanemon","Salamon","MetalGreymon","WereGarurumon","MagnaAngemon","Lillymon",
    "Zudomon","Garudamon","MegaKabuterimon","Phoenixmon","Seraphimon","Magnadramon","Imperialdramon","ExVeemon","Paildramon","Flamedramon",
    "Raidramon","Magnamon","Wormmon","Stingmon","Dinobeemon","Growlmon","WarGrowlmon","Gallantmon","Kyubimon","Taomon",
    "Sakuyamon","Gargomon","Rapidmon","MegaGargomon","Beelzemon","MarineAngemon","Guardromon","Andromon","HiAndromon","Leomon",
    "SaberLeomon","Ogremon","Numemon","Sukamon","Etemon","MetalEtemon","Monzaemon","ToyAgumon","BlackAgumon","BlackWarGreymon",
    "SkullGreymon","Machinedramon","Myotismon","VenomMyotismon","Piedmon","Puppetmon","MetalSeadramon","Apocalymon","Diaboromon","Keramon",
    "Infermon","Armageddemon","Alphamon","UlforceVeedramon","Dynasmon","Craniamon","Jesmon","Gankoomon","Examon","Lucemon",
    "Lilithmon","Belphemon","Barbamon","Daemon","Leviamon","Crusadermon","Dorumon","Dorugamon","DoruGreymon","Dorugoramon"
]

STAGE_MAP = {
    "Koromon": "유년기", "Tsunomon": "유년기", "Tokomon": "유년기", "Motimon": "유년기", "Tanemon": "유년기",
    "Agumon": "성장기", "Gabumon": "성장기", "Patamon": "성장기", "Tentomon": "성장기", "Palmon": "성장기",
    "Gatomon": "성숙기", "Greymon": "성숙기", "Garurumon": "성숙기", "Angemon": "성숙기", "Devimon": "성숙기",
    "MetalGreymon": "완전체", "WereGarurumon": "완전체", "MagnaAngemon": "완전체", "Lillymon": "완전체",
    "WarGreymon": "궁극체", "MetalGarurumon": "궁극체", "Omnimon": "궁극체", "Gallantmon": "궁극체",
    "Alphamon": "궁극체", "Beelzemon": "궁극체", "Lucemon": "궁극체",
}

PERSONALITY_PRESET = {
    "Agumon": ("밝음|용감함|친근함", [82,45,58,10,92,78,45,20]),
    "Gabumon": ("차분함|따뜻함|부드러움", [78,55,45,15,70,85,40,35]),
    "Patamon": ("귀여움|순수함|밝음", [96,38,28,5,90,92,25,45]),
    "WarGreymon": ("강렬함|리더십|용감함", [18,88,98,25,72,35,98,40]),
    "MetalGarurumon": ("냉정함|세련됨|침착함", [20,96,90,45,38,35,82,58]),
    "Omnimon": ("완벽함|카리스마|균형감", [12,98,96,35,65,42,100,82]),
    "Beelzemon": ("어두움|카리스마|강렬함", [18,92,88,92,25,18,80,88]),
    "Angemon": ("신비로움|부드러움|정의감", [55,85,72,10,80,82,78,92]),
    "Angewomon": ("우아함|신비로움|부드러움", [62,90,70,12,78,80,76,96]),
    "LadyDevimon": ("도도함|강렬함|시크함", [30,92,75,90,28,18,72,88]),
}

PERSONALITIES = [
    ("귀여움|밝음|친근함", [85,45,35,10,88,80,30,30]),
    ("차분함|시크함|냉정함", [35,88,60,40,35,40,65,70]),
    ("강렬함|리더십|용감함", [25,78,92,35,60,35,88,45]),
    ("신비로움|우아함|부드러움", [55,84,58,25,65,78,60,92]),
    ("장난기|활발함|개성강함", [78,62,50,25,82,58,38,50]),
    ("어두움|카리스마|강렬함", [22,82,80,88,25,22,75,82]),
]

def safe(name):
    return re.sub(r"[^a-zA-Z0-9_-]", "", name.lower().replace(" ", "_"))

def get_image_url(title):
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": title,
        "redirects": 1,
    }
    r = requests.get(API_URL, params=params, timeout=15)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for page in pages.values():
        src = page.get("original", {}).get("source")
        if src:
            return src
    return None

def download(url, path):
    headers = {"User-Agent": "DigimonCharacterMatch/1.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    path.write_bytes(r.content)

def clamp(x):
    return max(0, min(100, int(x)))

def slightly_vary(scores):
    return [clamp(x + random.randint(-8, 8)) for x in scores]

def get_profile(name):
    if name in PERSONALITY_PRESET:
        personality, scores = PERSONALITY_PRESET[name]
        return personality, scores

    personality, base_scores = random.choice(PERSONALITIES)
    return personality, slightly_vary(base_scores)

def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    for idx, name in enumerate(DIGIMON_NAMES, 1):
        print(f"[{idx}/{len(DIGIMON_NAMES)}] {name}")

        filename = safe(name) + ".png"
        save_path = IMG_DIR / filename
        image_path = f"images/{filename}"

        try:
            url = get_image_url(name)
            if url:
                download(url, save_path)
                print("  ✅ image saved")
            else:
                image_path = f"https://placehold.co/420x420/030712/00eaff?text={name}"
                print("  ⚠️ no image")
        except Exception as e:
            image_path = f"https://placehold.co/420x420/030712/00eaff?text={name}"
            print(f"  ❌ failed: {e}")

        stage = STAGE_MAP.get(name, random.choice(["성장기", "성숙기", "완전체", "궁극체"]))
        digi_type = random.choice(["공룡형", "짐승형", "용형", "천사형", "마인형", "사이보그형", "식물형", "곤충형", "디지몬"])
        personality, scores = get_profile(name)

        rows.append({
            "name": name,
            "stage": stage,
            "type": digi_type,
            "personality": personality,
            "image_url": image_path,
            "description": f"{name}의 외형과 분위기를 기반으로 매칭되는 디지몬입니다.",
            "cute": scores[0],
            "cool": scores[1],
            "strong": scores[2],
            "dark": scores[3],
            "bright": scores[4],
            "kind": scores[5],
            "leader": scores[6],
            "mysterious": scores[7],
        })

        time.sleep(0.2)

    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name","stage","type","personality","image_url","description",
            "cute","cool","strong","dark","bright","kind","leader","mysterious"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print("\n🎉 100마리 생성 완료!")
    print("CSV:", CSV_PATH)
    print("이미지:", IMG_DIR)
    print("총 개수:", len(rows))

if __name__ == "__main__":
    main()