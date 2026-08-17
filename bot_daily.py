"""
bot_daily.py — Mensaje diario con top 10 matches

Se ejecuta después del pipeline diario.
Lee top_matches.csv y manda mensaje a Telegram pidiendo respuesta.
"""

import os
import pandas as pd
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

MATCHES_FILE = Path("data/top_matches_full.csv")


def send_message(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    r = requests.post(url, json=payload)
    return r.json()


def main():
    df = pd.read_csv(MATCHES_FILE, encoding="utf-8")
    
    header = (
        f"🎯 <b>Top 10 Matches del día</b>\n"
        f"📅 {pd.Timestamp.now().strftime('%d/%m/%Y')}\n\n"
        f"Estos son los puestos que mejor matchean con tu perfil:\n\n"
    )
    
    body = ""
    for i, row in df.iterrows():
        title    = str(row.get("title", ""))[:55]
        company  = str(row.get("company", ""))[:30]
        city     = str(row.get("city", ""))
        modality = str(row.get("modality", ""))
        score    = row.get("score", 0)
        stack    = str(row.get("ai_stack", ""))[:50]
        
        emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        
        body += (
            f"{emoji} <b>[{i}]</b> <b>{title}</b>\n"
            f"      🏢 {company}\n"
            f"      📍 {city} · {modality}\n"
            f"      🛠️ {stack}\n"
            f"      ⭐ Score: {score}/100\n\n"
        )
    
    footer = (
        "✏️ <b>Respondé con los números que querés adaptar.</b>\n"
        "Ejemplo: <code>4,7,8</code>\n"
        "(separados por coma, sin espacios)"
    )
    
    text = header + body + footer
    
    result = send_message(text)
    
    if result.get("ok"):
        print(f"✓ Mensaje enviado. Message ID: {result['result']['message_id']}")
    else:
        print(f"✗ Error: {result}")


if __name__ == "__main__":
    main()