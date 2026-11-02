"""Lab 2 - Bangun indeks & cari (25 menit).

1. Letakkan 3 PDF di folder dokumen/, jalankan indeks, pastikan tiap file melaporkan jumlah chunk.
2. Ajukan 5 pertanyaan dengan query(); periksa apakah chunk teratas benar-benar relevan.
3. Ajukan 2 pertanyaan berparafrase; apakah pencarian semantik tetap menemukannya?

Dokumen yang dipakai (3 PDF tentang kecerdasan buatan, semuanya di folder dokumen/):
  - 1_Pengantar_Kecerdasan_Buatan.pdf
  - 2_Machine_Learning_dan_Deep_Learning.pdf
  - 3_Etika_dan_Masa_Depan_AI.pdf
"""
import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laporan_utils import Laporan
from rag_utils import bangun_indeks, cocok, query

BASE = os.path.dirname(os.path.abspath(__file__))
UKURAN, OVERLAP = 1000, 0.15
FILE_DIHARAPKAN = [
    "1_Pengantar_Kecerdasan_Buatan.pdf",
    "2_Machine_Learning_dan_Deep_Learning.pdf",
    "3_Etika_dan_Masa_Depan_AI.pdf",
]

# kw = kata kunci yang HARUS ada di chunk teratas agar dianggap relevan
# "sumber" = PDF yang memuat jawabannya (hanya untuk catatan di laporan)
PERTANYAAN = [
    {"q": "Siapa yang memperkenalkan istilah Artificial Intelligence dan pada tahun berapa?",
     "kw": ["McCarthy", "1956"], "sumber": "PDF 1"},
    {"q": "Komputer apa yang mengalahkan juara catur dunia Garry Kasparov?",
     "kw": ["Deep Blue", "Kasparov"], "sumber": "PDF 1"},
    {"q": "Apa perbedaan supervised learning dan unsupervised learning?",
     "kw": ["Supervised Learning", "Unsupervised Learning"], "sumber": "PDF 2"},
    {"q": "Apa yang dimaksud dengan overfitting?",
     "kw": ["overfitting", "menghafal"], "sumber": "PDF 2"},
    {"q": "Arsitektur apa yang mendasari model bahasa besar modern?",
     "kw": ["Transformer", "mendasari"], "sumber": "PDF 2"},
]
PARAFRASE = [
    {"q": "Bagaimana komputer bisa belajar dari contoh tanpa diberi aturan langkah demi langkah?",
     "kw": ["tanpa diprogram"], "sumber": "PDF 1",
     "catatan": "Teks memakai 'tanpa diprogram secara eksplisit'; pertanyaan memakai 'tanpa diberi aturan langkah demi langkah'."},
    {"q": "Mengapa program komputer bisa memperlakukan kelompok orang tertentu secara berbeda?",
     "kw": ["diskriminasi", "mewarisi"], "sumber": "PDF 3",
     "catatan": "Teks memakai 'bias', 'diskriminasi', dan 'mewarisi'; pertanyaan memakai 'memperlakukan kelompok tertentu secara berbeda'."},
]


def ringkas(t, n=150):
    t = " ".join(t.split())
    return t if len(t) <= n else t[:n] + "..."


def jalankan(indeks, daftar, k=3):
    hasil = []
    for s in daftar:
        atas = query(indeks, s["q"], k)
        rel = [cocok(a["teks"], s["kw"]) for a in atas]
        hasil.append((s, atas, rel))
    return hasil


