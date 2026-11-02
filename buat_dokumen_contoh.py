"""Membuat 3 PDF contoh (bahasa Indonesia) di folder dokumen/.

Jika Anda sudah punya PDF sendiri, cukup letakkan di folder dokumen/ dan
lewati skrip ini. Skrip ini hanya agar seluruh lab bisa dijalankan langsung.
"""
import os
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

BASE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(BASE, "dokumen")

DOKUMEN = {
"pengantar_rag.pdf": {
 "judul": "Pengantar Retrieval-Augmented Generation (RAG)",
 "bagian": [
  ("1. Pengertian RAG", [
   "Retrieval-Augmented Generation (RAG) adalah arsitektur yang menggabungkan pencarian dokumen dengan model bahasa besar. Model tidak hanya mengandalkan pengetahuan hasil pelatihan, tetapi juga menerima potongan dokumen yang relevan sebagai konteks tambahan saat menjawab pertanyaan.",
   "Pendekatan ini diperkenalkan oleh Lewis dan kawan-kawan pada tahun 2020 di Facebook AI Research. Tujuannya adalah mengurangi halusinasi dan memungkinkan jawaban bersumber dari dokumen terbaru tanpa harus melatih ulang model dari awal."]),
  ("2. Alur Kerja RAG", [
   "Sistem RAG terdiri dari dua tahap, yaitu tahap pengindeksan yang berjalan offline dan tahap penjawaban yang berjalan online. Pada tahap pengindeksan, dokumen dibaca, dipotong menjadi chunk, diubah menjadi vektor embedding, lalu disimpan dalam vector store.",
   "Pada tahap penjawaban, pertanyaan pengguna diubah menjadi vektor dengan model embedding yang sama. Sistem lalu mengambil k chunk yang paling dekat dengan vektor pertanyaan dan menyisipkannya ke dalam prompt untuk model bahasa."]),
  ("3. Embedding dan Kemiripan", [
   "Embedding adalah representasi teks berupa vektor bilangan real dengan dimensi tetap. Model MiniLM menghasilkan embedding 384 dimensi, sedangkan model berbasis BERT-base menghasilkan 768 dimensi. Teks dengan makna mirip akan menghasilkan vektor yang berdekatan.",
   "Kemiripan antar vektor biasanya diukur dengan cosine similarity, yang bernilai antara -1 dan 1. Semakin mendekati 1, semakin searah kedua vektor tersebut. Pencarian semantik tetap dapat menemukan dokumen walaupun kata dalam pertanyaan berbeda dari teks, misalnya pertanyaan tentang kendaraan roda empat yang cocok dengan dokumen tentang mobil."]),
  ("4. Chunking", [
   "Chunk yang terlalu kecil kehilangan konteks, sedangkan chunk yang terlalu besar mencampur beberapa topik sehingga skor kemiripannya menjadi encer. Praktik yang umum adalah ukuran 500 sampai 1000 karakter dengan overlap 10 sampai 20 persen.",
   "Overlap mencegah informasi penting terpotong tepat di batas antar chunk. Pemotongan berbasis kalimat atau paragraf lebih rapi daripada pemotongan karakter murni, tetapi ukuran chunk menjadi tidak seragam. Tabel perlu diperlakukan khusus karena baris tabel kehilangan makna bila terpisah dari baris judul kolomnya."]),
  ("5. Vector Store", [
   "Vector store menyimpan embedding dan mendukung pencarian tetangga terdekat. FAISS adalah pustaka buatan Meta untuk pencarian tetangga terdekat yang sangat cepat. ChromaDB menyimpan embedding bersama metadata seperti nama file dan nomor halaman, sedangkan Qdrant menyediakan layanan server tersendiri.",
   "Untuk koleksi besar, banyak vector store memakai indeks HNSW yang mencari tetangga terdekat secara aproksimasi demi kecepatan, dengan sedikit pengorbanan akurasi."]),
  ("6. Evaluasi Retrieval", [
   "Hit@k adalah proporsi pertanyaan uji yang jawaban benarnya muncul di antara k chunk teratas. Sebagai contoh, bila 12 dari 15 pertanyaan terjawab pada lima chunk teratas, maka Hit@5 bernilai 0,8. Metrik lain yang sering dipakai adalah MRR dan Recall@k.",
   "Disarankan menyiapkan minimal 15 sampai 30 pertanyaan uji lengkap dengan kata kunci jawaban. Bandingkan beberapa pengaturan chunk pada pertanyaan yang sama agar perbedaannya adil."]),
  ("7. Halusinasi dan Sitasi", [
   "Halusinasi adalah keluaran model yang terdengar meyakinkan tetapi tidak didukung fakta. RAG mengurangi halusinasi, tetapi tidak menghilangkannya sepenuhnya, terutama bila chunk yang diambil tidak relevan.",
   "Sistem yang baik menampilkan sumber berupa nama file dan nomor halaman sehingga pengguna dapat memeriksa jawaban. Bila chunk teratas tidak relevan, model sebaiknya menjawab bahwa informasi tidak ditemukan daripada mengarang."]),
 ],
 "tabel": {"setelah_bagian": "4. Chunking",
  "caption": "Tabel 1. Perbandingan ukuran chunk",
  "data": [["Ukuran", "Kelebihan", "Kekurangan", "Cocok untuk"],
           ["500 karakter", "Presisi tinggi, hemat token", "Konteks sempit, kalimat sering terpotong", "FAQ dan pertanyaan faktual singkat"],
           ["1000 karakter", "Seimbang antara konteks dan presisi", "Kadang memuat dua topik", "Dokumen laporan umum"],
           ["1500 karakter", "Konteks luas", "Skor encer dan boros token", "Dokumen naratif panjang"]]},
},
"machine_learning_dasar.pdf": {
 "judul": "Dasar-Dasar Machine Learning",
 "bagian": [
  ("1. Supervised Learning", [
   "Pada supervised learning, model belajar dari data yang sudah berlabel. Tugas klasifikasi memprediksi kategori, misalnya menandai surel sebagai spam atau bukan spam. Tugas regresi memprediksi nilai kontinu, misalnya harga rumah berdasarkan luas dan lokasi."]),
  ("2. Pembagian Data", [
   "Data biasanya dibagi menjadi data latih 70 persen, data validasi 15 persen, dan data uji 15 persen. Data validasi dipakai untuk menyetel hiperparameter, sedangkan data uji hanya dipakai satu kali di akhir untuk menilai performa akhir. Data uji tidak boleh dipakai saat tuning karena akan menyebabkan kebocoran informasi."]),
  ("3. Overfitting dan Underfitting", [
   "Overfitting terjadi ketika model sangat baik pada data latih tetapi buruk pada data baru. Cirinya adalah selisih besar antara akurasi latih, misalnya 99 persen, dan akurasi validasi, misalnya 72 persen. Model seolah menghafal data latih, termasuk derau di dalamnya.",
   "Underfitting terjadi ketika model terlalu sederhana sehingga akurasi latih maupun validasi sama-sama rendah. Cara mengatasi overfitting antara lain regularisasi, early stopping, dropout pada jaringan saraf, dan menambah jumlah data."]),
  ("4. Cross-Validation", [
   "Cross-validation menilai model secara lebih stabil daripada satu kali pembagian data. Pada k-fold cross-validation, data dibagi menjadi k lipatan dan setiap lipatan bergantian menjadi data validasi. Nilai k yang lazim adalah 5 atau 10.",
   "Untuk kelas yang tidak seimbang, gunakan stratified k-fold agar proporsi kelas pada tiap lipatan tetap terjaga."]),
  ("5. Metrik Klasifikasi", [
   "Akurasi menghitung proporsi prediksi yang benar, tetapi menyesatkan bila kelas tidak seimbang. Precision mengukur seberapa banyak prediksi positif yang benar, sedangkan recall mengukur seberapa banyak data positif yang berhasil ditemukan.",
   "F1-score adalah rata-rata harmonik dari precision dan recall sehingga nilainya rendah bila salah satunya rendah. Untuk deteksi penyakit, recall diutamakan karena melewatkan pasien jauh lebih berbahaya daripada alarm palsu. Untuk filter spam, precision diutamakan agar surel penting tidak terbuang."]),
  ("6. Gradient Descent", [
   "Gradient descent adalah algoritma optimasi iteratif yang memperbarui parameter ke arah berlawanan dengan gradien fungsi kerugian. Learning rate yang terlalu besar membuat pelatihan divergen, sedangkan yang terlalu kecil membuat pelatihan sangat lambat.",
   "Pada mini-batch gradient descent, gradien dihitung dari sebagian kecil data, biasanya berukuran 32 atau 64 sampel per langkah."]),
  ("7. Decision Tree dan Random Forest", [
   "Decision tree membagi data berdasarkan fitur dengan kriteria Gini impurity atau entropi. Pohon yang terlalu dalam cenderung overfitting. Random forest menggabungkan banyak pohon yang dilatih pada sampel acak berbeda (bagging) lalu mengambil suara terbanyak, sehingga variansi prediksi menurun."]),
  ("8. Regularisasi", [
   "Regularisasi L1, atau Lasso, mendorong sebagian bobot menjadi tepat nol sehingga berfungsi sebagai seleksi fitur. Regularisasi L2, atau Ridge, mengecilkan bobot tanpa menjadikannya nol. Kekuatan regularisasi diatur oleh hiperparameter lambda."]),
 ],
 "tabel": {"setelah_bagian": "5. Metrik Klasifikasi",
  "caption": "Tabel 1. Ringkasan metrik klasifikasi",
  "data": [["Metrik", "Rumus", "Dipakai ketika"],
           ["Akurasi", "(TP+TN)/(TP+TN+FP+FN)", "Kelas seimbang"],
           ["Precision", "TP/(TP+FP)", "Biaya false positive tinggi"],
           ["Recall", "TP/(TP+FN)", "Biaya false negative tinggi"],
           ["F1-score", "2*P*R/(P+R)", "Kelas tidak seimbang"]]},
},
"etika_keamanan_ai.pdf": {
 "judul": "Etika dan Keamanan Kecerdasan Buatan",
 "bagian": [
  ("1. Bias pada Data", [
   "Model kecerdasan buatan mewarisi bias yang ada pada data latihnya. Contoh yang sering dikutip adalah sistem seleksi pelamar kerja milik Amazon yang dihentikan pada tahun 2018 karena cenderung merendahkan pelamar perempuan, akibat dilatih dengan data riwayat perekrutan yang didominasi laki-laki.",
   "Mitigasi bias mencakup audit dataset, pengukuran metrik kewajaran antar kelompok, serta pengujian model pada subkelompok yang berbeda sebelum digunakan."]),
  ("2. Privasi dan Pelindungan Data Pribadi", [
   "Di Indonesia, pelindungan data pribadi diatur dalam Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi. Prinsip pentingnya adalah minimisasi data, persetujuan yang eksplisit dari pemilik data, serta hak subjek data untuk mengakses dan meminta penghapusan datanya.",
   "Anonimisasi menghapus identitas secara permanen, sedangkan pseudonimisasi hanya mengganti identitas dengan kode yang masih dapat ditelusuri kembali. Keduanya mengurangi risiko, tetapi hanya anonimisasi yang benar-benar melepaskan data dari pemiliknya."]),
  ("3. Transparansi dan Keterjelasan", [
   "Model kotak hitam sulit dijelaskan kepada pengguna yang terdampak keputusannya. Teknik seperti LIME dan SHAP memperkirakan seberapa besar kontribusi tiap fitur terhadap satu prediksi. Keterjelasan penting pada bidang berisiko tinggi seperti kredit, kesehatan, dan hukum."]),
  ("4. Serangan Adversarial", [
   "Serangan adversarial mengubah input sedikit saja, sering kali dengan derau yang tidak terlihat oleh mata, sehingga model salah mengklasifikasi. Contoh terkenal adalah stiker kecil pada rambu stop yang membuat model penglihatan komputer membacanya sebagai rambu batas kecepatan. Pertahanan yang umum adalah adversarial training, yaitu melatih model dengan contoh serangan."]),
  ("5. Prompt Injection", [
   "Prompt injection adalah serangan berupa instruksi berbahaya yang disisipkan dalam masukan pengguna atau dalam dokumen, dengan tujuan membajak perilaku model. Risikonya besar pada sistem RAG karena dokumen yang diambil diperlakukan sebagai konteks tepercaya.",
   "Mitigasinya antara lain memisahkan instruksi sistem dari data, menyaring keluaran model, dan menerapkan hak akses minimum pada alat yang dapat dipanggil model."]),
  ("6. Tata Kelola dan Akuntabilitas", [
   "Tata kelola yang baik mencakup audit berkala, keterlibatan manusia dalam pengambilan keputusan penting (human in the loop), dan pencatatan log keputusan. Dokumentasi model dalam bentuk model card diperkenalkan oleh Mitchell dan kawan-kawan pada tahun 2019 untuk menjelaskan tujuan, data, dan batasan sebuah model.",
   "Akuntabilitas tetap berada pada manusia dan organisasi yang menerapkan sistem, bukan pada model itu sendiri."]),
 ],
 "tabel": {"setelah_bagian": "5. Prompt Injection",
  "caption": "Tabel 1. Ringkasan risiko dan mitigasi",
  "data": [["Risiko", "Contoh", "Mitigasi"],
           ["Bias", "Seleksi otomatis menolak kelompok tertentu", "Audit dataset"],
           ["Kebocoran data", "Model mengungkap data pribadi", "Anonimisasi"],
           ["Serangan adversarial", "Stiker pada rambu stop", "Adversarial training"],
           ["Prompt injection", "Instruksi tersembunyi di dokumen", "Pisahkan instruksi dari data"]]},
},
}


