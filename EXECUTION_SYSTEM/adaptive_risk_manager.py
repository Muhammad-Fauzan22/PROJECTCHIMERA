# -*- coding: utf-8 -*-
# ==============================================================================
# ==             MANAJER RISIKO ADAPTIF - PROJECT CHIMERA GENESIS             ==
# ==============================================================================
#
# Lokasi: EXECUTION_SYSTEM/adaptive_risk_manager.py
# Deskripsi: Modul ini adalah jantung dari manajemen risiko eksekusi. Ia
#            bertanggung jawab untuk menghitung ukuran posisi (position sizing)
#            berdasarkan sinyal trading dan profil risiko yang telah ditentukan.
#            Tujuannya adalah untuk memastikan setiap trade memiliki risiko
#            yang terukur dan terkendali.
#
# ==============================================================================

# --- Import Library Standar ---
import logging

# Konfigurasi logging dasar untuk modul ini
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')


class AdaptiveRiskManager:
    """
    Kelas yang menghitung parameter trade (ukuran posisi, stop loss)
    berdasarkan aturan manajemen risiko.
    """

    def __init__(self, orchestrator):
        """
        Konstruktor untuk AdaptiveRiskManager.

        Args:
            orchestrator (ChimeraOrchestrator): Instance dari orkestrator utama.
        """
        logging.info("Inisialisasi Adaptive Risk Manager...")

        # Menyimpan referensi ke konfigurasi dan profil risiko.
        # Ini memungkinkan manajer risiko untuk mengakses semua parameter
        # yang dibutuhkan untuk kalkulasi.
        self.risk_profile = orchestrator.risk_profile
        self.config = orchestrator.config

        logging.info(">>> Adaptive Risk Manager berhasil diinisialisasi.")


    def calculate_position_size(self, trading_signal: dict, current_price: float, symbol: str = "BTC/IDR") -> dict | None:
        """
        Menghitung ukuran posisi yang tepat berdasarkan sinyal dan profil risiko.

        Args:
            trading_signal (dict): Dictionary sinyal dari Strategic Cortex.
            current_price (float): Harga pasar aset saat ini.
            symbol (str): Simbol aset yang akan diperdagangkan.

        Returns:
            dict | None: Sebuah dictionary "Trade Order" jika sinyalnya adalah
                         BUY atau SELL, atau None jika sinyalnya HOLD.
        """
        # Langkah 1: Periksa sinyal. Jika 'HOLD', tidak ada tindakan yang perlu diambil.
        if trading_signal['signal'] == 'HOLD':
            logging.info("Sinyal adalah 'HOLD'. Tidak ada order yang dihitung.")
            return None

        logging.info(f"Menghitung ukuran posisi untuk sinyal '{trading_signal['signal']}' pada harga {current_price:,.2f} IDR.")

        # Langkah 2: Ekstrak parameter risiko dari profil yang dimuat.
        capital_mgmt = self.risk_profile['capital_management']
        loss_ctrl = self.risk_profile['loss_control']

        initial_capital = capital_mgmt['initial_capital']
        risk_per_trade_pct = capital_mgmt['risk_per_trade']
        stop_loss_pct = loss_ctrl['static_stop_loss_pct'] # Menggunakan SL statis sesuai permintaan

        # Langkah 3: Hitung jumlah risiko absolut dalam Rupiah.
        # Ini adalah jumlah uang maksimal yang boleh hilang jika trade ini gagal.
        risk_amount_idr = initial_capital * (risk_per_trade_pct / 100.0)

        # Langkah 4: Hitung jarak ke stop loss dalam satuan harga.
        # Ini adalah seberapa jauh harga harus bergerak melawan kita sebelum posisi ditutup.
        stop_loss_distance = current_price * (stop_loss_pct / 100.0)

        # --- Pemeriksaan Keamanan ---
        # Mencegah error fatal jika stop_loss_distance adalah nol.
        if stop_loss_distance <= 0:
            logging.error("Jarak Stop Loss adalah nol atau negatif. Tidak dapat menghitung ukuran posisi. Periksa 'static_stop_loss_pct' di risk_profile.toml.")
            return None

        # Langkah 5: Hitung ukuran posisi dalam unit aset (misalnya, dalam BTC).
        # Formula: (Jumlah Risiko) / (Risiko per Unit Aset)
        position_size = risk_amount_idr / stop_loss_distance

        # Langkah 6: Tentukan harga stop loss absolut.
        side = trading_signal['signal'].lower() # 'buy' atau 'sell'
        if side == 'buy':
            stop_loss_price = current_price - stop_loss_distance
        else: # 'sell'
            stop_loss_price = current_price + stop_loss_distance

        # Langkah 7: Catat semua hasil perhitungan untuk transparansi dan audit.
        logging.info(f"  - Modal Awal: {initial_capital:,.2f} IDR")
        logging.info(f"  - Risiko per Trade: {risk_per_trade_pct}% ({risk_amount_idr:,.2f} IDR)")
        logging.info(f"  - Jarak Stop Loss: {stop_loss_pct}% ({stop_loss_distance:,.2f} IDR)")
        logging.info(f"  -> UKURAN POSISI DIHITUNG: {position_size:.8f} {symbol.split('/')[0]}")
        logging.info(f"  -> HARGA STOP LOSS: {stop_loss_price:,.2f} IDR")

        # Langkah 8: Buat "Trade Order" yang siap dieksekusi.
        # Ini adalah Data Transfer Object (DTO) yang akan dikirim ke komponen eksekusi.
        trade_order = {
            'symbol': symbol,
            'type': 'market',  # Tipe order (bisa juga 'limit')
            'side': side,      # 'buy' atau 'sell'
            'amount': position_size,
            'price': current_price,
            'stop_loss_price': stop_loss_price,
            'signal_details': trading_signal # Menyertakan detail sinyal asli untuk logging
        }

        return trade_order