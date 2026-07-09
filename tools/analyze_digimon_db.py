import os
import csv
import json
import time
import base64
from pathlib import Path
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

INPUT_CSV = BACKEND_DIR / "digimon.csv"
OUTPUT_CSV = BACKEND_DIR / "digimon_ai.csv"
FAILED_TXT = BACKEND_DIR / "digimon_ai_failed.txt"
IMAGE_DIR = FRONTEND_DIR / "images"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FIELDNAMES = [
    "name",
    "stage",
    "type",
    "personality",
    "image_url",
    "description",
    "cute",
    "cool",
    "strong",
    "dark",
    "bright",
    "kind",
    "leader",
    "mysterious",
]


def clamp(value):
    try:
        value = int(float(value))
    except Exception:
        value = 50
    return max(0, min(100, value))


def ensure_output_csv():
    if OUTPUT_CSV.exists():
        return

    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()


def load_existing_names():
    if not OUTPUT_CSV.exists():
        return set()

    names = set()

    with open(OUTPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if name:
                names.add(name)

    return names


def load_digimons():
    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(image_path):
    ext = image_path.suffix.lower()

    if ext == ".png":
        return "image/png"
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".webp":
        return "image/webp"

    return "image/jpeg"


def find_image_path(image_url):
    image_url = image_url.replace("\\", "/").strip()

    if image_url.startswith("images/"):
        filename = image_url.replace("images/", "", 1)
    else:
        filename = image_url

    image_path = IMAGE_DIR / filename

    if image_path.exists():
        return image_path

    stem = Path(filename).stem

    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        candidate = IMAGE_DIR / f"{stem}{ext}"
        if candidate.exists():
            return candidate

    return None


def save_failed(name, reason):
    with open(FAILED_TXT, "a", encoding="utf-8-sig") as f:
        f.write(f"{name} - {reason}\n")


def analyze_with_gpt(name, stage, digimon_type, image_path, max_retries=3):
    image_base64 = image_to_base64(image_path)
    mime_type = get_mime_type(image_path)

    prompt = f"""
너는 디지몬 캐릭터 외형 분석 AI야.

디지몬 이름: {name}
진화 단계: {stage}
타입: {digimon_type}

이미지를 직접 보고 이 디지몬의 외형과 분위기를 분석해.

아래 항목을 0~100점으로 평가해:
- cute: 귀여움
- cool: 멋짐
- strong: 강해 보임
- dark: 어둡고 다크한 느낌
- bright: 밝고 긍정적인 느낌
- kind: 착하고 친근한 느낌
- leader: 리더 또는 주인공 같은 느낌
- mysterious: 신비로운 느낌

personality는 한국어 키워드 3개를 | 로 구분해서 작성해.
description은 한국어 한 문장으로 자연스럽게 작성해.
닮은꼴 테스트 결과 카드에 어울리게 작성해.

반드시 JSON만 출력해.
마크다운 코드블록은 쓰지 마.

JSON 형식:
{{
  "personality": "밝음|용감함|친근함",
  "description": "밝고 용감한 분위기가 느껴지는 친근한 디지몬입니다.",
  "cute": 0,
  "cool": 0,
  "strong": 0,
  "dark": 0,
  "bright": 0,
  "kind": 0,
  "leader": 0,
  "mysterious": 0
}}
"""

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.2,
                max_tokens=400,
            )

            data = json.loads(response.choices[0].message.content)

            return {
                "personality": str(data.get("personality", "")).strip(),
                "description": str(data.get("description", "")).strip(),
                "cute": clamp(data.get("cute")),
                "cool": clamp(data.get("cool")),
                "strong": clamp(data.get("strong")),
                "dark": clamp(data.get("dark")),
                "bright": clamp(data.get("bright")),
                "kind": clamp(data.get("kind")),
                "leader": clamp(data.get("leader")),
                "mysterious": clamp(data.get("mysterious")),
            }

        except Exception as e:
            print(f"⚠️ GPT 오류 {attempt}/{max_retries}: {name}")
            print(f"   {e}")

            if attempt < max_retries:
                time.sleep(3)
            else:
                return None


def append_result(row):
    with open(OUTPUT_CSV, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


def format_seconds(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    sec = seconds % 60

    if minutes == 0:
        return f"{sec}초"

    return f"{minutes}분 {sec}초"


def main():
    print("====================================")
    print("디지몬 GPT Vision 재분석 시작")
    print("====================================")

    if not INPUT_CSV.exists():
        print(f"❌ digimon.csv 없음: {INPUT_CSV}")
        return

    if not IMAGE_DIR.exists():
        print(f"❌ 이미지 폴더 없음: {IMAGE_DIR}")
        return

    ensure_output_csv()

    digimons = load_digimons()
    done_names = load_existing_names()

    total = len(digimons)
    start_time = time.time()

    print(f"전체 디지몬 수: {total}")
    print(f"이미 완료된 수: {len(done_names)}")
    print("------------------------------------")

    for index, digimon in enumerate(digimons, start=1):
        name = digimon.get("name", "").strip()
        stage = digimon.get("stage", "").strip()
        digimon_type = digimon.get("type", "").strip()
        image_url = digimon.get("image_url", "").strip()

        if not name or not image_url:
            print(f"⚠️ {index}/{total} 데이터 누락으로 건너뜀")
            save_failed(f"row {index}", "name 또는 image_url 없음")
            continue

        if name in done_names:
            print(f"⏭️ {index}/{total} 이미 완료: {name}")
            continue

        image_path = find_image_path(image_url)

        if image_path is None:
            print(f"❌ {index}/{total} 이미지 없음: {name} / {image_url}")
            save_failed(name, f"이미지 없음: {image_url}")
            continue

        completed = len(done_names)
        elapsed = time.time() - start_time

        if completed > 0:
            avg = elapsed / completed
            eta = format_seconds(avg * (total - completed))
        else:
            eta = "계산 중"

        print(f"🔍 {index}/{total} 분석 중: {name} | 예상 남은 시간: {eta}")

        result = analyze_with_gpt(
            name=name,
            stage=stage,
            digimon_type=digimon_type,
            image_path=image_path,
        )

        if result is None:
            print(f"❌ 최종 실패: {name}")
            save_failed(name, "GPT 분석 실패")
            continue

        output_row = {
            "name": name,
            "stage": stage,
            "type": digimon_type,
            "personality": result["personality"],
            "image_url": image_url,
            "description": result["description"],
            "cute": result["cute"],
            "cool": result["cool"],
            "strong": result["strong"],
            "dark": result["dark"],
            "bright": result["bright"],
            "kind": result["kind"],
            "leader": result["leader"],
            "mysterious": result["mysterious"],
        }

        append_result(output_row)
        done_names.add(name)

        print(f"✅ 완료: {name}")
        time.sleep(0.7)

    print("------------------------------------")
    print("🎉 디지몬 GPT Vision 재분석 완료")
    print(f"저장 위치: {OUTPUT_CSV}")
    print(f"실패 목록: {FAILED_TXT}")


if __name__ == "__main__":
    main()