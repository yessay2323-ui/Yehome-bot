import time
import logging
import requests
import google.generativeai as genai

TELEGRAM_TOKEN = "8645035782:AAFCDcT-dk1SuUIsYE2hpJp3po3arLhuMds"
CHAT_ID = "8757312611"
GEMINI_API_KEY = "AIzaSyDftxUKG6ysLrzQJOLyM5oQ0m2vTPfNFew"

MY_PROFILE = {
    "나이": 29,
    "거주지역": "서울",
    "무주택여부": True,
    "혼인상태": "미혼",
    "취업상태": "구직중",
    "월소득_만원": 0,
    "자동차보유": False,
    "부양가족수": 0,
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def send(text, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        logger.error(f"전송 실패: {e}")

def analyze(content):
    prompt = f"""당신은 한국 공공주택 청약 전문가입니다.

신청자 프로필: {MY_PROFILE}

공고 내용 또는 URL: {content}

아래 형식으로 분석해주세요:

🏠 <b>[공고명]</b>

판정: ✅ 신청 가능 / ❌ 신청 불가 / ⚠️ 조건 확인 필요
(이유 한 줄)

📋 <b>자격 조건 체크</b>
• 나이: ✅/❌ (조건)
• 무주택: ✅/❌ (조건)
• 소득: ✅/⚠️/❌ (조건)
• 거주지역: ✅/❌ (조건)

📅 <b>주요 일정</b>
• 접수:
• 당첨발표:

📎 <b>필요 서류</b>
(핵심 서류 4~5개)

🔗 <b>접수처</b>

💡 <b>꼭 확인할 것</b>"""
    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"❌ 분석 오류: {e}"

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"timeout": 30, "offset": offset}, timeout=35)
        return r.json()
    except Exception as e:
        logger.error(f"업데이트 오류: {e}")
        return {"result": []}

def main():
    logger.info("Yehome 봇 시작!")
    send("🏠 <b>Yehome 봇이 켜졌어요!</b>\n\n공고 링크나 내용을 보내주시면 신청 가능 여부를 분석해드릴게요 😊")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                if "message" not in update:
                    continue
                msg = update["message"]
                cid = str(msg["chat"]["id"])
                text = msg.get("text", "").strip()
                if not text:
                    continue
                if text == "/start":
                    send("🏠 <b>Yehome에 오신 걸 환영해요!</b>\n\n공고 URL 또는 텍스트를 붙여넣으시면 바로 분석해드려요!\n\n/profile — 내 프로필 확인", cid)
                elif text == "/profile":
                    lines = "\n".join(f"• {k}: {v}" for k, v in MY_PROFILE.items())
                    send(f"👤 <b>내 프로필</b>\n\n{lines}", cid)
                else:
                    send("⏳ 분석 중...", cid)
                    result = analyze(text)
                    send(result, cid)
        except Exception as e:
            logger.error(f"오류: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
