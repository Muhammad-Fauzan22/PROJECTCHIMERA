# PROJECT CHIMERA

**Sistem Robot Trading AI Skala Besar Berbasis Multi-AI & Quantum Sentience**

---

## Deskripsi Proyek

Project Chimera adalah sistem robot trading AI canggih yang dirancang untuk beroperasi secara mandiri 24/7 di pasar kripto yang dinamis. Ia menggabungkan kekuatan beberapa AI (Gemini Pro, DeepSeek, Claude Sonnet 4, GPT-4o) dalam arsitektur multi-agent untuk mengambil keputusan trading yang sangat cerdas dan adaptif.

---

## Arsitektur

Struktur proyek ini mengikuti arsitektur modular multi-layer:

- **`AGENTS/`**: Rumah bagi agen-agen cerdas spesifik (ALPHA_AGENT, dll.).
- **`AI_BRAIN/`**: Modul inti AI yang mengelola dan merutekan permintaan ke model AI eksternal.
- **`COLLECTIVE_MEMORY/`**: Sistem penyimpanan dan sinkronisasi data ke Google Drive.
- **`CONTROL_PANEL/`**: Pusat kendali dan konfigurasi sistem.
- **`DATA_INGESTION_ENGINE/`**: Mesin untuk menelan dan memproses data mentah dari berbagai sumber.
- **`EXECUTION_SYSTEM/`**: Sistem yang bertanggung jawab atas eksekusi perdagangan dan manajemen risiko.
- **`GLOBAL_ANALYZER/`**: Modul analisis data on-chain dan pasar yang mendalam.
- **`PERCEPTION_SYSTEM/`**: Sistem sensor yang mengumpulkan data dari berbagai sumber intelijen.
- **`RESILIENCE_SYSTEM/`**: Komponen untuk menjaga sistem tetap berjalan dan pulih dari kegagalan.
- **`SENTIENT_CORE/`**: Inti sistem yang mengatur siklus kognitif utama.
- **`STRATEGIC_CORTEX/`**: Otak strategis yang menganalisis data dan membuat keputusan.
- **`WEB_SCRAPERS/`**: Modul untuk mengumpulkan data dari web secara cerdas dan adaptif.

---

## Panduan Penggunaan

1. **Persiapan Lingkungan**
   - Pastikan Python 3.9+ terinstal.
   - Buat lingkungan virtual: `python -m venv .venv`
   - Aktifkan lingkungan virtual: `.venv\Scripts\Activate.ps1` (Windows) atau `source .venv/bin/activate` (Linux/Mac).
   - Instal dependensi: `pip install -r requirements.txt`
   - Konfigurasikan file `CONTROL_PANEL/CONFIG/secrets.vault` dengan kunci API Anda.

2. **Menjalankan Sistem**
   - Jalankan orkestrator utama: `python -m SENTIENT_CORE.chimera_orchestrator`

3. **Pengembangan**
   - Kode ini dirancang untuk dikembangkan lebih lanjut. Setiap komponen modular dan dapat diperluas.

---
