const API_URL = "https://digimon-character-match.onrender.com";

const userNameInput = document.getElementById("userNameInput");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");
const loadingBox = document.getElementById("loadingBox");
const loadingText = document.getElementById("loadingText");
const barFill = document.getElementById("barFill");
const percentText = document.getElementById("percentText");
const resultBox = document.getElementById("resultBox");

window.currentResultId = null;

function getUserName() {
  return userNameInput?.value?.trim() || "친구";
}

function getDisplayName(item) {
  return item.name_ko || item.name || "";
}

function getImageSrc(imageUrl) {
  if (!imageUrl) return "";
  if (imageUrl.startsWith("http")) return imageUrl;
  return imageUrl.replace(/^\/+/, "");
}

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (!file) return;

  const imageUrl = URL.createObjectURL(file);
  preview.innerHTML = `<img src="${imageUrl}" alt="preview" />`;
  resultBox.style.display = "none";
});

function makeTrait(label, value) {
  const score = Number(value || 0);

  return `
    <div class="trait">
      <div class="trait-top">
        <span>${label}</span>
        <strong>${score}</strong>
      </div>
      <div class="trait-bar">
        <div class="trait-fill" style="width:${score}%"></div>
      </div>
    </div>
  `;
}

function formatFaceAnalysis(raw) {
  try {
    const cleaned = String(raw).replace(/```json|```/g, "").trim();
    const data = JSON.parse(cleaned);

    return `
      <div class="face-grid">
        <div class="face-label">얼굴형</div><div>${data.face_shape || "-"}</div>
        <div class="face-label">눈매</div><div>${data.eyes || "-"}</div>
        <div class="face-label">코</div><div>${data.nose || "-"}</div>
        <div class="face-label">입</div><div>${data.mouth || "-"}</div>
        <div class="face-label">턱선</div><div>${data.jaw || "-"}</div>
        <div class="face-label">분위기</div><div>${data.vibe || "-"}</div>
      </div>

      <div class="trait-box">
        ${makeTrait("귀여움", data.cute)}
        ${makeTrait("시크함", data.cool)}
        ${makeTrait("강함", data.strong)}
        ${makeTrait("어두움", data.dark)}
        ${makeTrait("밝음", data.bright)}
        ${makeTrait("상냥함", data.kind)}
        ${makeTrait("리더십", data.leader)}
        ${makeTrait("신비로움", data.mysterious)}
      </div>
    `;
  } catch (e) {
    return String(raw);
  }
}

function startLoadingAnimation() {
  loadingBox.style.display = "block";
  resultBox.style.display = "none";

  let percent = 0;

  const messages = [
    "⚡ 디지바이스 연결중...",
    "🔍 얼굴 데이터 스캔중...",
    "🐉 디지몬 후보 탐색중...",
    "🔥 진화 루트 계산중...",
    "✨ 최종 결과 생성중..."
  ];

  const timer = setInterval(() => {
    percent += Math.floor(Math.random() * 9) + 4;
    if (percent > 96) percent = 96;

    barFill.style.width = `${percent}%`;
    percentText.innerText = `${percent}%`;

    const index = Math.min(Math.floor(percent / 22), messages.length - 1);
    loadingText.innerText = messages[index];
  }, 350);

  return timer;
}

function finishLoadingAnimation(timer) {
  clearInterval(timer);
  barFill.style.width = "100%";
  percentText.innerText = "100%";
  loadingText.innerText = "✨ 분석 완료!";
}

function buildEvolutionRoute(route) {
  if (!route || route.length === 0) return "";

  return route.map((name, index) => `
    <div class="evo-step" style="animation-delay:${index * 0.35}s">
      <span class="badge">${name}</span>
    </div>
    ${index < route.length - 1 ? `
      <div class="evo-arrow" style="animation-delay:${index * 0.35 + 0.18}s">↓</div>
    ` : ""}
  `).join("");
}

function buildCards(results) {
  return results.map(item => {
    const displayName = getDisplayName(item);

    return `
      <div class="card ${item.rank === 1 ? "rank1" : ""}">
        <h2>${item.rank === 1 ? "🥇" : item.rank === 2 ? "🥈" : "🥉"} ${displayName}</h2>

        <img
          src="${getImageSrc(item.image_url)}"
          alt="${displayName}"
          onerror="this.src='https://placehold.co/300x300/fff7e6/ff7a00?text=${encodeURIComponent(displayName)}';"
        />

        <div class="score">${item.score}%</div>

        <div class="score-bar">
          <div class="score-fill" style="width:${item.score}%"></div>
        </div>

        <p>
          <span class="badge">${item.stage || ""}</span>
          <span class="badge">${item.type || ""}</span>
        </p>

        <p class="reason">${item.reason || ""}</p>
        <p class="desc">${item.description || ""}</p>
      </div>
    `;
  }).join("");
}

