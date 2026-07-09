import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

FEATURES = [
    "cute",
    "cool",
    "strong",
    "dark",
    "bright",
    "kind",
    "leader",
    "mysterious",
]


def analyze_face(image_bytes):
    prompt = """
사진 속 사람의 인상과 분위기를 디지몬 매칭용으로 분석해줘.

아래 항목을 0~100점으로 평가해줘.

- cute
- cool
- strong
- dark
- bright
- kind
- leader
- mysterious

반드시 JSON 형식으로만 답해.

예시:
{
  "cute": 70,
  "cool": 65,
  "strong": 45,
  "dark": 20,
  "bright": 80,
  "kind": 75,
  "leader": 50,
  "mysterious": 30
}
"""

    import base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
        temperature=0.2,
        max_tokens=300,
    )

    return response.choices[0].message.content


def final_select_top3(face_analysis, candidates):
    prompt = f"""
너는 디지몬 닮은꼴 테스트 최종 심사 AI야.

사람 얼굴 분석 결과:
{face_analysis}

후보 디지몬 목록:
{json.dumps(candidates, ensure_ascii=False)}

위 후보 중에서 최종 TOP 3를 골라줘.

반드시 JSON 배열 형식으로만 답해.

형식:
[
  {{
    "name": "Agumon",
    "score": 94,
    "reason": "밝고 친근한 인상이 Agumon의 에너지와 잘 어울려요."
  }}
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=700,
    )

    return response.choices[0].message.content