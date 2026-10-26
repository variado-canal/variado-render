import sys, json, asyncio
import edge_tts

async def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        job = json.load(f)
    text = job["narracion"]
    voice = job.get("voz_edge","es-MX-JorgeNeural")
    rate = job.get("rate","+18%")
    comm = edge_tts.Communicate(text=text,voice=voice,rate=rate)
    await comm.save(sys.argv[2])
if __name__ == "__main__":
    asyncio.run(main())