def buat_pdf(nama_file, isi):
    st = getSampleStyleSheet()
    judul = ParagraphStyle("j", parent=st["Title"], fontSize=18, spaceAfter=14)
    h = ParagraphStyle("h", parent=st["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=4)
    p = ParagraphStyle("p", parent=st["BodyText"], fontSize=10.5, leading=15, spaceAfter=6)
    cap = ParagraphStyle("c", parent=p, fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    sel = ParagraphStyle("s", parent=p, fontSize=9, leading=11, spaceAfter=0)
    doc = SimpleDocTemplate(os.path.join(FOLDER, nama_file), pagesize=A4,
                            leftMargin=60, rightMargin=60, topMargin=60, bottomMargin=60,
                            title=isi["judul"])
    cerita = [Paragraph(escape(isi["judul"]), judul)]
    t = isi["tabel"]
    for nama, paragraf in isi["bagian"]:
        cerita.append(Paragraph(escape(nama), h))
        for kal in paragraf:
            cerita.append(Paragraph(escape(kal), p))
        if nama == t["setelah_bagian"]:
            cerita.append(Paragraph(escape(t["caption"]), cap))
            data = [[Paragraph(escape(c), sel) for c in baris] for baris in t["data"]]
            tb = Table(data, hAlign="LEFT")
            tb.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                    ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            cerita.append(tb)
            cerita.append(Paragraph("Sumber: ringkasan penulis.", p))
    doc.build(cerita)


if __name__ == "__main__":
    os.makedirs(FOLDER, exist_ok=True)
    for nama, isi in DOKUMEN.items():
        buat_pdf(nama, isi)
        print("dibuat:", os.path.join("dokumen", nama))
