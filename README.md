![Neofetch Card](./output_card.svg)

# GitHub Profile Card

Animasyonlu ASCII balık içeren, neofetch tarzı GitHub profil kartı.
`output_card.svg` README tarafından otomatik gösterilir.

## Yapı

```
generate_card.py      # Kartı üretir (template + veriler -> output_card.svg)
templates/
  card_template.svg   # SVG şablon (placeholder'lar: {full_name}, {title}, ...)
fish_frames.json      # ASCII balık animasyon frame'leri (bir kez indirildi)
scripts/
  fetch_fish_cache.py # Balık frame'lerini ascii-motion.app'ten çeker
output_card.svg       # Üretilen kart (README embed eder)
```

## Kullanım

```bash
# Statik değerlerle üret (token gerekmez)
python3 generate_card.py

# Gerçek GitHub istatistikleriyle üret
export GH_TOKEN="ghp_..."
python3 generate_card.py
```

`GH_TOKEN` ortam değişkeni varsa GitHub GraphQL API'den repo/stars/commits/followers
çekilir, yoksa `STATIC` fallback değerleri kullanılır.

## Balık animasyonunu güncellemek

Frame'ler `fish_frames.json` içinde cache'lenir. Yeniden indirmek için:

```bash
python3 scripts/fetch_fish_cache.py
```
