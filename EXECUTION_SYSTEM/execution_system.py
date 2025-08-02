# -*- coding: utf-8 -*-
# ==============================================================================
# ==             SISTEM EKSEKUSI SADAR-KONEKSI - PROJECT CHIMERA              ==
# ==============================================================================
#
# Lokasi: EXECUTION_SYSTEM/execution_system.py
# Deskripsi: Versi yang sadar akan status koneksi. Menonaktifkan trading
#            jika tidak terhubung ke bursa.
#
# ==============================================================================

import logging
from .platform_integrations.binance_toolkit import BinanceToolkit

class ExecutionSystem:
    """
    Menerima sinyal dan mengubahnya menjadi aksi trading jika koneksi memungkinkan.
    """
    def __init__(self, orchestrator):
        logging.info("Inisialisasi Sistem Eksekusi (Sadar-Koneksi)...")
        self.orchestrator = orchestrator
        
        self.binance_toolkit = BinanceToolkit(self.orchestrator)
        
        if self.binance_toolkit.is_connected:
            logging.info(">>> Sistem Eksekusi dalam mode 'TRADING AKTIF'.")
        else:
            logging.warning(">>> Sistem Eksekusi dalam mode 'TRADING NONAKTIF' karena tidak ada koneksi ke bursa.")

    def process_signal(self, signal):
        """
        Memproses sinyal trading hanya jika terhubung ke bursa.
        """
        # Pemeriksaan status koneksi sebelum melakukan apapun
        if not self.binance_toolkit.is_connected:
            logging.info("Sinyal diterima, tetapi eksekusi dilewati karena tidak ada koneksi ke Binance.")
            return

        logging.info(f"Sistem Eksekusi menerima sinyal: {signal}")
        
        if signal and signal.get('signal') != 'HOLD' and signal.get('confidence', 0) > 0.75:
            logging.info("Sinyal valid, mempersiapkan eksekusi...")
            # Di masa depan, logika trading akan ada di sini
            self.binance_toolkit.get_account_balance() # Contoh aksi
        else:
            logging.info("Sinyal tidak memenuhi syarat untuk eksekusi.")