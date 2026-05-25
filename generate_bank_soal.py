"""
generate_bank_soal.py
=====================
Auto-generator Bank Soal Psiko Kecermatan
Super Admin jalankan script ini untuk generate paket baru.

Usage:
  python generate_bank_soal.py --paket 7 --output bank_soal_p7.json
  python generate_bank_soal.py --paket 7 --push-supabase
"""

import random
import json
import argparse
import os
import sys
from itertools import permutations

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ══════════════════════════════════════
# DEFINISI SIMBOL — tambah set baru di sini
# Super admin bisa ubah/tambah set simbol
# ══════════════════════════════════════
SYMBOL_SETS = {
    # Paket 3 (sudah ada)
    "P3_K1":  {"A":"♈","B":"♉","C":"♊","D":"♋","E":"♌"},
    "P3_K2":  {"A":"📊","B":"📈","C":"📉","D":"📅","E":"📋"},
    "P3_K3":  {"A":"🥇","B":"🥈","C":"🥉","D":"🏅","E":"🎖️"},
    "P3_K4":  {"A":"☀️","B":"🌤️","C":"⛅","D":"🌥️","E":"☁️"},
    "P3_K5":  {"A":"🕒","B":"🕕","C":"🕘","D":"🕛","E":"🕜"},
    # Paket 4 (sudah ada)
    "P4_K1":  {"A":"🐶","B":"🐱","C":"🐭","D":"🦊","E":"🐻"},
    "P4_K2":  {"A":"📉","B":"📈","C":"📊","D":"💹","E":"🧾"},
    "P4_K3":  {"A":"╠","B":"╣","C":"╦","D":"╩","E":"╬"},
    "P4_K4":  {"A":"⇇","B":"⇈","C":"⇉","D":"⇊","E":"⇄"},
    "P4_K5":  {"A":"📁","B":"📂","C":"🗂️","D":"🗃️","E":"🗄️"},
    # Set baru — untuk paket 7, 8, dst
    "SET_GEO":  {"A":"▲","B":"▼","C":"◆","D":"●","E":"■"},
    "SET_ARW":  {"A":"↑","B":"↓","C":"←","D":"→","E":"↔"},
    "SET_MATH": {"A":"∑","B":"∏","C":"∫","D":"∂","E":"∞"},
    "SET_CARD": {"A":"♠","B":"♥","C":"♦","D":"♣","E":"★"},
    "SET_MOON": {"A":"🌑","B":"🌓","C":"🌕","D":"🌗","E":"🌙"},
    "SET_DICE": {"A":"⚀","B":"⚁","C":"⚂","D":"⚃","E":"⚄"},
    "SET_PLANT":{"A":"🌱","B":"🌿","C":"🍀","D":"🌺","E":"🍁"},
    "SET_FLAG": {"A":"🚩","B":"🏴","C":"🏳️","D":"🎌","E":"🏁"},
    "SET_HAND": {"A":"✊","B":"✋","C":"👌","D":"👍","E":"👎"},
    "SET_WEAT": {"A":"⛈️","B":"🌪️","C":"🌈","D":"❄️","E":"🌊"},
}

# Template paket — definisi 10 kolom per paket
PAKET_TEMPLATES = {
    3: [
        {"nama":"Kolom I",   "roman":"I",   "set":"P3_K1"},
        {"nama":"Kolom II",  "roman":"II",  "set":"P3_K2"},
        {"nama":"Kolom III", "roman":"III", "set":"P3_K3"},
        {"nama":"Kolom IV",  "roman":"IV",  "set":"P3_K4"},
        {"nama":"Kolom V",   "roman":"V",   "set":"P3_K5"},
        {"nama":"Kolom VI",  "roman":"VI",  "set":"SET_GEO"},
        {"nama":"Kolom VII", "roman":"VII", "set":"SET_ARW"},
        {"nama":"Kolom VIII","roman":"VIII","set":"SET_MATH"},
        {"nama":"Kolom IX",  "roman":"IX",  "set":"SET_CARD"},
        {"nama":"Kolom X",   "roman":"X",   "set":"SET_MOON"},
    ],
    4: [
        {"nama":"Kolom I",   "roman":"I",   "set":"P4_K1"},
        {"nama":"Kolom II",  "roman":"II",  "set":"P4_K2"},
        {"nama":"Kolom III", "roman":"III", "set":"P4_K3"},
        {"nama":"Kolom IV",  "roman":"IV",  "set":"P4_K4"},
        {"nama":"Kolom V",   "roman":"V",   "set":"P4_K5"},
        {"nama":"Kolom VI",  "roman":"VI",  "set":"SET_DICE"},
        {"nama":"Kolom VII", "roman":"VII", "set":"SET_PLANT"},
        {"nama":"Kolom VIII","roman":"VIII","set":"SET_FLAG"},
        {"nama":"Kolom IX",  "roman":"IX",  "set":"SET_HAND"},
        {"nama":"Kolom X",   "roman":"X",   "set":"SET_WEAT"},
    ],
    7: [
        {"nama":"Kolom I",   "roman":"I",   "set":"SET_GEO"},
        {"nama":"Kolom II",  "roman":"II",  "set":"SET_ARW"},
        {"nama":"Kolom III", "roman":"III", "set":"SET_MATH"},
        {"nama":"Kolom IV",  "roman":"IV",  "set":"SET_CARD"},
        {"nama":"Kolom V",   "roman":"V",   "set":"SET_MOON"},
        {"nama":"Kolom VI",  "roman":"VI",  "set":"SET_DICE"},
        {"nama":"Kolom VII", "roman":"VII", "set":"SET_PLANT"},
        {"nama":"Kolom VIII","roman":"VIII","set":"SET_FLAG"},
        {"nama":"Kolom IX",  "roman":"IX",  "set":"SET_HAND"},
        {"nama":"Kolom X",   "roman":"X",   "set":"SET_WEAT"},
    ],
}


