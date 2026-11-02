# Lab RAG: Chunking, Indeks, dan Hit@k

Jalankan dari dalam folder ini:

    pip install pdfplumber scikit-learn numpy matplotlib reportlab pillow
    python buat_dokumen_contoh.py   # opsional: buat 3 PDF contoh di dokumen/
    python lab1_chunking.py         # -> Lab1_Eksperimen_Chunking.pdf
    python lab2_indeks_cari.py      # -> Lab2_Indeks_dan_Pencarian.pdf
    python lab3_hit_at_k.py         # -> Lab3_Hit_at_k.pdf

Untuk memakai PDF sendiri: taruh di dokumen/, lalu ubah PDF di lab1, PERTANYAAN/PARAFRASE di lab2,
dan SOAL (15 pertanyaan + kata kunci) di lab3.

Embedding: otomatis memakai sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) bila terpasang;
jika tidak, memakai LSA (TF-IDF n-gram karakter + SVD) yang berjalan offline.
