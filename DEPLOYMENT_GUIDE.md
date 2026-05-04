# Panduan Deployment Dashboard NPCC (Live 24/7)

Ikuti langkah-langkah di bawah ini untuk membuat dashboard Anda online dan berjalan otomatis setiap 12 jam menggunakan GitHub.

## Langkah 1: Persiapan di GitHub
1.  Buat akun di [GitHub.com](https://github.com) jika belum punya.
2.  Klik tombol **New** untuk membuat repositori baru.
3.  Beri nama repositori (misalnya: `npcc-dashboard`).
4.  Pilih **Public**, lalu klik **Create repository**.

## Langkah 2: Mengunggah Folder ke GitHub
Anda bisa menggunakan GitHub Desktop atau cara cepat via browser:
1.  Buka repositori yang baru Anda buat di browser.
2.  Klik **"uploading an existing file"**.
3.  **Seret dan lepas (Drag & Drop)** semua file dari folder `Website tenaga ahli` di laptop Anda ke jendela browser GitHub.
    *   *Pastikan folder `.github` juga terikut (jika tidak bisa diseret, buat folder manual di GitHub).*
4.  Tunggu proses upload selesai, lalu klik **Commit changes**.

## Langkah 3: Memberikan Izin ke GitHub Actions
Agar script scraper bisa menyimpan data ke repositori:
1.  Di halaman repositori GitHub, klik tab **Settings**.
2.  Di menu samping kiri, klik **Actions** > **General**.
3.  Scroll ke bawah ke bagian **Workflow permissions**.
4.  Pilih **Read and write permissions**.
5.  Klik **Save**.

## Langkah 4: Menyalakan Hosting (GitHub Pages)
1.  Masih di tab **Settings**, klik menu **Pages** di samping kiri.
2.  Pada bagian **Build and deployment**, pastikan Source adalah **Deploy from a branch**.
3.  Pilih Branch: `main` dan folder: `/ (root)`.
4.  Klik **Save**.
5.  Tunggu sekitar 1-2 menit. GitHub akan memberikan link (misalnya: `https://username.github.io/npcc-dashboard/`).

## Langkah 5: Tes Otomatisasi
1.  Klik tab **Actions** di bagian atas repositori.
2.  Klik workflow **Scrape Daily Data** di sebelah kiri.
3.  Klik tombol **Run workflow** > **Run workflow** untuk mencoba menjalankan scraper sekarang juga tanpa menunggu 12 jam.
4.  Jika berhasil (ikon centang hijau), file `live_data.json` di repositori Anda akan terupdate otomatis.

---
**Dashboard Anda sekarang sudah LIVE!** 
Setiap kali script berjalan, data di dashboard akan berubah sendiri tanpa Anda perlu menyalakan laptop.
