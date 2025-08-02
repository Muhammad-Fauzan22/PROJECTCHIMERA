# -*- coding: utf-8 -*-
# ==============================================================================
# ==               KOMPRESOR DATA FRAKTAL - PROJECT CHIMERA GENESIS           ==
# ==============================================================================
#
# Lokasi: PERCEPTION_SYSTEM/market_scanner/fractal_compressor.py
# Deskripsi: Modul ini bertanggung jawab untuk melakukan kompresi lossy
#            pada data time-series (seperti harga) menggunakan dekomposisi
#            wavelet. Tujuannya adalah untuk mengurangi kebutuhan penyimpanan
#            data historis dengan tetap mempertahankan fitur-fitur penting
#            dari pergerakan harga.
#
# ==============================================================================

# --- Import Library ---
# Pastikan library berikut sudah terinstal:
# pip install numpy PyWavelets
import numpy as np
import pywt


class FractalCompressor:
    """
    Kelas untuk mengompres data time-series menggunakan Transformasi Wavelet.
    Ini bekerja dengan mengubah sinyal ke domain frekuensi, menghilangkan
    koefisien yang kurang penting (noise), dan merekonstruksi sinyal kembali.
    """

    def __init__(self, config: dict):
        """
        Konstruktor untuk FractalCompressor.

        Args:
            config (dict): Objek konfigurasi yang dimuat dari chimera_config.toml,
                           diteruskan oleh Orkestrator.
        """
        # Mengambil rasio kompresi dari konfigurasi. Nilai ini menentukan
        # seberapa agresif kompresi akan dilakukan.
        self.compression_ratio = config['data']['compression_ratio']
        self.wavelet_type = 'db4'  # Daubechies 4: Pilihan umum dengan keseimbangan yang baik.

        print(f"FractalCompressor diinisialisasi dengan rasio kompresi: {self.compression_ratio}%")
        print(f"Menggunakan wavelet tipe: '{self.wavelet_type}'")


    def _get_decomposition_level(self, data_length: int) -> int:
        """
        Fungsi helper untuk menentukan level dekomposisi wavelet yang optimal
        berdasarkan panjang data input.

        Args:
            data_length (int): Jumlah titik data dalam sinyal.

        Returns:
            int: Level dekomposisi maksimal yang diizinkan.
        """
        # Menggunakan fungsi bawaan dari pywt untuk menghitung level maksimal
        # yang dimungkinkan untuk panjang data dan tipe wavelet yang diberikan.
        w = pywt.Wavelet(self.wavelet_type)
        return pywt.dwt_max_level(data_length, w.dec_len)


    def compress(self, data: np.ndarray) -> np.ndarray:
        """
        Mengompres data harga yang diberikan sesuai dengan compression_ratio.

        Args:
            data (np.ndarray): Array 1D NumPy berisi data harga.

        Returns:
            np.ndarray: Array 1D NumPy berisi data yang telah terkompresi
                        dan direkonstruksi.
        """
        if not isinstance(data, np.ndarray):
            data = np.array(data)

        data_length = len(data)
        if data_length < 10: # Data terlalu pendek untuk dikompresi secara efektif
            return data

        # 1. DEKOMPOSISI: Memecah sinyal menjadi koefisien aproksimasi dan detail
        #    pada berbagai level frekuensi.
        level = self._get_decomposition_level(data_length)
        if level == 0: # Tidak bisa didekomposisi lebih lanjut
            return data
            
        coeffs = pywt.wavedec(data, self.wavelet_type, level=level)

        # 2. KALKULASI THRESHOLD: Menentukan nilai ambang batas untuk membuang
        #    koefisien yang tidak penting.
        #    Kita akan membuang persentase koefisien terkecil sesuai compression_ratio.
        all_coeffs_flat = np.concatenate(coeffs)
        num_coeffs_to_keep = int(len(all_coeffs_flat) * (1 - self.compression_ratio / 100.0))
        
        # Jika rasio 100%, semua koefisien dibuang kecuali satu yang paling penting
        if num_coeffs_to_keep <= 0:
            num_coeffs_to_keep = 1

        # Temukan nilai absolut dari koefisien ke-N terbesar.
        # Semua koefisien dengan nilai absolut di bawah ini akan dianggap noise.
        abs_coeffs = np.abs(all_coeffs_flat)
        threshold = np.sort(abs_coeffs)[-num_coeffs_to_keep]

        # 3. THRESHOLDING: Menerapkan ambang batas. Koefisien di bawah ambang
        #    dijadikan nol.
        thresholded_coeffs = [pywt.threshold(c, threshold, mode='hard') for c in coeffs]

        # 4. REKONSTRUKSI: Membangun kembali sinyal dari koefisien yang
        #    telah "dibersihkan".
        compressed_data = pywt.waverec(thresholded_coeffs, self.wavelet_type)

        # Memastikan panjang data output sama dengan input karena proses
        # padding wavelet terkadang bisa sedikit berbeda.
        return compressed_data[:data_length]