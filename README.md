# Sinta Scraper

Script Python ini digunakan untuk men-scrape dan mengambil data otomatis dari sistem SINTA (https://sinta.kemdiktisaintek.go.id/).

## Data yang Diambil
Script ini mengekstrak riwayat publikasi beserta metriknya dari profil penulis yang ditentukan (melalui file `author_ids.xlsx`). Secara spesifik, data yang diambil untuk setiap publikasi/item meliputi:
- **AuthorID** dan **AuthorName**: Identitas penulis di profil SINTA.
- **Tab/Kategori**: Kategori/sumber publikasi (misalnya: Scopus, Garuda, Google Scholar, dll.).
- **Title**: Judul publikasi atau artikel.
- **Link**: Tautan URL menuju halaman asal atau detail publikasi.
- **Meta**: Informasi metadata publikasi (nama jurnal, penerbit, volume, dll.).
- **Year**: Tahun publikasi.
- **Cited**: Jumlah sitasi atau kutipan yang diterima.
- **Quartile**: Peringkat kuartil jurnal/publikasi (misalnya Q1, Q2, Q3, Q4, dll.).

## Persiapan dan Kredensial
Sebelum menjalankan script ini, Anda **wajib** mengisi data kredensial login SINTA Anda yang berada di dalam file `sinta_scraper.py`. Buka file tersebut dan ubah bagian berikut:

```python
# Kredensial login
USERNAME = "[EMAIL_ADDRESS]"
PASSWORD = "[PASSWORD]"
```

Selain itu, pastikan Anda telah menyediakan file `author_ids.xlsx` di direktori yang sama, yang memiliki kolom `AuthorID` berisi daftar nomor ID penulis yang ingin ditarik datanya.

## Cara Menjalankan
1. Pastikan Anda telah menginstal seluruh library yang dibutuhkan (seperti `selenium`, `pandas`, `webdriver-manager`).
2. Isi kredensial login pada `sinta_scraper.py` sesuai instruksi di atas.
3. Eksekusi script menggunakan terminal/CMD: `python sinta_scraper.py`.
4. Hasil akhir scrape akan otomatis tersimpan dalam format `.csv` dan `.xlsx`.
