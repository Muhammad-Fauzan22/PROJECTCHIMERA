# -*- coding: utf-8 -*-
# ==============================================================================
# == RISK MANAGEMENT AGENT - PROJECT CHIMERA ==
# ==============================================================================
# Lokasi: EXECUTION_SYSTEM/risk_management_agent.py
# Deskripsi: Modul ini bertanggung jawab untuk menganalisis sinyal trading
#            yang kompleks dari DataSynthesizer, mengelola risiko, dan
#            menghasilkan command eksekusi yang aman dan optimal.
# ==============================================================================

import logging
import sys
import os

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik satu level untuk mendapatkan direktori root proyek (PROJECTCHIMERA)
project_root = os.path.dirname(current_script_dir)
# Naik satu level lagi karena EXECUTION_SYSTEM ada di dalam root
project_root = os.path.dirname(project_root)
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, project_root)
# --- AKHIR PENYESUAIAN PATH ---

# Impor konfigurasi untuk profil risiko
try:
    import toml
    from CONTROL_PANEL.CONFIG import risk_profile
    CONFIG_PATH = os.path.join(project_root, 'CONTROL_PANEL', 'CONFIG')
    RISK_PROFILE_PATH = os.path.join(CONFIG_PATH, 'risk_profile.toml')
    
    # Memuat konfigurasi risiko
    with open(RISK_PROFILE_PATH, 'r', encoding='utf-8') as f:
        RISK_CONFIG = toml.load(f)
    logging.info("Konfigurasi risiko berhasil dimuat.")
except Exception as e:
    logging.error(f"Gagal memuat konfigurasi risiko: {e}")
    RISK_CONFIG = {} # Fallback ke dictionary kosong jika gagal

class RiskManagementAgent:
    """
    Agen cerdas untuk manajemen risiko dan pengambilan keputusan eksekusi.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi RiskManagementAgent.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke sistem lain.
        """
        self.orchestrator = orchestrator
        self.risk_config = RISK_CONFIG
        logging.info("RiskManagementAgent diinisialisasi.")

    def analyze_smart_signal(self, smart_signal: dict, portfolio_status: dict):
        """
        Menganalisis sinyal cerdas dari DataSynthesizer dan membuat keputusan eksekusi.

        Args:
            smart_signal (dict): Sinyal kompleks dari DataSynthesizer.
                Contoh: {
                    'signal': 'BULLISH',
                    'confidence': 0.85,
                    'recommended_long': ['BTC/USDT', 'ETH/USDT'],
                    'recommended_short': ['SOL/USDT'],
                    'summary_risks': 'Volatilitas tinggi terdeteksi di pasar crypto...',
                    'market_context': 'Bull run 50-day MA'
                }
            portfolio_status (dict): Status portofolio saat ini (saldo, posisi terbuka, dll).

        Returns:
            dict: Perintah eksekusi yang telah disetujui dan disempurnakan, atau None jika tidak ada aksi.
                Contoh: {
                    'action': 'EXECUTE',
                    'symbol': 'BTC/USDT',
                    'side': 'BUY',
                    'confidence': 0.85,
                    'position_size_idr': 150000,
                    'risk_adjusted': True
                }
        """
        if not isinstance(smart_signal, dict) or not isinstance(portfolio_status, dict):
            logging.warning("Input tidak valid untuk analyze_smart_signal.")
            return None

        signal_type = smart_signal.get('signal')
        confidence = smart_signal.get('confidence', 0)
        recommended_longs = smart_signal.get('recommended_long', [])
        recommended_shorts = smart_signal.get('recommended_short', [])
        summary_risks = smart_signal.get('summary_risks', '')
        
        logging.info(f"Menganalisis sinyal: {signal_type} dengan confidence {confidence}")

        # --- Validasi awal ---
        if signal_type not in ['BULLISH', 'BEARISH'] or confidence <= 0.5:
            logging.info("Sinyal tidak kuat atau tidak valid. Tidak ada aksi.")
            return None

        # --- 1. Pilih aset berdasarkan sinyal ---
        selected_symbol = None
        trade_side = None
        if signal_type == 'BULLISH' and recommended_longs:
            selected_symbol = recommended_longs[0] # Pilih aset pertama
            trade_side = 'BUY'
            logging.debug(f"Aset long dipilih: {selected_symbol}")
        elif signal_type == 'BEARISH' and recommended_shorts:
            selected_symbol = recommended_shorts[0] # Pilih aset pertama
            trade_side = 'SELL'
            logging.debug(f"Aset short dipilih: {selected_symbol}")
        else:
            logging.info("Tidak ada rekomendasi aset yang sesuai dengan sinyal.")
            return None

        # --- 2. Hitung ukuran posisi dasar ---
        # Asumsi: Kita menggunakan konfigurasi risiko untuk menentukan ukuran posisi
        base_position_percentage = self.risk_config.get('position_sizing', {}).get('base_percentage_per_trade', 1.0) # Default 1%
        account_balance_idr = portfolio_status.get('free_balance_idr', 0)
        base_position_size_idr = account_balance_idr * (base_position_percentage / 100.0)
        
        logging.debug(f"Ukuran posisi dasar: Rp {base_position_size_idr:,.2f} ({base_position_percentage}% dari saldo)")

        # --- 3. Terapkan logika penyesuaian berdasarkan risiko ---
        adjusted_position_size_idr = base_position_size_idr
        is_risk_adjusted = False
        
        # Logika: Kurangi ukuran posisi sebesar 20% jika kata 'Volatilitas tinggi' ada di summary_risks
        risk_keywords = ["Volatilitas tinggi", "High volatility", "Market uncertainty"]
        if any(keyword in summary_risks for keyword in risk_keywords):
            reduction_factor = 0.20
            adjusted_position_size_idr = base_position_size_idr * (1 - reduction_factor)
            is_risk_adjusted = True
            logging.info(f"Volatilitas tinggi terdeteksi. Mengurangi ukuran posisi sebesar {reduction_factor*100}%.")
        
        # Batas minimum ukuran posisi (misalnya, Rp 50,000)
        min_position_size_idr = self.risk_config.get('position_sizing', {}).get('minimum_position_value_idr', 50000)
        if adjusted_position_size_idr < min_position_size_idr:
            logging.warning(f"Ukuran posisi yang disesuaikan (Rp {adjusted_position_size_idr:,.2f}) di bawah minimum (Rp {min_position_size_idr:,.2f}). Tidak ada aksi.")
            return None

        # --- 4. Hasilkan execution_command ---
        execution_command = {
            'action': 'EXECUTE',
            'symbol': selected_symbol,
            'side': trade_side,
            'confidence': confidence,
            'position_size_idr': round(adjusted_position_size_idr, 2),
            'risk_adjusted': is_risk_adjusted,
            'reason': f"Sinyal {signal_type} dengan confidence {confidence}. Aset: {selected_symbol}."
        }
        
        logging.info(f"Perintah eksekusi disetujui: {execution_command}")
        return execution_command

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Konfigurasi logging dasar untuk debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Karena kelas ini membutuhkan orchestrator, kita tidak bisa menjalankannya secara mandiri
    # tanpa mocking atau instance sebenarnya. Ini hanya untuk memastikan tidak ada syntax error.
    print("risk_management_agent.py dimuat dengan sukses. Siap untuk diintegrasikan.")
