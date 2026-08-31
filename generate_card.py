import os
import json
import gzip
import base64
import urllib.request
import urllib.error

GITHUB_TOKEN = os.getenv("GH_TOKEN")
USERNAME = os.getenv("GH_USERNAME") or "emre-tiryaki"

# --- Statik fallback değerler (vault ~/Documents/hermes + portfolyo all.json'dan) ---
STATIC = {
    "repos": "24",
    "stars": "1",
    "contributed": "18",
    "followers": "64",
    "commits": "577",
    "top_language": "Go",
}

# ASCII Motion "Fish Loop" projesi - tum frame'ler, SMIL ile animasyon
# canvas 60x30, 19 frame, frame basina 100ms (~1.9s loop)
FISH_FRAME_DUR = 0.1  # saniye (100ms)


def fetch_fish_animation():
    """fish_frames.json dosyasindan (bir kez indirildi) TUM frame'leri okur
    ve SMIL <animate> ile oynayan ASCII balik uretir.
    Dosya yoksa statik yer tutucu doner."""
    cache_path = os.path.join(os.path.dirname(__file__), "fish_frames.json")
    try:
        if not os.path.exists(cache_path):
            print(f"[warn] {cache_path} bulunamadi, yer tutucu kullaniliyor.")
            return '<text class="fish" x="25" y="163" fill="#c2f261">  &lt;fish loop&gt;</text>'
        with open(cache_path, encoding="utf-8") as fp:
            obj = json.load(fp)
        frames = obj["frames"]
        W = obj["canvas"]["width"]
        H = obj["canvas"]["height"]

        n = len(frames)
        dur_s = FISH_FRAME_DUR
        total = n * dur_s  # toplam dongu suresi (sn)

        groups = []
        for fi, frame in enumerate(frames):
            rows = []
            for y in range(H):
                spans = []
                for x in range(W):
                    cell = frame.get(f"{x},{y}")
                    if not cell or cell.get("char") in (None, " ", ""):
                        spans.append("<tspan> </tspan>")
                    else:
                        color = cell.get("color", "#c2f261")
                        ch = (cell["char"].replace("&", "&amp;")
                              .replace("<", "&lt;").replace(">", "&gt;"))
                        spans.append(f'<tspan fill="{color}">{ch}</tspan>')
                rows.append(f'<tspan x="520" y="{35 + y*15}">{"".join(spans)}</tspan>')
            frame_text = "".join(rows)

            t0 = fi * dur_s / total
            t1 = (fi + 1) * dur_s / total
            kt = f"0;{t0:.4f};{t1:.4f};1"
            dv = "none;inline;none;none"
            anim = (
                f'<animate attributeName="display" '
                f'values="{dv}" keyTimes="{kt}" '
                f'dur="{total:.2f}s" repeatCount="indefinite" '
                f'begin="0s"/>'
            )
            groups.append(f'<text class="fish" display="none">{frame_text}{anim}</text>')

        return "\n".join(groups)
    except Exception as e:
        print(f"[warn] Fish animasyonu okunamadi ({e}), yer tutucu kullaniliyor.")
        return '<text class="fish" x="25" y="163" fill="#c2f261">  &lt;fish loop&gt;</text>'


def fetch_github_stats():
    """GitHub GraphQL ile profil istatistiklerini çeker.
    Token yoksa veya istek başarısızsa STATIC fallback döner."""
    if not GITHUB_TOKEN:
        print("[info] GH_TOKEN bulunamadi, statik degerler kullaniliyor.")
        return dict(STATIC)

    query = """
    query($username: String!) {
      user(login: $username) {
        repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR]) {
          totalCount
          nodes { stargazerCount }
        }
        repositoriesContributedTo(first: 100) {
          totalCount
        }
        followers { totalCount }
        contributionsCollection {
          totalCommitContributions
        }
      }
    }
    """
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    body = json.dumps({"query": query, "variables": {"username": USERNAME}}).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"[warn] GitHub API hatasi ({e}), statik degerler kullaniliyor.")
        return dict(STATIC)

    user = payload.get("data", {}).get("user")
    if not user:
        print("[warn] GitHub API veri dondurmedi, statik degerler kullaniliyor.")
        return dict(STATIC)

    total_repos = user["repositories"]["totalCount"]
    total_stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])
    contributed = user["repositoriesContributedTo"]["totalCount"]
    total_followers = user["followers"]["totalCount"]
    total_commits = user["contributionsCollection"]["totalCommitContributions"]

    return {
        "repos": str(total_repos),
        "stars": str(total_stars),
        "contributed": str(contributed),
        "followers": str(total_followers),
        "commits": f"{total_commits:,}",
        "top_language": STATIC["top_language"],
    }


def main():
    stats = fetch_github_stats()
    fish_frame = fetch_fish_animation()

    stats.update({
        "full_name": "Emre Tiryaki",
        "title": "Backend Developer",
        "fish_frame": fish_frame,

        # Sağ sütun
        "os_info": "Arch Linux x86_64",
        "host_info": "Lenovo LOQ 15IRX10",
        "kernel_info": "Linux 7.1.4-arch1-1",
        "ide_info": "VSCode",

        "languages_prog": "Go, TypeScript",

        "flagship": "ClearSky — real-time flight tracking (Go + TS microservices)",
    })

    # Nokta doldurma: etiket uzunluguna gore boslugu '.' ile doldur
    # Sag sutun 525-965 = 440px, 13px monospace ~7.8px/karakter -> ~56 kolon
    def make_dots(label, value, total_cols=56):
        avail = total_cols - len(label) - 2 - len(value)
        if avail < 1:
            return " "
        return "." * avail

    stats["os_dots"] = make_dots("OS", stats["os_info"])
    stats["host_dots"] = make_dots("Host", stats["host_info"])
    stats["kernel_dots"] = make_dots("Kernel", stats["kernel_info"])
    stats["ide_dots"] = make_dots("IDE", stats["ide_info"])
    stats["prog_dots"] = make_dots("Programming", stats["languages_prog"])

    # Template'i oku ve placeholder'lari doldur
    with open("templates/card_template.svg", "r", encoding="utf-8") as f:
        template = f.read()

    # XML'de özel anlami olan karakterleri escape et
    def xml_escape(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    output_svg = template
    for key, value in stats.items():
        if key == "fish_frame":
            # Fish frame zaten güvenli SVG (<tspan>) içerir, escape ETME
            output_svg = output_svg.replace(f"{{{key}}}", str(value))
        else:
            output_svg = output_svg.replace(f"{{{key}}}", xml_escape(value))

    with open("output_card.svg", "w", encoding="utf-8") as f:
        f.write(output_svg)

    print("[ok] output_card.svg uretildi.")


if __name__ == "__main__":
    main()
