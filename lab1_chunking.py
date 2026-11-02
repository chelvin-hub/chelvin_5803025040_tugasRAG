"""Lab 1 - Eksperimen chunking (15 menit).

1. Baca tiap PDF dengan baca_pdf() dan cetak 500 karakter pertama.
2. Potong dengan potong() memakai tiga ukuran (500, 1000, 1500) dan overlap 10-20%.
3. Lihat 3 chunk acak tiap ukuran: terpotong di tengah kalimat atau daftar poin?

Dokumen yang dipakai (3 PDF tentang kecerdasan buatan, taruh di FOLDER_DOKUMEN
atau di folder yang sama dengan file ini):
  - 1_Pengantar_Kecerdasan_Buatan.pdf
  - 2_Machine_Learning_dan_Deep_Learning.pdf
  - 3_Etika_dan_Masa_Depan_AI.pdf
Ketiganya tidak berisi tabel, tetapi penuh daftar poin (bullet, nomor, dan butir
bertahun seperti "1950: ..."). Karena itu yang diperiksa pada langkah 3 adalah
apakah chunk memotong sebuah butir daftar, bukan tabel.
"""
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laporan_utils import Laporan
from rag_utils import FOLDER_DOKUMEN, baca_pdf, potong, potong_dengan_posisi

BASE = os.path.dirname(os.path.abspath(__file__))
NAMA_PDF = [
    "1_Pengantar_Kecerdasan_Buatan.pdf",
    "2_Machine_Learning_dan_Deep_Learning.pdf",
    "3_Etika_dan_Masa_Depan_AI.pdf",
]
UKURAN = [500, 1000, 1500]
OVERLAP = [0.10, 0.15, 0.20]
OVERLAP_UTAMA = 0.15
SEED = 42

# Awal butir daftar: "• ...", "1. ...", "1950: ...", "1980-an: ...", "2012 hingga ..."
POLA_BUTIR = re.compile(r"^(•\s|\d+\.\s|\d{4}(-an)?\b)")
# Baris butir yang panjang dan tidak berakhir tanda baca dianggap berlanjut ke baris berikutnya
PANJANG_BARIS_LANJUT = 70


def cari_pdf(nama):
    """Cari file di FOLDER_DOKUMEN, lalu di folder skrip ini."""
    for folder in (FOLDER_DOKUMEN, BASE):
        path = os.path.join(folder, nama)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"{nama} tidak ditemukan di {FOLDER_DOKUMEN} maupun {BASE}")


def wilayah_daftar(teks):
    """Cari rentang karakter tiap butir daftar (baris butir + baris lanjutannya)."""
    baris, pos = [], 0
    for b in teks.split("\n"):
        baris.append((pos, pos + len(b), b))
        pos += len(b) + 1
    hasil, i = [], 0
    while i < len(baris):
        mulai, akhir, isi = baris[i]
        if POLA_BUTIR.match(isi):
            j = i
            while (j + 1 < len(baris)
                   and len(baris[j][2]) >= PANJANG_BARIS_LANJUT
                   and baris[j][2].rstrip()[-1:] not in ".!?"
                   and not POLA_BUTIR.match(baris[j + 1][2])):
                j += 1
            hasil.append((mulai, baris[j][1]))
            i = j + 1
        else:
            i += 1
    return hasil


def awal_di_tengah_kalimat(teks, mulai):
    """Chunk dimulai di tengah kalimat bila karakter bermakna sebelumnya bukan akhir kalimat/baris."""
    sebelum = teks[:mulai].rstrip(" ")
    return bool(sebelum) and sebelum[-1] not in ".!?:\n"


def akhir_di_tengah_kalimat(teks, akhir):
    ujung = teks[:akhir].rstrip()
    return bool(ujung) and ujung[-1] not in ".!?"


def memotong_daftar(wil, mulai, akhir):
    """True bila chunk beririsan dengan sebuah butir daftar tetapi tidak memuat butir itu seluruhnya."""
    for a, b in wil:
        beririsan = mulai < b and akhir > a
        utuh = mulai <= a and akhir >= b
        if beririsan and not utuh:
            return True
    return False


def persen(x, n):
    return f"{x}/{n} ({x / n:.0%})"


