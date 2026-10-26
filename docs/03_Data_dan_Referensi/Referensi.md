# Referensi dan Ringkasan Relevansi (CP02)

Panduan mensyaratkan minimal 5 sumber kredibel, termasuk minimal 2 paper metode atau dataset yang relevan. Kolom **Status baca** wajib diperbarui oleh anggota yang membaca. Jangan mengutip isi yang belum dibaca penuh.

| # | Rujukan | Jenis | Ringkasan relevansi | Dipakai di | Status baca |
|---|---|---|---|---|---|
| 1 | Kamal dkk. (2024), Mendeley Data | **Dataset** | Dataset utama: 4.728 foto TBS, 5 tingkat ordinal, split stratified; deskripsinya menyarankan regresi ordinal dan *weighted loss* | seluruh proyek | halaman dataset dibaca; isi arsip diverifikasi |
| 2 | Shi, Cao & Raschka (2023), *Pattern Anal. Appl.* | **Paper metode** | CORN: K−1 tugas biner bersyarat, konsisten peringkat, tanpa batasan bobot seperti CORAL | metode utama E3 | [isi] |
| 3 | Cao, Mirjalili & Raschka (2020), *Pattern Recognit. Lett.* | **Paper metode** | CORAL: K−1 tugas biner dengan bobot bersama dan bias berbeda; dasar teori konsistensi peringkat | tinjauan pustaka | [isi] |
| 4 | Tan & Le (2019), *ICML* | **Paper metode** | EfficientNet: *compound scaling*; B0 = 5,3 juta parameter dengan akurasi ImageNet yang baik | backbone | [isi] |
| 5 | Suharjito dkk. (2021), *Comput. Electron. Agric.* | Paper aplikasi | Klasifikasi kematangan TBS di perangkat seluler dengan CNN ringan | pembanding pendekatan; batas efisiensi | [isi – periksa apakah memakai CE nominal] |
| 6 | Suharjito dkk. (2023), *Scientific Data* | Dataset | Tumpukan TBS di pabrik (domain berbeda) | batas klaim, ide uji lintas domain | [isi] |
| 7 | Omar dkk. (2024), *Data in Brief* | Dataset | Dataset kematangan sawit luar ruangan | ide uji lintas dataset | [isi] |
| 8 | Selvaraju dkk. (2017), *ICCV* | Paper metode | Grad-CAM: peta panas berbasis gradien | analisis kesalahan, demo | [isi] |
| 9 | Kaufman dkk. (2012), *ACM TKDD* | Paper metodologi | Definisi dan taksonomi kebocoran data | audit near-duplicate | [isi] |
| 10 | Kapoor & Narayanan (2023), *Patterns* | Paper metodologi | Kebocoran sebagai penyebab hasil ML yang tidak dapat direproduksi | justifikasi P2 | [isi] |
| 11 | Cohen (1968), *Psychological Bulletin* | Paper metrik | *Weighted kappa*: kesepakatan dengan bobot jarak kategori | metrik QWK | [isi] |

## Daftar pustaka (APA 7)

1. Kamal, I. M., Mochammad, S., Nurahmi, L., Natawijaya, A., & Kalili, M. (2024). *An ordinal dataset for ripeness level classification in oil palm fruit quality grading* (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/424y96m6sw.1
2. Shi, X., Cao, W., & Raschka, S. (2023). Deep neural networks for rank-consistent ordinal regression based on conditional probabilities. *Pattern Analysis and Applications, 26*(3), 941–955. https://doi.org/10.1007/s10044-023-01181-9
3. Cao, W., Mirjalili, V., & Raschka, S. (2020). Rank consistent ordinal regression for neural networks with application to age estimation. *Pattern Recognition Letters, 140*, 325–331. https://doi.org/10.1016/j.patrec.2020.11.008
4. Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. In *Proceedings of the 36th International Conference on Machine Learning* (PMLR 97, pp. 6105–6114).
5. Suharjito, Elwirehardja, G. N., & Prayoga, J. S. (2021). Oil palm fresh fruit bunch ripeness classification on mobile devices using deep learning approaches. *Computers and Electronics in Agriculture, 188*, 106359. https://doi.org/10.1016/j.compag.2021.106359
6. Suharjito, Junior, F. A., Koeswandy, Y. P., Debi, Nurhayati, P. W., Asrol, M., & Marimin. (2023). Annotated datasets of oil palm fruit bunch piles for ripeness grading using deep learning. *Scientific Data, 10*, 72. https://doi.org/10.1038/s41597-023-01958-x
7. Omar, Z., Abdul Majeed, A. P. P., Rosbi, M., Ghazalli, S. A., & Selamat, H. (2024). Outdoor oil palm fruit ripeness dataset. *Data in Brief, 55*, 110667. https://doi.org/10.1016/j.dib.2024.110667
8. Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. In *2017 IEEE International Conference on Computer Vision (ICCV)* (pp. 618–626). https://doi.org/10.1109/ICCV.2017.74
9. Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining. *ACM Transactions on Knowledge Discovery from Data, 6*(4), 1–21. https://doi.org/10.1145/2382577.2382579
10. Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), 100804. https://doi.org/10.1016/j.patter.2023.100804
11. Cohen, J. (1968). Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit. *Psychological Bulletin, 70*(4), 213–220. https://doi.org/10.1037/h0026256

## Perangkat lunak yang digunakan

PyTorch & torchvision (BSD-3-Clause; bobot pra-latih ImageNet dari torchvision), scikit-learn (BSD-3-Clause), pandas (BSD-3-Clause), NumPy (BSD-3-Clause), Matplotlib (lisensi PSF-based Matplotlib), Pillow (MIT-CMU/HPND), Gradio (Apache-2.0), PyYAML (MIT). Implementasi CORN ditulis ulang dari deskripsi makalah [2] dan dicocokkan dengan perilaku pustaka rujukan `coral-pytorch` (MIT) tanpa menyalin kodenya.
