# -*- coding: utf-8 -*-
# ==============================================================================
# ==             EXECUTION AGENT (DEFINITIF v2) - PROJECT CHIMERA             ==
# ==============================================================================
#
# Lokasi: AGENTS/EXECUTION_AGENT/execution_agent.py
# Deskripsi: Agen ini bertindak sebagai 'tangan' dari organisme trading.
#            Tugasnya adalah menerima perintah eksekusi yang sudah final
#            dan melaksanakannya di bursa dengan presisi tinggi.
#
# ==============================================================================

import logging

# Mengimpor toolkit yang menjadi satu-satunya jembatan ke bursa
from EXECUTION_SYSTEM.platform_integrations.binance_toolkit import BinanceToolkit

class ExecutionAgent:
    """
    Agen yang bertanggung jawab untuk eksekusi perdagangan yang optimal.
    Menerima perintah yang sudah diverifikasi dan berinteraksi langsung
    dengan API bursa.
    """
    def __init__(self, orchestrator):
        """
        Inisialisasi dengan toolkit bursa yang relevan.
        """
        logging.info("Menginisialisasi Execution Agent...")
        self.orchestrator = orchestrator
        
        self.binance_toolkit = BinanceToolkit(orchestrator)
        
        logging.info(">>> Execution Agent siap menerima dan mengeksekusi perintah.")

    def execute_command(self, command: dict):
        """
        Mengeksekusi perintah perdagangan yang telah diverifikasi di Binance.
        Ini adalah fungsi inti dari Execution Agent.
        
        Args:
            command (dict): Perintah final dari Risk Management Agent.
        """
        if not command:
            logging.debug("Execution Agent tidak menerima perintah untuk dieksekusi.")
            return

        # --- Gerbang Keamanan 1: Cek Koneksi ---
        if not self.binance_toolkit.is_connected:
            logging.error(f"EKSEKUSI DIBATALKAN. Tidak terhubung ke Binance. Perintah: {command}")
            return

        logging.info(f"Execution Agent menerima perintah untuk dieksekusi: {command}")
        
        try:
            # --- Langkah 1: Ekstrak dan Terjemahkan Perintah ---
            asset = command['asset']
            action = command['action']  # 'BULLISH' atau 'BEARISH'
            size_rp = command['size_rp']
            
            side = 'buy' if action == 'BULLISH' else 'sell'
            
            # --- Langkah 2: Konversi Ukuran Posisi ---
            price = self.binance_toolkit.get_market_price(asset)
            
            if not price:
                logging.error(f"EKSEKUSI GAGAL. Gagal mendapatkan harga pasar untuk {asset}.")
                return
                
            quantity = size_rp / price
            
            # --- Langkah 3: Eksekusi Perintah ---
            logging.info(f"Mengirim order ke Binance: {side.upper()} {quantity:.8f} {asset} @ MARKET PRICE")
            
            order_result = self.binance_toolkit.place_order(
                symbol=asset,
                order_type='market',
                side=side,
                amount=quantity
            )
            
            if order_result:
                logging.info(f"EKSEKUSI BERHASIL. Order ID: {order_result.get('id')}")
            else:
                logging.error("EKSEKUSI GAGAL. Toolkit Binance tidak mengembalikan hasil order.")

        except Exception as e:
            logging.critical(f"Terjadi error tak terduga selama proses eksekusi: {e}", exc_info=True)