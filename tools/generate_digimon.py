import csv
import os
import re
import time
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_IMAGES_DIR = ROOT_DIR / "frontend" / "images"
BACKEND_CSV_PATH = ROOT_DIR / "backend" / "digimon.csv"

API_URL = "https://digimon.fandom.com/api.php"

DIGIMON_LIST = [
    ("아구몬", "Agumon", "성장기", "공룡형", "밝음|용감함|친근함", "밝고 용감한 분위기의 대표 성장기 디지몬"),
    ("파피몬", "Gabumon", "성장기", "파충류형", "차분함|따뜻함|부드러움", "차분하고 따뜻한 인상의 성장기 디지몬"),
    ("파닥몬", "Patamon", "성장기", "포유류형", "귀여움|순수함|밝음", "순하고 귀여운 분위기의 디지몬"),
    ("텐타몬", "Tentomon", "성장기", "곤충형", "성실함|똑똑함|친근함", "성실하고 지적인 느낌의 곤충형 디지몬"),
    ("팔몬", "Palmon", "성장기", "식물형", "상냥함|부드러움|밝음", "상냥하고 포근한 분위기의 식물형 디지몬"),
    ("가트몬", "Gatomon", "성숙기", "성수형", "도도함|귀여움|민첩함", "도도하면서도 귀여운 분위기의 성숙기 디지몬"),
    ("그레이몬", "Greymon", "성숙기", "공룡형", "강함|열정|직진형", "강한 인상과 뜨거운 에너지가 느껴지는 디지몬"),
    ("가루몬", "Garurumon", "성숙기", "짐승형", "차가움|충성심|냉정함", "차분하고 날카로운 분위기의 늑대형 디지몬"),
    ("엔젤몬", "Angemon", "성숙기", "천사형", "신비로움|부드러움|정의감", "신비롭고 부드러운 분위기의 천사형 디지몬"),
    ("데블몬", "Devimon", "성숙기", "마인형", "어두움|카리스마|강렬함", "어둡고 강렬한 카리스마가 느껴지는 디지몬"),
    ("워그레이몬", "WarGreymon", "궁극체", "용인형", "강렬함|리더십|용감함", "강렬한 눈빛과 리더십이 돋보이는 궁극체 디지몬"),
    ("메탈가루몬", "MetalGarurumon", "궁극체", "사이보그형", "냉정함|세련됨|침착함", "차갑고 세련된 분위기의 궁극체 디지몬"),
    ("오메가몬", "Omnimon", "궁극체", "성기사형", "완벽함|카리스마|균형감", "강함과 차분함이 공존하는 성기사형 디지몬"),
    ("브이몬", "Veemon", "성장기", "소룡형", "활발함|장난기|밝음", "활발하고 장난기 있는 밝은 분위기의 디지몬"),
    ("길몬", "Guilmon", "성장기", "파충류형", "순수함|엉뚱함|강한잠재력", "순수하지만 강한 잠재력이 느껴지는 디지몬"),
    ("레나몬", "Renamon", "성장기", "짐승인형", "시크함|차분함|민첩함", "시크하고 차분한 분위기의 여우형 디지몬"),
    ("임프몬", "Impmon", "성장기", "소악마형", "장난기|까칠함|개성강함", "장난기 많고 개성이 강한 소악마형 디지몬"),
    ("테리어몬", "Terriermon", "성장기", "짐승형", "귀여움|여유로움|친근함", "귀엽고 여유로운 분위기의 디지몬"),
    ("엔젤우몬", "Angewomon", "완전체", "대천사형", "우아함|신비로움|부드러움", "우아하고 신비로운 분위기의 완전체 디지몬"),
    ("레이디데블몬", "LadyDevimon", "완전체", "타천사형", "도도함|강렬함|시크함", "도도하고 시크한 카리스마가 있는 디지몬"),
]


def safe_filename(name):
    return re.sub(r"[^a-zA-Z0-9_-]", "", name.lower())


def get_image_url(title):
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": title,
        "redirects": 1,
    }

    res = requests.get(API_URL, params=params, timeout=15)
    res.raise_for_status()
    data = res.json()

    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():
        original = page.get("original")
        if original and original.get("source"):
            return original["source"]

    return None


def download_image(url, save_path):
    headers = {
        "User-Agent": "DigimonCharacterMatch/1.0"
    }

    res = requests.get(url, headers=headers, timeout=20)
    res.raise_for_status()

    save_path.write_bytes(res.content)


def main():
    FRONTEND_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    for ko_name, en_name, stage, digi_type, personality, description in DIGIMON_LIST:
        print(f"🔍 {en_name} 이미지 찾는 중...")

        filename = f"{safe_filename(en_name)}.png"
        save_path = FRONTEND_IMAGES_DIR / filename
        frontend_path = f"images/{filename}"

        try:
            image_url = get_image_url(en_name)

            if image_url:
                print(f"⬇️ 다운로드: {image_url}")
                download_image(image_url, save_path)
                print(f"✅ 저장 완료: {save_path}")
            else:
                print(f"⚠️ 이미지 못 찾음: {en_name}")
                frontend_path = f"https://placehold.co/420x420/030712/00eaff?text={en_name}"

        except Exception as e:
            print(f"❌ 실패: {en_name} / {e}")
            frontend_path = f"https://placehold.co/420x420/030712/00eaff?text={en_name}"

        rows.append({
            "name": ko_name,
            "stage": stage,
            "type": digi_type,
            "personality": personality,
            "image_url": frontend_path,
            "description": description,
        })

        time.sleep(0.4)

    with open(BACKEND_CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "stage", "type", "personality", "image_url", "description"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n🎉 완료!")
    print(f"CSV 생성: {BACKEND_CSV_PATH}")
    print(f"이미지 폴더: {FRONTEND_IMAGES_DIR}")


if __name__ == "__main__":
    main()