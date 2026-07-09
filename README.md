# 🐉 Digimon Character Match

AI 얼굴 분석을 통해 가장 닮은 디지몬을 찾아주는 웹서비스입니다.

## 기능
- 사진 업로드
- AI 얼굴 특징 분석
- 디지몬 TOP3 매칭
- 진화 루트 표시
- 결과 복사
- 반응형 UI

## 기술 스택
- FastAPI
- OpenAI Vision
- HTML/CSS/JavaScript
- Pandas
- Pillow

## 실행 방법

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload