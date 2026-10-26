# Naskah Pitch Proposal UTS: MataSawit

Naskah ini menyertai deck **MataSawit – Pitch Proposal Kelompok 3** (12 slide; https://claude.ai/artifact/6UVcmoCi8rtajxoV9UBcty, dapat diunduh sebagai PPTX/PDF dan berisi naskah yang sama di catatan pembicara), slide demi slide, untuk sidang proposal UTS. Format sidang menurut panduan: 15 menit per kelompok, terdiri dari **8 menit presentasi, 5 menit tanya jawab**, dan 2 menit pergantian. Semua anggota wajib berbicara atau menjawab.

Naskah ditulis untuk diucapkan, bukan dibacakan. Nadanya pitch: meyakinkan, tetapi tetap jujur dan terukur, seperti mengajukan proyek kepada klien yang awam teknologi. **Yedija** adalah ketua proyek: ia membuka, menutup, menjembatani antarbagian, dan memandu sesi tanya jawab.

**Konvensi.**

- **[➡️ Slide n]** berarti pindah ke slide n. Klik tepat saat membaca tanda ini, lalu beri jeda satu ketukan sebelum kalimat pertama slide baru.
- **[jeda]** berarti berhenti satu sampai dua detik supaya audiens sempat mencerna.
- **[tunjuk ...]** berarti arahkan pandangan atau *pointer* ke bagian slide yang disebut.
- **[serah ke ...]** adalah kalimat pergantian pembicara. Ucapkan persis, lalu orang berikutnya langsung melangkah maju; jangan ada jeda kosong.
- Istilah teknis diucapkan dalam bahasa Inggris dan dicetak miring. Saat pertama muncul, istilah itu langsung diikuti penjelasan singkat dalam bahasa Indonesia.

## Daftar Isi

- [1. Peta waktu dan pembagian peran](#1-peta-waktu-dan-pembagian-peran)
- [2. Naskah per slide](#2-naskah-per-slide)
- [3. Catatan penyampaian](#3-catatan-penyampaian)
- [4. Antisipasi tanya jawab](#4-antisipasi-tanya-jawab)
- [5. Angka yang wajib dihafal](#5-angka-yang-wajib-dihafal)

## 1. Peta waktu dan pembagian peran

Total sekitar **7 menit 25 detik**, menyisakan kira-kira 35 detik cadangan dalam slot 8 menit. Kolom "Selesai paling lambat" adalah patokan saat latihan dengan pengatur waktu.

| Slide | Bagian | Pembicara | Durasi | Selesai paling lambat |
|---|---|---|---|---|
| 1 | Judul dan tim | Yedija | 30 detik | 0:30 |
| 2 | Masalah: dinilai dengan mata | Yedija | 35 detik | 1:05 |
| 3 | Kerugian di gerbang pabrik | Yedija | 40 detik | 1:45 |
| 4 | Solusi: MataSawit | Yedija | 35 detik | 2:20 |
| 5 | Data | Juanito | 35 detik | 2:55 |
| 6 | Temuan audit: kebocoran | Juanito | 45 detik | 3:40 |
| 7 | Perbaikan: split blok | Juanito | 40 detik | 4:20 |
| 8 | Metode ordinal | Steven | 40 detik | 5:00 |
| 9 | Model dan eksperimen | Steven | 40 detik | 5:40 |
| 10 | Evaluasi dan penerapan | Steven | 40 detik | 6:20 |
| 11 | Rencana dan risiko | Yedija | 35 detik | 6:55 |
| 12 | Mengapa layak disetujui | Yedija | 30 detik | 7:25 |

**Pembagian peran.**

| Anggota | Bagian presentasi | Fokus tanya jawab |
|---|---|---|
| **Yedija** (ketua proyek) | slide 1–4 dan 11–12 | latar belakang, kegunaan, batas klaim, rencana kerja; memandu sesi tanya jawab |
| **Juanito** (data) | slide 5–7 | dataset, lisensi, audit kebocoran, split blok, label manual |
| **Steven** (model) | slide 8–10 | CORN, EfficientNet, eksperimen, metrik, demo dan latensi |

## 2. Naskah per slide

### Slide 1: Judul dan tim (0:00–0:30) · Yedija

**[Slide 1]**

Selamat pagi, Bapak/Ibu. Kami Kelompok 3. Saya Yedija, ketua proyek, bersama Juanito yang memegang data dan Steven yang memegang model.

Kami mengajukan **MataSawit**: alat yang menilai tingkat kematangan tandan sawit hanya dari satu foto ponsel. [tunjuk deretan foto] Inilah lima tingkat yang dinilai, dari mentah sampai busuk, semuanya foto asli dari kebun di Kalimantan Tengah. [jeda]

### Slide 2: Masalah (0:30–1:05) · Yedija

**[➡️ Slide 2]**

Kenapa sawit? Indonesia adalah produsen sawit nomor satu dunia, dengan hampir 17 juta hektare kebun, dan menguasai lebih dari separuh ekspor minyak sawit dunia. Sepertiga produksinya berasal dari kebun rakyat.

[tunjuk kartu gelap] Kalimantan Tengah, tempat data kami dipotret, menyumbang 17,6 persen produksi nasional.

Tetapi mutu komoditas sebesar ini masih dinilai dengan mata, dan penilaian manual di pabrik dikenal subjektif serta sering memicu sengketa. [jeda]

### Slide 3: Kerugian di gerbang pabrik (1:05–1:45) · Yedija

**[➡️ Slide 3]**

Ini contoh nyata dari buku panduan pekebun terbitan Wageningen University. [tunjuk alur] Satu truk membawa 8.430 kilogram tandan. Di pabrik, petugas hanya memeriksa sekitar sepuluh persen tandan, dengan mata. Hasilnya, 156 kilogram dipotong, 84 kilogram karena buah dinilai mentah.

[tunjuk angka oranye] Pekebun kehilangan 249.600 rupiah dari satu kiriman. Panen terlalu dini, minyaknya sedikit; terlambat, mutunya turun. Dan pekebun baru tahu setelah sampai di pabrik. [jeda]

### Slide 4: Solusi MataSawit (1:45–2:20) · Yedija

**[➡️ Slide 4]**

Solusi kami: MataSawit. [tunjuk kiri ke kanan] Pengguna memotret satu tandan, model membaca warna, tekstur, dan buah yang mulai rontok, lalu menampilkan tingkat kematangan nol sampai empat, peluang tiap tingkat, peta panas bagian foto yang menentukan, dan peringatan kalau model ragu. Tampilan ini masih ilustrasi tampilan aplikasinya.

[tunjuk baris bawah] Penggunanya pekebun, pengepul, petugas sortasi, dan peneliti.

**[serah ke Juanito]** "Datanya dari mana? Juanito akan menjelaskan."

### Slide 5: Data (2:20–2:55) · Juanito

**[➡️ Slide 5]**

Terima kasih, Yedija. Kami memakai dataset terbuka dari Mendeley Data, disusun tim ITS bersama industri sawit: 4.728 foto lapangan dari Kalimantan Tengah, lima tingkat yang berurutan. [tunjuk foto]

Lisensinya CC BY, jadi legal dipakai, dan sudah kami unduh serta cek keasliannya. [tunjuk kotak kanan] Kelasnya tidak seimbang: Matang Penuh 3,6 kali lebih banyak daripada Busuk, jadi akurasi saja tidak cukup.

Tetapi temuan terpenting muncul saat kami mengaudit datanya. [jeda]

### Slide 6: Temuan audit (2:55–3:40) · Juanito

**[➡️ Slide 6]**

Foto dalam dataset ini diambil beruntun: satu tandan dipotret beberapa kali, dengan nomor berkas berurutan. [tunjuk dua foto] Immature126 dan 127 jelas tandan yang sama, tetapi pembagian data resmi yang acak memasukkan satu ke data latih dan satunya ke data uji.

[tunjuk 92%] Sembilan puluh dua persen foto uji resmi punya tetangga bernomor langsung di data latih. [tunjuk 62%] Kami cek manual 40 pasangan: 62 persen yang bisa diputuskan memang tandan yang sama.

Artinya, model bisa diuji dengan tandan yang sudah pernah ia lihat, seperti ujian yang soalnya bocor. [jeda]

### Slide 7: Perbaikan: split blok (3:40–4:20) · Juanito

**[➡️ Slide 7]**

Solusinya *split blok*, atau pembagian per blok. Nomor berkas tiap kelas kami potong per dua puluh foto, dan satu blok selalu berada di satu bagian.

[tunjuk baris kedua tabel] Foto uji yang bertetangga dengan data latih turun dari 92 persen menjadi 8,3 persen. [tunjuk baris bawah] Dampaknya terlihat bahkan pada model warna sederhana: macro-F1 0,681 di split resmi, tetapi 0,657 di split blok. Angka resmi tampak lebih bagus karena bocor.

Jadi split blok menjadi acuan kami, dan split resmi tetap dilaporkan sebagai pembanding.

**[serah ke Steven]** "Bagaimana modelnya dibangun, Steven akan menjelaskan."

### Slide 8: Metode ordinal (4:20–5:00) · Steven

**[➡️ Slide 8]**

Terima kasih, Juanito. Yang membuat masalah ini istimewa: tingkat kematangan itu **berurutan**. [tunjuk panel atas] Klasifikasi biasa, *cross-entropy*, memperlakukannya seperti lima laci tanpa urutan, sehingga salah satu tingkat dan salah tiga tingkat dihukum sama.

[tunjuk panel hijau] Metode utama kami, CORN, mengubahnya menjadi tangga pertanyaan ya atau tidak: lebih matang dari mentah? Lebih matang dari setengah matang? Jumlah jawaban "ya" menjadi tingkatnya.

Pertanyaan utama kami: apakah cara ini mengurangi kesalahan berat tanpa mengorbankan ketepatan. [jeda]

### Slide 9: Model dan eksperimen (5:00–5:40) · Steven

**[➡️ Slide 9]**

Modelnya EfficientNet-B0, jaringan konvolusi ringan sekitar empat juta parameter yang sudah belajar dari jutaan foto ImageNet, lalu kami latih ulang dengan foto sawit. [tunjuk dua kepala] Ujungnya dua: kepala biasa sebagai pembanding, dan kepala CORN sebagai metode utama.

[tunjuk tabel] Ada delapan eksperimen: E0 dan E1 baseline, E2 lawan E3 pertanyaan utama, E4 menguji augmentasi warna, E5 membantu kelas kecil, dan E6, E7 mengukur kebocoran. Setiap perbandingan hanya mengubah satu faktor, diulang tiga *seed*, atau tiga kali pengacakan awal. [jeda]

### Slide 10: Evaluasi dan penerapan (5:40–6:20) · Steven

**[➡️ Slide 10]**

[tunjuk kiri] Kami tidak hanya melihat akurasi. *Macro-F1* memastikan kelas kecil seperti busuk dihitung adil; MAE dan kesalahan berat mengukur seberapa jauh model meleset. Data uji hanya dibuka sekali.

[tunjuk kanan] Model dilatih di GPU gratis Google Colab, lalu dijalankan sebagai aplikasi web di laptop biasa, dengan cadangan perintah baris.

[tunjuk kotak hijau] Kriteria sukses ini kami tetapkan sebelum melatih model, dan kalau hasilnya negatif, tetap kami laporkan.

**[serah ke Yedija]** "Kembali ke Yedija untuk rencana kerjanya."

### Slide 11: Rencana dan risiko (6:20–6:55) · Yedija

**[➡️ Slide 11]**

Terima kasih, Steven. [tunjuk kotak gelap] Fondasinya sudah jadi: data diunduh dan diaudit, split blok dibuat, baseline sudah dijalankan, 18 model CNN pertama sudah dilatih, dan seluruh *pipeline*, atau alur kerja otomatisnya, lulus 21 uji.

[tunjuk tabel] Berikutnya, mengikuti jadwal checkpoint: evaluasi terkontrol, analisis kesalahan, demo, laporan, sampai demo langsung di UAS. [tunjuk baris bawah] Risikonya sudah ada cadangan: satu seed dulu kalau GPU terbatas, hasil negatif tetap dilaporkan, dan cadangan video kalau demo gagal. [jeda]

### Slide 12: Mengapa layak disetujui (6:55–7:25) · Yedija

**[➡️ Slide 12]**

Empat alasan. Masalahnya nyata dan bernilai uang bagi pekebun. Datanya legal, sudah diaudit dan diuji. Solusinya murah: foto ponsel, GPU gratis, laptop biasa. Dan kami bekerja jujur: kebocoran sudah ditemukan sebelum melatih, dan kriteria sukses ditetapkan dari awal. [jeda]

Karena itu kami memohon persetujuan untuk melanjutkan ke pelatihan model dan demo. Terima kasih; kami siap menerima pertanyaan.

## 3. Catatan penyampaian

- **Tempo.** Bagian lisan naskah ini sekitar 800 kata. Dibawakan dengan tempo tenang, ditambah jeda dan pergantian pembicara, durasinya 7–7,5 menit. Latih bertiga minimal tiga kali dengan pengatur waktu, termasuk pergantian pembicara, dan cocokkan dengan kolom "Selesai paling lambat".
- **Pergantian pembicara.** Kalimat **[serah ke ...]** adalah jembatan. Pembicara berikutnya sudah berdiri di samping sebelum kalimat itu selesai, lalu membuka dengan "Terima kasih, [nama]." Jangan berebut *clicker*: yang sedang bicara memegang klik.
- **Bila waktu menipis**, potong sesuai urutan ini tanpa mengubah slide:
  1. kalimat "Penggunanya pekebun, pengepul..." di slide 4 (sudah terlihat di slide);
  2. daftar E4–E7 di slide 9, cukup "dan empat eksperimen pendukung";
  3. kalimat "Panen terlalu dini..." di slide 3.

  **Jangan memotong** angka 92% dan 62% di slide 6, perbandingan macro-F1 0,681 vs 0,657 di slide 7, dan kalimat "kalau hasilnya negatif, tetap kami laporkan" di slide 10. Itulah yang membuat pitch terdengar jujur dan berbeda.
- **Kontak mata.** Slide memuat angka yang sama dengan naskah, jadi tidak perlu membaca slide. Lihat penguji, lalu tunjuk angkanya saat menyebutnya.
- **Angka desimal.** Ucapkan "tujuh belas koma enam persen", bukan "tujuh belas titik enam". "Rp249.600" diucapkan "dua ratus empat puluh sembilan ribu enam ratus rupiah".
- **Hasil awal sudah ada, tetapi jangan dibesar-besarkan.** Pitch ini tetap proposal. Kalau ditanya, sebutkan angka di T1 dan T11 apa adanya, termasuk bahwa CORN tidak lebih baik daripada CE.
- **Slide 4 adalah ilustrasi.** Ucapkan kalimat "Tampilan ini masih ilustrasi" agar penguji tidak mengira modelnya sudah jadi.
- **Hindari pengisi santai** ("nah", "jadi gini", "kayak"). Penghubung yang dipakai cukup "pertama", "kedua", "artinya", dan "karena itu".
- **Persiapan teknis.** Buka deck dalam mode *Present* sebelum giliran. Unduh juga sebagai PDF atau PPTX dan simpan di laptop serta *flashdisk* sebagai cadangan bila internet kampus bermasalah.

## 4. Antisipasi tanya jawab

Pertanyaan yang perlu disiapkan paling matang ditandai **⚠️**. **Yedija memandu**: bila pertanyaan tidak ditujukan ke orang tertentu, Yedija mengucapkan "Terima kasih atas pertanyaannya; [nama] akan menjawab," sesuai kolom penjawab. Bila pertanyaan di luar cakupan, katakan terus terang, lalu sampaikan apa yang dapat disimpulkan dari data yang ada. Panduan mewajibkan **semua anggota** berbicara atau menjawab, jadi usahakan Juanito dan Steven masing-masing menjawab minimal satu pertanyaan.

### 4.1 Masalah dan kegunaan (penjawab: Yedija)

**⚠️ T1. "Seberapa akurat nanti? Apakah bisa menggantikan petugas sortasi?"**

"Hasil pelatihan pertama sudah ada. Pada split blok, CNN mencapai akurasi sekitar 91 persen dan macro-F1 0,91, jauh di atas baseline warna yang macro-F1-nya 0,657, dan hanya sekitar 2 persen prediksi yang meleset dua tingkat atau lebih. Soal menggantikan petugas: tidak. Posisinya pendapat kedua yang konsisten, karena datanya dari satu wilayah dan belum diuji pada foto tumpukan di pabrik."

**T2. "Angka Rp249.600 itu dari kapan? Apakah masih berlaku?"**

"Itu contoh formulir sortasi dalam buku panduan Wageningen terbitan 2016, pada harga TBS saat itu, Rp1,6 juta per ton. Kami memakainya untuk menunjukkan mekanisme potongan, bukan sebagai estimasi kerugian hari ini. Karena potongannya dihitung dalam kilogram, besarnya ikut harga TBS yang berlaku."

**T3. "Apakah bisa dipakai di kebun yang tidak ada sinyal?"**

"Versi semester ini berbasis web, jadi butuh koneksi atau laptop di lokasi. Modelnya ringan, sekitar 16 megabyte, sehingga aplikasi ponsel *offline* lewat ONNX atau TFLite realistis sebagai pengembangan lanjutan, tetapi tidak kami janjikan dalam semester ini."

**T4. "Apa bedanya dengan penelitian sebelumnya tentang kematangan sawit?"**

"Kami tidak mengklaim arsitektur baru. Bedanya ada dua: pertama, kami memperlakukan tingkat kematangan sebagai urutan dan mengukur jarak kesalahan, sedangkan pekerjaan sebelumnya memakai klasifikasi biasa. Kedua, kami mengaudit kebocoran data dan menyediakan split yang lebih jujur, sehingga angkanya tidak menggelembung."

**T5. "Data hanya dari Kalimantan Tengah. Apakah berlaku di daerah lain?"**

"Belum dapat kami pastikan, dan itu kami tulis sebagai batasan. Ke depan, model dapat diuji pada dataset lain yang sudah terbit, misalnya foto tumpukan di pabrik dan dataset kematangan luar ruangan."

### 4.2 Data dan audit (penjawab: Juanito)

**⚠️ T6. "Kalau datanya bocor, kenapa tidak memakai dataset lain saja?"**

"Datasetnya tetap bernilai: legal, cukup besar, kategorinya ditetapkan dengan masukan ahli, dan lima tingkatnya berurutan, sesuai pertanyaan kami. Yang bermasalah bukan fotonya, melainkan cara pembagian resminya. Itu yang kami perbaiki dengan split blok. Justru temuan ini menjadi salah satu kontribusi kami."

**⚠️ T7. "Bagaimana kalian yakin split blok sudah cukup? Kenapa 20?"**

"Ada dua bukti: foto uji yang bertetangga dengan data latih turun dari 92 persen menjadi 5,6 persen, dan pemeriksaan manual kami menunjukkan 6 dari 18 pasangan tandan sama terpisah di split resmi, tetapi nol di split blok. Angka 20 dipilih agar kelas terkecil, Busuk dengan 411 foto, tetap punya sekitar dua puluh blok untuk dibagi 70/15/15. Kami akui kemiripan antarsesi masih ada, jadi split blok mengurangi, belum menghapus sepenuhnya."

**T8. "Empat puluh pasangan untuk cek manual, apakah cukup?"**

"Sampelnya memang kecil; selang kepercayaan 95 persennya 44 sampai 77 persen. Tapi cek manual ini bukan satu-satunya bukti. Ia memperkuat analisis statistik pada seluruh 4.722 pasangan berurutan, yang menunjukkan 50 persen sangat mirip padahal harapannya hanya 5 persen. Kami juga bukan ahli sawit, dan itu kami tulis sebagai keterbatasan."

**T9. "Apakah boleh memakai data ini? Bagaimana izinnya?"**

"Lisensinya Creative Commons Attribution 4.0: boleh dipakai dan dibagikan dengan mencantumkan sumber. Atribusinya kami cantumkan di proposal, slide, dan aplikasi. Datanya tidak berisi wajah atau data pribadi."

**T10. "Kenapa fotonya cuma 256 piksel? Bukankah itu kecil?"**

"Penyusun dataset sudah mengecilkannya ke 256×256. Untuk model kami cukup, karena masukannya 224×224, ukuran standar model pra-latih ImageNet. Untungnya, semua foto berukuran sama, jadi model tidak bisa mengambil jalan pintas dari perbedaan ukuran."

### 4.3 Metode (penjawab: Steven)

**⚠️ T11. "Bagaimana kalau CORN ternyata tidak lebih baik?"**

"Pada hasil awal kami, memang begitu: CORN setara atau sedikit di bawah cross-entropy, macro-F1 0,905 lawan 0,914, dan MAE 0,121 lawan 0,111, dari tiga seed. Dugaan kami, cross-entropy sudah jarang meleset jauh, sekitar 98 persen prediksinya paling banyak meleset satu tingkat, sehingga ruang perbaikan untuk CORN kecil. Itu tetap hasil yang sah: panduan menyebut hasil negatif dapat dinilai baik bila eksperimennya valid dan penyebabnya dianalisis. Kriteria suksesnya sudah kami tulis sebelum melatih, jadi kami tidak menggeser target setelah melihat hasil."

**⚠️ T12. "Kenapa klasifikasi, bukan deteksi seperti YOLO?"**

"Pertanyaan pengguna kami adalah 'tandan ini tingkat berapa?', dan setiap foto di dataset berisi satu tandan utama dengan satu label. Deteksi butuh kotak pembatas per tandan, yang tidak tersedia di dataset ini. Deteksi banyak tandan, misalnya di tumpukan pabrik, kami catat sebagai pengembangan lanjutan."

**T13. "Kenapa EfficientNet-B0, bukan model yang lebih besar seperti ViT?"**

"Ada tiga alasan: ringan, sekitar 4 juta parameter, sehingga muat di GPU gratis dan bisa berjalan di CPU untuk demo; sudah terbukti untuk *transfer learning*; dan fokus kami adalah membandingkan dua cara menghitung kesalahan secara adil, bukan mencari arsitektur terbesar. Backbone yang sama untuk keduanya membuat perbandingannya bersih."

**T14. "Kenapa augmentasi warna tidak dipakai? Bukankah biasanya membantu?"**

"Karena warna kulit buah adalah isyarat kematangan itu sendiri. Kalau warnanya diacak, kami khawatir model kehilangan isyarat utamanya. Tapi itu baru dugaan, jadi kami mengujinya sebagai eksperimen E4, bukan memutuskannya sepihak."

**T15. "Kenapa macro-F1, bukan akurasi?"**

"Karena kelasnya tidak seimbang: Busuk hanya 411 foto, Matang Penuh 1.489. Akurasi bisa tinggi walau kelas kecil sering salah. Macro-F1 memberi bobot sama untuk setiap kelas. Kami tetap melaporkan akurasi sebagai pelengkap, ditambah MAE dan kesalahan berat untuk jarak kesalahan."

**T16. "Bagaimana memastikan model melihat buahnya, bukan latarnya?"**

"Kami memakai Grad-CAM, peta panas yang menunjukkan bagian foto yang paling memengaruhi keputusan. Pada analisis kesalahan, kami akan memeriksa apakah model fokus pada tandan atau pada latar seperti tanah atau sepatu."

### 4.4 Rencana dan tim (penjawab: Yedija)

**T17. "Bagaimana pembagian kerja kalian?"**

"Saya ketua proyek, sekaligus dokumentasi dan demo. Juanito memegang data dan audit, Steven memegang model dan eksperimen. Peran ini bisa diputar setelah UTS, dan setiap minggu masing-masing mengisi logbook dengan bukti yang bisa dibuka."

**T18. "Apakah waktunya cukup?"**

"Bagian yang paling tidak pasti sudah selesai: data sudah diaudit dan 18 model sudah dilatih di Colab. Sisanya analisis kesalahan, demo, dan laporan, yang semuanya bisa dikerjakan di CPU laptop."

## 5. Angka yang wajib dihafal

Semua anggota, bukan hanya yang membawakan slide tersebut.

| Angka | Arti | Sumber |
|---|---|---|
| 16,83 juta ha | luas kebun sawit Indonesia | Outlook Kelapa Sawit 2024 |
| > 55% | pangsa Indonesia di ekspor minyak sawit dunia | Outlook Kelapa Sawit 2024 |
| 34% | produksi dari kebun rakyat (rata-rata 2015–2024) | Outlook Kelapa Sawit 2024 |
| 17,6% | kontribusi Kalimantan Tengah | Outlook Kelapa Sawit 2024 |
| 8.430 kg · 156 kg · Rp249.600 | contoh satu truk: berat, potongan, kerugian | Woittiez dkk. 2016 |
| 4.728 | jumlah foto dataset | Kamal dkk. 2024 |
| 758 / 1.405 / 1.489 / 665 / 411 | jumlah foto per tingkat (Mentah → Busuk) | Kamal dkk. 2024 |
| 92% → 8,3% | foto uji bertetangga dengan data latih: split resmi → split blok | audit kami |
| 62% (IK 95%: 44–77%) | pasangan berurutan yang adalah tandan sama | label manual kami |
| 3.434 / 658 / 636 | latih / validasi / uji split blok | audit kami (split beku) |
| 0,681 vs 0,657 | macro-F1 baseline warna, split resmi vs split blok | baseline E1 kami |
| 0,914 · 0,905 | macro-F1 CNN + CE · CNN + CORN (split blok, 3 seed) | hasil awal E2, E3 |
| 12,3 ms | latensi model per foto di CPU laptop | benchmark kami |
| ±4 juta · ±16 MB | parameter · ukuran bobot EfficientNet-B0 | konfigurasi kami |
| < 200 ms | target latensi per foto di CPU | kriteria sukses |
