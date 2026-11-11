# Gempa Bumi Dunia dengan Flask

Aplikasi visualisasi data gempa menggunakan Flask, Pandas, Leaflet, dan Chart.js. Dataset `all_month.csv` disimpan satu folder dengan `app.py`.

## Menjalankan di macOS

Buka Terminal pada folder `gempabumi_flask`, lalu jalankan:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Buka `http://127.0.0.1:5000` di browser. Biarkan terminal tetap terbuka saat aplikasi digunakan. Tekan `Control+C` di terminal untuk menghentikan server.

Peta dan grafik memuat pustaka serta peta dasar dari internet, jadi koneksi internet diperlukan.
