# -*- coding: utf-8 -*-
"""Generates audio/*.mp3 (Microsoft neural voices) and data.js from words.py."""
import asyncio, json, os, sys
import edge_tts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import CATEGORIES, MALAYALAM

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ROOT, "audio")
os.makedirs(AUDIO, exist_ok=True)
VOICE = {"hi": "hi-IN-SwaraNeural", "ml": "ml-IN-SobhanaNeural"}

items, jobs = [], []
def add(cat, lang, he, native, tr, en, idx):
    fname = f"{lang}_{idx:03d}.mp3"
    items.append({"cat": cat, "lang": lang, "he": he, "native": native, "tr": tr, "en": en, "audio": f"audio/{fname}"})
    jobs.append((native.replace("...", ",").strip(), VOICE[lang], os.path.join(AUDIO, fname)))

i = 0
cats = []
for key, emoji, name, words in CATEGORIES:
    cats.append({"key": key, "emoji": emoji, "name": name})
    for w in words:
        i += 1; add(key, "hi", *w, i)
cats.append({"key": "ml", "emoji": "🌴", "name": "בונוס: מלאיאלאם (קרלה)"})
for j, w in enumerate(MALAYALAM, 1):
    add("ml", "ml", *w, j)

async def gen(text, voice, path, sem):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, voice, rate="-15%").save(path); return
            except Exception as e:
                print("retry", path, e); await asyncio.sleep(2)

async def main():
    sem = asyncio.Semaphore(6)
    await asyncio.gather(*(gen(*j, sem) for j in jobs))

asyncio.run(main())
with open(os.path.join(ROOT, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.CATS=" + json.dumps(cats, ensure_ascii=False) + ";\n")
    f.write("window.WORDS=" + json.dumps(items, ensure_ascii=False) + ";\n")
hi = sum(1 for x in items if x["lang"] == "hi")
print(f"hindi={hi} malayalam={len(items)-hi} mp3={len(os.listdir(AUDIO))}")