function buildCandidates(candidates) {
  return candidates.map((item, index) => `
    <div class="candidate-item">
      <span>${item.rank || index + 1}. ${getDisplayName(item)}</span>
      <strong>${item.score}%</strong>
    </div>
  `).join("");
}

function toggleCandidates() {
  const list = document.getElementById("candidateList");
  if (!list) return;
  list.classList.toggle("open");
}

function renderResult(data) {
  window.currentResultId = data.result_id;

  const results = data.results || [];

  if (results.length === 0) {
    resultBox.style.display = "block";
    resultBox.innerHTML = "❌ 결과를 찾을 수 없어요.";
    return;
  }

  const userName = data.user_name || getUserName();
  const first = results[0];
  const firstName = getDisplayName(first);

  const evolutionHtml = buildEvolutionRoute(data.evolution_route || []);
  const cards = buildCards(results);
  const candidateHtml = buildCandidates(data.candidates || []);

  resultBox.style.display = "block";
  resultBox.innerHTML = `
    <div class="result-title hero-result">
      <div class="champion-label">ACCESS COMPLETE</div>

      <img
        class="champion-img"
        src="${getImageSrc(first.image_url)}"
        alt="${firstName}"
        onerror="this.src='https://placehold.co/420x420/030712/00eaff?text=${encodeURIComponent(firstName)}';"
      />

      <h2>${userName}님의 DIGIMON</h2>
      <h1>${firstName}</h1>
      <p class="score">${first.score}% MATCH</p>
      <p class="reason">${first.reason || ""}</p>
    </div>

    <div class="evolution-box">
      <h3>🔥 EVOLUTION ROUTE</h3>
      <div class="evolution-route">${evolutionHtml}</div>
    </div>

    <div class="face-box">
      <h3>🧠 FACE ANALYSIS</h3>
      ${formatFaceAnalysis(data.face_analysis)}
    </div>

    ${cards}

    <div class="candidate-box">
      <button class="candidate-toggle" onclick="toggleCandidates()">
        🔍 AI 후보 10개 보기
      </button>

      <div class="candidate-list" id="candidateList">
        ${candidateHtml}
      </div>
    </div>

    <div class="action-row">
      <button class="share-btn" onclick="shareResultCard()">
        💬 결과 링크 공유
      </button>

      <button class="retry-btn" onclick="resetTest()">
        🔄 다시하기
      </button>
    </div>
  `;
}

function resetTest() {
  window.currentResultId = null;
  imageInput.value = "";
  userNameInput.value = "";

  preview.innerHTML = `
    <div>
      <strong>PHOTO UPLOAD</strong>
      <p>Click to select your image</p>
    </div>
  `;

  resultBox.style.display = "none";
  loadingBox.style.display = "none";
  barFill.style.width = "0%";
  percentText.innerText = "0%";
  analyzeBtn.disabled = false;
  analyzeBtn.innerText = "⚡ ANALYZE NOW";
}

async function analyzeImage() {
  const file = imageInput.files[0];

  if (!file) {
    alert("사진을 먼저 선택해줘!");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.innerText = "분석중... 🐉";

  const timer = startLoadingAnimation();

  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_name", getUserName());

  try {
    const response = await fetch(`${API_URL}/match`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    finishLoadingAnimation(timer);

    setTimeout(() => {
      loadingBox.style.display = "none";

      if (!data.success) {
        resultBox.style.display = "block";
        resultBox.innerHTML = `❌ ${data.message}`;
        return;
      }

      renderResult(data);
    }, 500);

  } catch (error) {
    console.error(error);
    clearInterval(timer);
    loadingBox.style.display = "none";
    resultBox.style.display = "block";
    resultBox.innerHTML = "❌ 분석 실패! 서버가 켜져있는지 확인해줘.";
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerText = "⚡ ANALYZE NOW";
  }
}

async function shareResultCard() {
  const resultId = window.currentResultId;

  if (!resultId) {
    alert("공유할 결과가 없어요!");
    return;
  }

  const shareUrl = `${window.location.origin}/result.html?id=${resultId}`;
  const userName = getUserName();

  if (navigator.share) {
    try {
      await navigator.share({
        title: "디지몬 닮은꼴 테스트",
        text: `${userName}님의 디지몬 닮은꼴 결과가 도착했습니다!`,
        url: shareUrl
      });
    } catch (e) {
      console.log("공유 취소 또는 실패:", e);
    }
  } else {
    await navigator.clipboard.writeText(shareUrl);
    alert("결과 링크가 복사됐어! 카톡에 붙여넣으면 돼.");
  }
}