def analisis_pdf(nama, rnd):
    """Jalankan langkah 1-3 untuk satu PDF dan kembalikan semua hasilnya."""
    path = cari_pdf(nama)
    teks = baca_pdf(path)
    n_huruf = sum(c.isalpha() for c in teks)
    kualitas = {
        "File": nama,
        "Total karakter": len(teks),
        "Karakter rusak (U+FFFD)": teks.count("\ufffd"),
        "Sisa kode font '(cid:'": teks.count("(cid:"),
        "Jumlah butir daftar": len(wilayah_daftar(teks)),
        "Persentase huruf": f"{n_huruf / len(teks):.0%}",
    }
    print(f"\n########## {nama} ##########")
    print("=== Langkah 1: 500 karakter pertama ===")
    print(teks[:500])
    print(kualitas)

    print("\n=== Langkah 2: jumlah chunk ===")
    tabel_jumlah = [["Ukuran (karakter)"] + [f"overlap {int(o * 100)}%" for o in OVERLAP]]
    for u in UKURAN:
        baris = [u]
        for o in OVERLAP:
            n = len(potong(teks, u, o))
            baris.append(n)
            print(f"ukuran={u:5d} overlap={o:.0%} -> {n} chunk")
        tabel_jumlah.append(baris)

    wil = wilayah_daftar(teks)
    cuplikan = {}
    statistik = [["Ukuran", "Jumlah chunk", "Awal di tengah kalimat",
                  "Akhir di tengah kalimat", "Memotong butir daftar"]]
    mentah = {}  # ukuran -> (n, awal, akhir, daftar) untuk kesimpulan gabungan
    for u in UKURAN:
        pot = potong_dengan_posisi(teks, u, OVERLAP_UTAMA)
        n = len(pot)
        a = sum(awal_di_tengah_kalimat(teks, m) for m, _, _ in pot)
        z = sum(akhir_di_tengah_kalimat(teks, e) for _, e, _ in pot)
        t = sum(memotong_daftar(wil, m, e) for m, e, _ in pot)
        mentah[u] = (n, a, z, t)
        statistik.append([u, n, persen(a, n), persen(z, n), persen(t, n)])
        pilih = sorted(rnd.sample(range(n), min(3, n)))
        cuplikan[u] = [(i + 1, pot[i][0], pot[i][1], pot[i][2],
                        awal_di_tengah_kalimat(teks, pot[i][0]),
                        akhir_di_tengah_kalimat(teks, pot[i][1]),
                        memotong_daftar(wil, pot[i][0], pot[i][1])) for i in pilih]
        print(f"\n=== Langkah 3: ukuran {u} ({len(pilih)} chunk acak) ===")
        for no, m, e, isi, aw, ak, dp in cuplikan[u]:
            print(f"--- chunk #{no} [{m}:{e}] awal_tengah={aw} akhir_tengah={ak} potong_daftar={dp}")
            print(isi)

    return dict(nama=nama, teks=teks, kualitas=kualitas, tabel_jumlah=tabel_jumlah,
                statistik=statistik, cuplikan=cuplikan, mentah=mentah)


def catatan_kualitas(hasil):
    """Catatan kualitas teks yang dihitung dari angka, bukan ditulis tetap."""
    k = hasil["kualitas"]
    if k["Karakter rusak (U+FFFD)"] == 0 and k["Sisa kode font '(cid:'"] == 0:
        return (f"{hasil['nama']}: teks terbaca bersih, tidak ada karakter rusak maupun sisa kode font. "
                f"Terdeteksi {k['Jumlah butir daftar']} butir daftar.")
    return (f"{hasil['nama']}: PERHATIAN, ditemukan {k['Karakter rusak (U+FFFD)']} karakter rusak dan "
            f"{k['Sisa kode font ' + chr(39) + '(cid:' + chr(39)]} sisa kode font; periksa hasil ekstraksi.")


