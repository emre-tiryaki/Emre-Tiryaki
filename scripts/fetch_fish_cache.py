import json, gzip, base64, urllib.request, os

SB = open('/tmp/realkey.txt').read().strip() if os.path.exists('/tmp/realkey.txt') else "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE2MTMxOTUxOTIsImV4cCI6MTkyODc3MTE5Mn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8wFUSw"
PID = "424d1127-7ab4-449a-ac73-a543524a4141"
url = f"https://tgfvqyubdujqtsfqyuun.supabase.co/rest/v1/projects?id=eq.{PID}&select=canvas_data"
req = urllib.request.Request(url, headers={"apikey":SB,"Authorization":f"Bearer {SB}"})
data = json.load(urllib.request.urlopen(req, timeout=20))
raw = data[0]["canvas_data"]["__data"]
txt = gzip.decompress(base64.b64decode(raw)).decode("utf-8","replace")
obj = json.loads(txt)

out = {
    "name": obj.get("name"),
    "canvas": {"width": obj["canvas"]["width"], "height": obj["canvas"]["height"]},
    "frames": [f["data"] for f in obj["animation"]["frames"]],
}
with open("fish_frames.json", "w", encoding="utf-8") as fp:
    json.dump(out, fp, ensure_ascii=False)
print("Kaydedildi:", os.path.abspath("fish_frames.json"))
print("Frame sayisi:", len(out["frames"]), "| canvas:", out["canvas"])
