import json
import random

FEATURES = [
    "cute", "cool", "strong", "dark",
    "bright", "kind", "leader", "mysterious"
]


def to_int(value, default=50):
    try:
        return int(float(value))
    except Exception:
        return default


def parse_face_analysis(face_analysis):
    if isinstance(face_analysis, dict):
        return face_analysis

    try:
        text = str(face_analysis).replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {}


def calc_match_score(face, digimon):
    total = 0

    for key in FEATURES:
        face_score = to_int(face.get(key), 50)
        digi_score = to_int(digimon.get(key), 50)

        diff = abs(face_score - digi_score)
        total += 100 - diff

    max_total = len(FEATURES) * 100
    percent = round((total / max_total) * 100)

    return max(55, min(98, percent))


def make_reason(face, digimon, score):
    personality = digimon.get("personality", "")
    name = digimon.get("name", "이 디지몬")

    if personality:
        return f"{personality.replace('|', '·')} 분위기가 얼굴 분석 결과와 잘 맞아서 선택됐어!"

    return f"{name}의 분위기와 얼굴 분석 결과가 잘 어울려서 선택됐어!"


def match_candidates(face_analysis, digimon_list, limit=10):
    face = parse_face_analysis(face_analysis)

    candidates = []

    for digimon in digimon_list:
        score = calc_match_score(face, digimon)

        # 완전 동일 결과 방지용 아주 작은 흔들림
        score = score + random.randint(-2, 2)
        score = max(55, min(98, score))

        item = dict(digimon)
        item["score"] = score
        item["reason"] = make_reason(face, digimon, score)

        candidates.append(item)

    candidates.sort(key=lambda x: x["score"], reverse=True)

    results = []
    for index, item in enumerate(candidates[:limit], start=1):
        item["rank"] = index
        results.append(item)

    return results