import csv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "backend" / "digimon_ai.csv"
BACKUP_PATH = ROOT_DIR / "backend" / "digimon_ai_backup.csv"

NAME_KO = {
    "Agumon": "아구몬",
    "Gabumon": "파피몬",
    "Patamon": "파닥몬",
    "Tentomon": "텐타몬",
    "Palmon": "팔몬",
    "Gatomon": "가트몬",
    "Greymon": "그레이몬",
    "Garurumon": "가루몬",
    "Angemon": "엔젤몬",
    "Devimon": "데블몬",
    "WarGreymon": "워그레이몬",
    "MetalGarurumon": "메탈가루몬",
    "Omnimon": "오메가몬",
    "Veemon": "브이몬",
    "Guilmon": "길몬",
    "Renamon": "레나몬",
    "Impmon": "임프몬",
    "Terriermon": "테리어몬",
    "Angewomon": "엔젤우몬",
    "LadyDevimon": "레이디데블몬",

    "Koromon": "코로몬",
    "Tsunomon": "뿔몬",
    "Tokomon": "토코몬",
    "Motimon": "모티몬",
    "Tanemon": "타네몬",
    "Salamon": "플롯트몬",
    "WereGarurumon": "워가루몬",
    "MagnaAngemon": "홀리엔젤몬",
    "Lillymon": "릴리몬",
    "Zudomon": "쥬드몬",
    "Garudamon": "가루다몬",
    "Phoenixmon": "피닉스몬",
    "Seraphimon": "세라피몬",
    "Magnadramon": "홀리드라몬",
    "ExVeemon": "엑스브이몬",
    "Paildramon": "파일드라몬",
    "Flamedramon": "화염드라몬",
    "Raidramon": "번개드라몬",
    "Magnamon": "매그너몬",
    "Wormmon": "추추몬",
    "Stingmon": "스팅몬",
    "Dinobeemon": "디노비몬",
    "Growlmon": "그라우몬",
    "WarGrowlmon": "메가로그라우몬",
    "Gallantmon": "듀크몬",
    "Kyubimon": "구미호몬",
    "Taomon": "도사몬",
    "Sakuyamon": "샤크라몬",
    "Gargomon": "가르고몬",
    "Rapidmon": "래피드몬",
    "MegaGargomon": "세인트가르고몬",
    "Beelzemon": "베르제브몬",
    "MarineAngemon": "마린엔젤몬",
    "Guardromon": "가드로몬",
    "Andromon": "안드로몬",
    "HiAndromon": "하이안드로몬",
    "Leomon": "레오몬",
    "SaberLeomon": "샤벨레오몬",
    "Ogremon": "우가몬",
    "Numemon": "워매몬",
    "Sukamon": "스카몬",
    "Etemon": "에테몬",
    "MetalEtemon": "메탈에테몬",
    "Monzaemon": "몬자에몬",
    "ToyAgumon": "토이아구몬",
    "BlackAgumon": "블랙아구몬",
    "BlackWarGreymon": "블랙워그레이몬",
    "SkullGreymon": "스컬그레이몬",
    "Machinedramon": "파워드라몬",
    "Myotismon": "묘티스몬",
    "VenomMyotismon": "베놈묘티스몬",
    "Piedmon": "피에몬",
    "Puppetmon": "피노키몬",
    "MetalSeadramon": "메탈시드라몬",
    "Apocalymon": "아포카리몬",
    "Diaboromon": "디아블로몬",
    "Keramon": "케라몬",
    "Infermon": "인펠몬",
    "Armageddemon": "아마게몬",
    "Alphamon": "알파몬",
    "UlforceVeedramon": "알포스브이드라몬",
    "Dynasmon": "듀나스몬",
    "Craniamon": "크레니엄몬",
    "Jesmon": "제스몬",
    "Gankoomon": "간쿠몬",
    "Examon": "엑자몬",
    "Lucemon": "루체몬",
    "Lilithmon": "리리스몬",
    "Barbamon": "발바몬",
    "Daemon": "데몬",
    "Leviamon": "리바이어몬",
    "Crusadermon": "로드나이트몬",
    "Dorumon": "돌몬",
    "Dorugamon": "돌가몬",
    "DoruGreymon": "돌그레이몬",
    "Dorugoramon": "돌고라몬",
}


def main():
    if not CSV_PATH.exists():
        print(f"❌ 파일 없음: {CSV_PATH}")
        return

    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    if not rows:
        print("❌ 데이터가 비어있음")
        return

    # 백업 생성
    with open(BACKUP_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # name_ko 컬럼 추가
    if "name_ko" not in fieldnames:
        fieldnames.insert(1, "name_ko")

    unknown = []

    for row in rows:
        eng = row.get("name", "").strip()
        ko = NAME_KO.get(eng, eng)

        row["name_ko"] = ko

        if ko == eng:
            unknown.append(eng)

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("✅ name_ko 추가 완료")
    print(f"백업 파일: {BACKUP_PATH}")

    if unknown:
        print("⚠️ 한글 이름 없는 디지몬:")
        for name in unknown:
            print("-", name)


if __name__ == "__main__":
    main()