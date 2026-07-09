from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
from pathlib import Path
import pandas as pd
import os
import json

from vision import analyze_face, final_select_top3
from matcher import match_candidates


app = FastAPI(title="Digimon Character Match API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "digimon_ai.csv"


def load_digimon():
    if not CSV_PATH.exists():
        return []

    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        print("CSV 로드 오류:", e)
        return []


def get_evolution_route(name):
    routes = {
        "Agumon": ["Koromon", "Agumon", "Greymon", "MetalGreymon", "WarGreymon"],
        "Gabumon": ["Tsunomon", "Gabumon", "Garurumon", "WereGarurumon", "MetalGarurumon"],
        "Patamon": ["Tokomon", "Patamon", "Angemon", "MagnaAngemon", "Seraphimon"],
        "Tentomon": ["Motimon", "Tentomon", "Kabuterimon", "MegaKabuterimon", "HerculesKabuterimon"],
        "Palmon": ["Tanemon", "Palmon", "Togemon", "Lillymon", "Rosemon"],
        "Gatomon": ["Salamon", "Gatomon", "Angewomon", "Magnadramon"],
        "Greymon": ["Koromon", "Agumon", "Greymon", "MetalGreymon", "WarGreymon"],
        "Garurumon": ["Tsunomon", "Gabumon", "Garurumon", "WereGarurumon", "MetalGarurumon"],
        "Angemon": ["Tokomon", "Patamon", "Angemon", "MagnaAngemon", "Seraphimon"],
        "Devimon": ["DemiMeramon", "DemiDevimon", "Devimon", "Myotismon", "VenomMyotismon"],
        "WarGreymon": ["Koromon", "Agumon", "Greymon", "MetalGreymon", "WarGreymon"],
        "MetalGarurumon": ["Tsunomon", "Gabumon", "Garurumon", "WereGarurumon", "MetalGarurumon"],
        "Omnimon": ["Agumon + Gabumon", "WarGreymon + MetalGarurumon", "Omnimon"],
        "Veemon": ["Chibomon", "Veemon", "ExVeemon", "Paildramon", "Imperialdramon"],
        "Guilmon": ["Gigimon", "Guilmon", "Growlmon", "WarGrowlmon", "Gallantmon"],
        "Renamon": ["Viximon", "Renamon", "Kyubimon", "Taomon", "Sakuyamon"],
        "Impmon": ["Yaamon", "Impmon", "Wizardmon", "Baalmon", "Beelzemon"],
        "Terriermon": ["Gummymon", "Terriermon", "Gargomon", "Rapidmon", "MegaGargomon"],
        "Angewomon": ["Salamon", "Gatomon", "Angewomon", "Magnadramon"],
        "LadyDevimon": ["BlackGatomon", "LadyDevimon", "Lilithmon"],
    }

    return routes.get(name, [name])


def parse_gpt_top3(raw_text):
    try:
        cleaned = str(raw_text)
        cleaned = cleaned.replace("```json", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()
        return json.loads(cleaned)
    except Exception as e:
        print("GPT TOP3 파싱 오류:", e)
        print("원본:", raw_text)
        return []


@app.get("/")
def root():
    digimon_list = load_digimon()

    return {
        "message": "🐉 Digimon Character Match API is running!",
        "status": "success",
        "csv_exists": CSV_PATH.exists(),
        "csv_path": str(CSV_PATH),
        "digimon_count": len(digimon_list),
    }


@app.get("/status")
def status():
    digimon_list = load_digimon()

    return {
        "status": "ok",
        "csv_exists": CSV_PATH.exists(),
        "csv_path": str(CSV_PATH),
        "digimon_count": len(digimon_list),
    }


@app.get("/digimon")
def get_digimon():
    digimon_list = load_digimon()

    return {
        "count": len(digimon_list),
        "data": digimon_list,
    }


@app.post("/match")
async def match_digimon(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        digimon_list = load_digimon()

        if len(digimon_list) == 0:
            return {
                "success": False,
                "message": "digimon_ai.csv를 찾을 수 없거나 데이터가 비어 있습니다.",
                "csv_path": str(CSV_PATH),
                "results": [],
            }

        face_analysis = analyze_face(image_bytes)

        candidates = match_candidates(face_analysis, digimon_list, limit=10)

        if len(candidates) == 0:
            return {
                "success": False,
                "message": "매칭 후보를 만들 수 없습니다.",
                "face_analysis": face_analysis,
                "results": [],
            }

        gpt_raw = final_select_top3(face_analysis, candidates)
        gpt_results = parse_gpt_top3(gpt_raw)

        final_results = []

        for gpt_item in gpt_results[:3]:
            base_item = next(
                (item for item in candidates if item["name"] == gpt_item.get("name")),
                None,
            )

            if not base_item:
                continue

            final_results.append({
                **base_item,
                "rank": len(final_results) + 1,
                "score": gpt_item.get("score", base_item.get("score", 0)),
                "reason": gpt_item.get("reason", base_item.get("reason", "")),
            })

        if len(final_results) < 3:
            for item in candidates:
                if item["name"] not in [r["name"] for r in final_results]:
                    copied = dict(item)
                    copied["rank"] = len(final_results) + 1
                    final_results.append(copied)

                if len(final_results) == 3:
                    break

        return {
            "success": True,
            "message": "디지몬 닮은꼴 분석 완료!",
            "face_analysis": face_analysis,
            "evolution_route": get_evolution_route(final_results[0]["name"]) if final_results else [],
            "candidates": candidates,
            "image_info": {
                "filename": file.filename,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
            },
            "results": final_results,
        }

    except Exception as e:
        print("분석 오류:", e)

        return {
            "success": False,
            "message": f"분석 중 오류가 발생했습니다: {str(e)}",
            "results": [],
        }