# ══════════════════════════════════════
# CORE LOGIC — generate soal
# Jawaban = simbol yang TIDAK muncul dari 5
# ══════════════════════════════════════
def generate_soal(symbols: dict, jumlah: int = 50, seed: int = None) -> list:
    """Generate soal untuk satu kolom."""
    if seed is not None:
        random.seed(seed)

    keys = list(symbols.keys())   # ['A','B','C','D','E']
    vals = list(symbols.values()) # ['♈','♉','♊','♋','♌']
    soal_list = []

    # Pastikan distribusi jawaban merata (tidak bias ke satu huruf)
    # Setiap 5 soal, semua jawaban A-E muncul minimal sekali
    answers_pool = (keys * (jumlah // 5 + 1))[:jumlah]
    random.shuffle(answers_pool)

    for i, kunci in enumerate(answers_pool):
        # shown = 4 simbol selain kunci, acak urutannya
        shown_keys = [k for k in keys if k != kunci]
        random.shuffle(shown_keys)
        shown_symbols = [symbols[k] for k in shown_keys]
        soal_list.append({
            "nomor": i + 1,
            "shown": shown_symbols,
            "kunci": kunci
        })

    return soal_list


def generate_paket(nomor_paket: int, jumlah_soal_per_kolom: int = 50) -> dict:
    """Generate satu paket lengkap (10 kolom × 50 soal = 500 soal)."""
    if nomor_paket not in PAKET_TEMPLATES:
        raise ValueError(
            f"Paket {nomor_paket} belum ada template-nya. "
            f"Tambahkan di PAKET_TEMPLATES dulu."
        )

    template = PAKET_TEMPLATES[nomor_paket]
    kolom_list = []

    for idx, kolom_def in enumerate(template):
        symbols = SYMBOL_SETS[kolom_def["set"]]
        # seed berbeda per kolom agar tidak identik antar kolom
        seed = nomor_paket * 1000 + idx
        soal = generate_soal(symbols, jumlah_soal_per_kolom, seed=seed)
        kolom_list.append({
            "nomor": idx + 1,
            "nama": kolom_def["nama"],
            "roman": kolom_def["roman"],
            "simbol": symbols,
            "soal": soal
        })

    return {
        "nomor": nomor_paket,
        "nama": f"Paket {nomor_paket}",
        "total_soal": len(template) * jumlah_soal_per_kolom,
        "kolom": kolom_list
    }


def validate_paket(paket: dict) -> bool:
    """Validasi: setiap soal, jawaban harus = simbol yang hilang."""
    errors = []
    for kolom in paket["kolom"]:
        symbols = kolom["simbol"]
        sym_vals = set(symbols.values())
        for soal in kolom["soal"]:
            shown_set = set(soal["shown"])
            missing_sym = sym_vals - shown_set
            if len(missing_sym) != 1:
                errors.append(
                    f"Kolom {kolom['nama']} soal #{soal['nomor']}: "
                    f"shown={soal['shown']} tidak valid"
                )
                continue
            expected_key = [k for k, v in symbols.items()
                            if v in missing_sym][0]
            if soal["kunci"] != expected_key:
                errors.append(
                    f"Kolom {kolom['nama']} soal #{soal['nomor']}: "
                    f"kunci={soal['kunci']} tapi seharusnya={expected_key}"
                )

    if errors:
        print(f"❌ VALIDASI GAGAL ({len(errors)} error):")
        for e in errors[:10]:
            print(f"   {e}")
        return False

    total = sum(len(k["soal"]) for k in paket["kolom"])
    print(f"✅ Validasi OK — {len(paket['kolom'])} kolom, {total} soal, semua jawaban benar")
    return True


def export_js(paket: dict, output_path: str):
    """Export ke format JS yang langsung bisa dipakai V3 frontend."""
    lines = [f"// Bank Soal Paket {paket['nomor']} — AUTO-GENERATED"]
    lines.append(f"// Total: {paket['total_soal']} soal")
    lines.append(f"const KOLOM_DATA_P{paket['nomor']} = ")
    kolom_js = []
    for k in paket["kolom"]:
        sym_str = json.dumps(k["simbol"], ensure_ascii=False)
        q_str = json.dumps(
            [{"shown": s["shown"], "key": s["kunci"]} for s in k["soal"]],
            ensure_ascii=False
        )
        kolom_js.append(
            f'  {{\n'
            f'    name:"{k["nama"]}",roman:"{k["roman"]}",\n'
            f'    symbols:{sym_str},\n'
            f'    questions:{q_str}\n'
            f'  }}'
        )
    lines.append("[\n" + ",\n".join(kolom_js) + "\n];")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📄 JS exported → {output_path}")


def push_to_supabase(paket: dict, supabase_url: str, supabase_key: str):
    """Push paket ke Supabase via REST API."""
    try:
        import urllib.request
        import urllib.parse

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        # 1. Insert paket
        paket_data = json.dumps({
            "nomor": paket["nomor"],
            "nama": paket["nama"],
            "aktif": False
        }).encode()

        req = urllib.request.Request(
            f"{supabase_url}/rest/v1/paket",
            data=paket_data, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req) as r:
            paket_row = json.loads(r.read())[0]
        paket_id = paket_row["id"]
        print(f"✅ Paket inserted: {paket_id}")

        # 2. Insert kolom & soal
        for kolom in paket["kolom"]:
            kolom_data = json.dumps({
                "paket_id": paket_id,
                "nomor": kolom["nomor"],
                "nama": kolom["nama"],
                "roman": kolom["roman"],
                "simbol": kolom["simbol"]
            }).encode()
            req = urllib.request.Request(
                f"{supabase_url}/rest/v1/kolom",
                data=kolom_data, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req) as r:
                kolom_row = json.loads(r.read())[0]
            kolom_id = kolom_row["id"]

            # Batch insert soal (max 50 per request)
            soal_batch = [
                {
                    "kolom_id": kolom_id,
                    "nomor": s["nomor"],
                    "shown": s["shown"],
                    "kunci": s["kunci"]
                }
                for s in kolom["soal"]
            ]
            req = urllib.request.Request(
                f"{supabase_url}/rest/v1/soal",
                data=json.dumps(soal_batch).encode(),
                headers=headers, method="POST"
            )
            urllib.request.urlopen(req).close()
            print(f"  ↳ {kolom['nama']}: {len(soal_batch)} soal inserted")

        print(f"\n🎉 Paket {paket['nomor']} berhasil di-push ke Supabase!")
        print(f"   Aktifkan di Admin Panel → Toggle 'Aktif'")

    except Exception as e:
        print(f"❌ Push gagal: {e}")
        print("   Pastikan SUPABASE_URL dan SUPABASE_KEY sudah di-set.")


# ══════════════════════════════════════
# CLI ENTRY POINT
# ══════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generator Bank Soal Psiko Kecermatan"
    )
    parser.add_argument("--paket", type=int, required=True,
                        help="Nomor paket (3, 4, 7, dst)")
    parser.add_argument("--soal", type=int, default=50,
                        help="Jumlah soal per kolom (default: 50)")
    parser.add_argument("--output", type=str, default=None,
                        help="Path output JSON (default: bank_soal_pN.json)")
    parser.add_argument("--export-js", action="store_true",
                        help="Export juga sebagai .js untuk V3 frontend")
    parser.add_argument("--push-supabase", action="store_true",
                        help="Push langsung ke Supabase database")
    parser.add_argument("--validate-only", action="store_true",
                        help="Hanya validasi tanpa menyimpan")

    args = parser.parse_args()

    print(f"\n🔄 Generating Paket {args.paket} ({args.soal} soal/kolom)...")
    paket = generate_paket(args.paket, args.soal)

    # Validasi wajib
    ok = validate_paket(paket)
    if not ok:
        exit(1)

    if args.validate_only:
        exit(0)

    # Export JSON
    out_json = args.output or f"bank_soal_p{args.paket}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(paket, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON saved → {out_json}")

    # Export JS (opsional)
    if args.export_js:
        out_js = out_json.replace(".json", ".js")
        export_js(paket, out_js)

    # Push ke Supabase (opsional)
    if args.push_supabase:
        # Baca dari .env jika ada
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            print("❌ Set env vars dulu:")
            print("   set SUPABASE_URL=https://xxx.supabase.co")
            print("   set SUPABASE_KEY=your-anon-key")
        else:
            push_to_supabase(paket, url, key)

    print(f"\n📊 Summary Paket {args.paket}:")
    for k in paket["kolom"]:
        dist = {}
        for s in k["soal"]:
            dist[s["kunci"]] = dist.get(s["kunci"], 0) + 1
        dist_str = " ".join(f"{k}:{v}" for k, v in sorted(dist.items()))
        print(f"  {k['nama']:12} | {dist_str}")
