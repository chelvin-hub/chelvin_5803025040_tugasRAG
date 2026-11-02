"""Fungsi inti RAG sederhana: baca_pdf, potong, bangun_indeks, query, hit_at_k.

Backend embedding:
  - "neural": sentence-transformers (kalau terpasang & modelnya bisa diunduh)
  - "lsa"   : TF-IDF n-gram karakter + TruncatedSVD (semantik ringan, offline)
  - "tfidf" : TF-IDF n-gram karakter saja (pembanding berbasis kata/leksikal)
  - "auto"  : coba "neural", kalau gagal pakai "lsa"
"""
import glob
import os
import re

import numpy as np
import pdfplumber
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

FOLDER_DOKUMEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dokumen")
MODEL_NEURAL = "paraphrase-multilingual-MiniLM-L12-v2"


# ---------------------------------------------------------------- baca & potong
def baca_pdf(path):
    """Baca seluruh teks sebuah PDF (semua halaman digabung)."""
    halaman = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            halaman.append(p.extract_text() or "")
    return "\n".join(halaman)


def potong_dengan_posisi(teks, ukuran=1000, overlap=0.15):
    """Sliding window per karakter. Mengembalikan list (mulai, akhir, teks)."""
    if not 0 <= overlap < 1:
        raise ValueError("overlap harus 0 <= overlap < 1 (mis. 0.15 = 15%)")
    langkah = max(1, int(ukuran * (1 - overlap)))
    hasil, mulai = [], 0
    while mulai < len(teks):
        akhir = min(mulai + ukuran, len(teks))
        potongan = teks[mulai:akhir].strip()
        if potongan:
            hasil.append((mulai, akhir, potongan))
        if akhir == len(teks):
            break
        mulai += langkah
    return hasil


def potong(teks, ukuran=1000, overlap=0.15):
    """Potong teks menjadi chunk berukuran `ukuran` karakter dengan overlap pecahan."""
    return [t for _, _, t in potong_dengan_posisi(teks, ukuran, overlap)]


def norm(s):
    """Normalisasi untuk pencocokan kata kunci: huruf kecil, spasi/baris baru jadi satu spasi."""
    return re.sub(r"\s+", " ", s).lower().strip()


# ---------------------------------------------------------------------- indeks
class Indeks:
    def __init__(self, chunks, meta, backend="auto"):
        self.chunks, self.meta = chunks, meta
        self.backend = self._pilih_backend(backend)
        self._fit()

    def _pilih_backend(self, backend):
        if backend in ("auto", "neural"):
            try:
                from sentence_transformers import SentenceTransformer
                self._st = SentenceTransformer(MODEL_NEURAL)
                return "neural"
            except Exception:
                if backend == "neural":
                    raise
                return "lsa"
        return backend

    def _fit(self):
        if self.backend == "neural":
            self.Z = np.asarray(self._st.encode(self.chunks, normalize_embeddings=True))
            return
        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        X = self.vec.fit_transform(self.chunks)
        if self.backend == "tfidf":
            self.Z = normalize(X)
        else:  # lsa
            nc = max(2, min(64, X.shape[0] - 1, X.shape[1] - 1))
            self.svd = TruncatedSVD(n_components=nc, random_state=0)
            self.Z = normalize(self.svd.fit_transform(X))

    def skor(self, pertanyaan):
        if self.backend == "neural":
            q = np.asarray(self._st.encode([pertanyaan], normalize_embeddings=True))
            return np.asarray(self.Z @ q.T).ravel()
        q = self.vec.transform([pertanyaan])
        if self.backend == "tfidf":
            q = normalize(q)
            return np.asarray((self.Z @ q.T).todense()).ravel()
        q = normalize(self.svd.transform(q))
        return (self.Z @ q.T).ravel()


def bangun_indeks(folder=FOLDER_DOKUMEN, ukuran=1000, overlap=0.15, backend="auto", verbose=True):
    """Baca semua PDF di `folder`, potong, lalu bangun indeks. Mencetak jumlah chunk per file."""
    chunks, meta = [], []
    for path in sorted(glob.glob(os.path.join(folder, "*.pdf"))):
        nama = os.path.basename(path)
        bagian = potong(baca_pdf(path), ukuran, overlap)
        if verbose:
            print(f"  {nama}: {len(bagian)} chunk")
        for i, c in enumerate(bagian):
            chunks.append(c)
            meta.append({"file": nama, "no": i})
    if not chunks:
        raise FileNotFoundError(f"Tidak ada PDF di {folder}")
    idx = Indeks(chunks, meta, backend)
    if verbose:
        print(f"  Total {len(chunks)} chunk | ukuran={ukuran} overlap={overlap:.0%} | backend={idx.backend}")
    return idx


def query(indeks, pertanyaan, k=3):
    """Kembalikan k chunk teratas: list dict(skor, file, no, teks)."""
    s = indeks.skor(pertanyaan)
    urut = np.argsort(-s)[:k]
    return [{"skor": float(s[i]), "file": indeks.meta[i]["file"], "no": indeks.meta[i]["no"],
             "teks": indeks.chunks[i]} for i in urut]


# ------------------------------------------------------------------- evaluasi
def cocok(teks, kata_kunci):
    """True bila SEMUA kata kunci muncul dalam teks (tanpa peduli huruf besar/kecil)."""
    t = norm(teks)
    return all(norm(k) in t for k in kata_kunci)


def peringkat_hit(indeks, soal):
    """Peringkat (mulai dari 1) chunk pertama yang memuat kata kunci; None bila tidak ada."""
    s = indeks.skor(soal["q"])
    for rank, i in enumerate(np.argsort(-s), start=1):
        if cocok(indeks.chunks[i], soal["kw"]):
            return rank
    return None


def hit_at_k(indeks, daftar_soal, k):
    """Proporsi soal yang chunk berisi kata kunci jawabannya masuk k teratas."""
    hit = 0
    for soal in daftar_soal:
        atas = query(indeks, soal["q"], k)
        hit += any(cocok(a["teks"], soal["kw"]) for a in atas)
    return hit / len(daftar_soal)