def main():
    # ---- Langkah 1
    print("=== Langkah 1: membangun indeks ===")
    buf = io.StringIO()
    with redirect_stdout(buf):
        idx = bangun_indeks(ukuran=UKURAN, overlap=OVERLAP, backend="auto")
    log_indeks = buf.getvalue()
    print(log_indeks)
    idx_leksikal = bangun_indeks(ukuran=UKURAN, overlap=OVERLAP, backend="tfidf", verbose=False)
    per_file = {}
    for m in idx.meta:
        per_file[m["file"]] = per_file.get(m["file"], 0) + 1
    hilang = [f for f in FILE_DIHARAPKAN if f not in per_file]
    if hilang:
        print("PERINGATAN: file belum terindeks (cek folder dokumen/):", ", ".join(hilang))
    total = len(idx.chunks)

    # ---- Langkah 2
    print("=== Langkah 2: 5 pertanyaan ===")
    h2 = jalankan(idx, PERTANYAAN)
    for s, atas, rel in h2:
        print(f"\nQ: {s['q']}  (kata kunci: {s['kw']}; jawaban di {s['sumber']})")
        for r, (a, ok) in enumerate(zip(atas, rel), 1):
            print(f"  #{r} skor={a['skor']:.3f} {a['file']}#{a['no']} relevan={ok} | {ringkas(a['teks'])}")
    n_top1 = sum(rel[0] for _, _, rel in h2)
    n_top3 = sum(any(rel) for _, _, rel in h2)

    # ---- Langkah 3
    print("\n=== Langkah 3: parafrase ===")
    sem = jalankan(idx, PARAFRASE)
    lek = jalankan(idx_leksikal, PARAFRASE)
    for (s, a1, r1), (_, a2, r2) in zip(sem, lek):
        print(f"\nQ: {s['q']}")
        print(f"  {idx.backend}: top1 relevan={r1[0]} top3 relevan={any(r1)} | {a1[0]['file']}#{a1[0]['no']}")
        print(f"  tfidf : top1 relevan={r2[0]} top3 relevan={any(r2)} | {a2[0]['file']}#{a2[0]['no']}")

    # ---- Kesimpulan dari angka
    sem_top3 = sum(any(r) for _, _, r in sem)
    lek_top3 = sum(any(r) for _, _, r in lek)
    sem_top1 = sum(r[0] for _, _, r in sem)
    lek_top1 = sum(r[0] for _, _, r in lek)
    kes = (f"Pada 5 pertanyaan langsung, chunk peringkat 1 relevan pada {n_top1}/5 pertanyaan dan salah satu dari "
           f"3 chunk teratas relevan pada {n_top3}/5 pertanyaan. Pada 2 pertanyaan parafrase, backend "
           f"'{idx.backend}' menemukan chunk relevan di peringkat 1 pada {sem_top1}/2 dan di 3 teratas pada "
           f"{sem_top3}/2, sedangkan pembanding TF-IDF (kecocokan bentuk kata) {lek_top1}/2 dan {lek_top3}/2. ")
    gagal_top1 = [s["q"] for s, atas, rel in h2 if not rel[0]]
    if gagal_top1:
        kes += ("Pertanyaan yang chunk peringkat 1-nya belum relevan: " + "; ".join(f'"{q}"' for q in gagal_top1) +
                ". Penyebab yang mungkin: kalimat jawaban terbelah di batas chunk sehingga kata kuncinya "
                "terpisah, sementara chunk di sebelahnya memuat topik yang mirip. ")
    if sem_top1 == lek_top1 and sem_top3 == lek_top3:
        kes += ("Pada dua parafrase ini, semantik dan TF-IDF memberi hasil yang sama, jadi tes ini belum bisa "
                "membedakan keduanya; kemungkinan karena pertanyaan masih berbagi beberapa kata dengan teks "
                "dan TF-IDF n-gram karakter menangkap variasi bentuk kata. ")
    kes += (f"Perlu diingat korpusnya sangat kecil: hanya {total} chunk dari {len(per_file)} PDF, sehingga 3 chunk "
            f"teratas sudah mencakup sekitar {min(3, total) / total:.0%} seluruh korpus dan angka top-3 mudah "
            "tinggi. Peringkat 1 lebih menjanjikan sebagai ukuran mutu. ")
    if idx.backend == "lsa":
        kes += ("Catatan: backend LSA hanya semantik ringan (hubungan antar kata dipelajari dari korpus yang kecil), "
                "sehingga parafrase yang benar-benar tidak berbagi kata akan sulit. Untuk hasil lebih kuat, pasang "
                "sentence-transformers; kode ini otomatis memakainya.")
    print("\nKesimpulan:", kes)

    # ---- Laporan PDF
    L = Laporan(os.path.join(BASE, "Lab2_Indeks_dan_Pencarian.pdf"), "Lab 2 - Bangun Indeks & Cari",
                f"ukuran chunk {UKURAN}, overlap {int(OVERLAP * 100)}%, backend: {idx.backend}")
    L.h1("Langkah 1. Membangun indeks")
    L.p("Tiga PDF diletakkan di folder dokumen/. Setiap file melaporkan jumlah chunk-nya:")
    L.tabel([["File", "Jumlah chunk"]] + [[f, n] for f, n in per_file.items()] + [["Total", total]],
            [9 * 28.35, 4 * 28.35])
    L.kode(log_indeks.rstrip())
    if hilang:
        L.p("PERINGATAN: file berikut belum terindeks: " + ", ".join(hilang))
    L.h1("Langkah 2. Lima pertanyaan dan pemeriksaan chunk teratas")
    L.p("Sebuah chunk dianggap relevan bila memuat semua kata kunci jawaban. Tabel menunjukkan 3 chunk teratas.")
    for s, atas, rel in h2:
        L.h2(f"{s['q']} (jawaban di {s['sumber']})")
        L.tabel([["Peringkat", "Skor", "Sumber", "Relevan?", "Cuplikan"]] +
                [[r, f"{a['skor']:.3f}", f"{a['file']} #{a['no']}", "ya" if ok else "tidak", ringkas(a["teks"], 140)]
                 for r, (a, ok) in enumerate(zip(atas, rel), 1)],
                [1.6 * 28.35, 1.3 * 28.35, 3.8 * 28.35, 1.6 * 28.35, 8.7 * 28.35])
    L.p(f"Ringkasan: chunk peringkat 1 relevan pada {n_top1}/5 pertanyaan; ada chunk relevan di 3 teratas pada {n_top3}/5.")
    L.h1("Langkah 3. Pertanyaan berparafrase")
    L.p("Dua pertanyaan memakai kata yang berbeda dari teks dokumen. Dibandingkan: pencarian semantik "
        f"({idx.backend}) vs TF-IDF.")
    baris = [["Pertanyaan", "Catatan", f"{idx.backend}: top1 / top3", "TF-IDF: top1 / top3"]]
    for (s, a1, r1), (_, a2, r2) in zip(sem, lek):
        baris.append([s["q"], s["catatan"], f"{'ya' if r1[0] else 'tidak'} / {'ya' if any(r1) else 'tidak'}",
                      f"{'ya' if r2[0] else 'tidak'} / {'ya' if any(r2) else 'tidak'}"])
    L.tabel(baris, [5 * 28.35, 6 * 28.35, 3 * 28.35, 3 * 28.35])
    for (s, a1, r1), _ in zip(sem, lek):
        L.p(f"Chunk teratas untuk \"{s['q']}\": {a1[0]['file']} #{a1[0]['no']} (skor {a1[0]['skor']:.3f})")
        L.kode(ringkas(a1[0]["teks"], 400))
    L.h1("Kesimpulan")
    L.p(kes)
    L.halaman_baru()
    L.h1("Lampiran: kode lab2_indeks_cari.py")
    L.kode(open(__file__, encoding="utf-8").read())
    L.simpan()
    print("\nLaporan: Lab2_Indeks_dan_Pencarian.pdf")


if __name__ == "__main__":
    main()