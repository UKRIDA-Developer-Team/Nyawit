# Hasil cek manual pasangan bernomor berurutan

Pasangan dilabeli: 40 dari 40 (acak, seed tetap). **Ya (tandan sama): 18**, tidak: 11, ragu: 11.

- Di antara pasangan yang dapat diputuskan: **62%** tandan sama (18/29; IK 95% Wilson 44–77%).
- Batas bawah (ragu dihitung "tidak"): 45% (IK 95% 31–60%).
- Dari 18 pasangan tandan sama, yang **terpisah antara train dan val/test**: **6 pada split resmi**, **0 pada split blok**.

Kesimpulan: foto bernomor berurutan sering merupakan tandan fisik yang sama. Split resmi (acak) memisahkan sebagian pasangan tersebut ke train dan val/test, sedangkan split blok menjaganya tetap dalam satu split. Ini mengonfirmasi secara manual temuan statistik pada audit.

Catatan: sampel kecil (40 pasangan) dan dilabeli oleh tim (bukan ahli sawit); banyaknya label "ragu" berasal dari foto gelap/terang, tertutup tangan, atau terlalu dekat (lihat kolom `catatan`).