def buat_kesimpulan(semua):
    """Gabungkan statistik seluruh PDF per ukuran, lalu susun kesimpulan dari angkanya."""
    gabung = {}
    for u in UKURAN:
        n = sum(h["mentah"][u][0] for h in semua)
        a = sum(h["mentah"][u][1] for h in semua)
        z = sum(h["mentah"][u][2] for h in semua)
        t = sum(h["mentah"][u][3] for h in semua)
        gabung[u] = (n, a, z, t)
    rincian = "; ".join(
        f"ukuran {u}: {gabung[u][0]} chunk, awal di tengah kalimat {persen(gabung[u][1], gabung[u][0])}, "
        f"akhir di tengah kalimat {persen(gabung[u][2], gabung[u][0])}, "
        f"memotong butir daftar {persen(gabung[u][3], gabung[u][0])}"
        for u in UKURAN)
    n_kecil, n_besar = gabung[UKURAN[0]][0], gabung[UKURAN[-1]][0]
    pz_kecil = gabung[UKURAN[0]][2] / n_kecil
    pz_besar = gabung[UKURAN[-1]][2] / n_besar
    rata = sum(len(h["teks"]) for h in semua) // len(semua)
    arah = "turun" if pz_besar < pz_kecil - 0.05 else "naik" if pz_besar > pz_kecil + 0.05 else "hampir tidak berubah"
    return (
        "Pemotongan per karakter tidak mengenal batas kalimat maupun butir daftar. Gabungan ketiga PDF "
        f"(overlap {int(OVERLAP_UTAMA * 100)}%) - {rincian}. "
        f"Persentase chunk yang berakhir di tengah kalimat {arah} saat ukuran diperbesar dari "
        f"{UKURAN[0]} ke {UKURAN[-1]} karakter ({pz_kecil:.0%} menjadi {pz_besar:.0%}), sedangkan jumlah chunk "
        f"turun dari {n_kecil} menjadi {n_besar} dan tiap chunk memuat lebih banyak topik. "
        f"Dokumen ini pendek (rata-rata {rata:,} karakter), sehingga ukuran {UKURAN[-1]} hanya "
        "menghasilkan sedikit chunk dan angkanya kasar. "
        "Chunk pertama selalu bersih di awal karena dimulai dari posisi 0. Karena isinya penuh daftar poin, "
        "butir yang terpisah dari kalimat pembukanya kehilangan konteks. Perbaikan yang layak dicoba: "
        "pemotongan berbasis kalimat/paragraf dan memperlakukan satu butir daftar (beserta judul bagiannya) "
        "sebagai satu kesatuan."
    )


def main():
    rnd = random.Random(SEED)
    semua = [analisis_pdf(nama, rnd) for nama in NAMA_PDF]
    kesimpulan = buat_kesimpulan(semua)
    print("\nKesimpulan:", kesimpulan)

    L = Laporan(os.path.join(BASE, "Lab1_Eksperimen_Chunking.pdf"),
                "Lab 1 - Eksperimen Chunking", "Dikerjakan dengan Python (pdfplumber + fungsi potong)")
    for no_pdf, h in enumerate(semua, 1):
        L.h1(f"PDF {no_pdf}: {h['nama']}")
        L.h2("Langkah 1. Membaca PDF dan memeriksa teks")
        L.p("Berikut 500 karakter pertama hasil baca_pdf():")
        L.kode(h["teks"][:500])
        L.spasi()
        L.tabel([["Pemeriksaan", "Hasil"]] + [[k, v] for k, v in h["kualitas"].items()],
                [6 * 28.35, 8 * 28.35])
        L.p(catatan_kualitas(h))
        L.h2("Langkah 2. Jumlah chunk tiap pengaturan")
        L.p("Fungsi potong(teks, ukuran, overlap) memakai jendela geser per karakter; "
            "langkah = ukuran x (1 - overlap).")
        L.tabel(h["tabel_jumlah"])
        L.cap(f"Tabel {no_pdf}a. Jumlah chunk untuk 3 ukuran x 3 overlap. Makin besar ukuran, makin sedikit "
              "chunk; makin besar overlap, makin banyak chunk.")
        L.h2(f"Langkah 3. Chunk acak per ukuran (overlap {int(OVERLAP_UTAMA * 100)}%, seed {SEED})")
        L.tabel(h["statistik"])
        L.cap(f"Tabel {no_pdf}b. Statistik seluruh chunk pada tiap ukuran (bukan hanya yang dicuplik).")
        for u in UKURAN:
            L.p(f"Ukuran {u} karakter")
            for no, m, e, isi, aw, ak, dp in h["cuplikan"][u]:
                L.p(f"Chunk #{no} (karakter {m}-{e}) | awal di tengah kalimat: {'ya' if aw else 'tidak'} | "
                    f"akhir di tengah kalimat: {'ya' if ak else 'tidak'} | "
                    f"memotong butir daftar: {'ya' if dp else 'tidak'}")
                L.kode(isi)
                L.spasi(4)
        L.halaman_baru()
    L.h1("Kesimpulan")
    L.p(kesimpulan)
    L.halaman_baru()
    L.h1("Lampiran: kode lab1_chunking.py")
    L.kode(open(__file__, encoding="utf-8").read())
    L.simpan()
    print("\nLaporan: Lab1_Eksperimen_Chunking.pdf")


if __name__ == "__main__":
    main()