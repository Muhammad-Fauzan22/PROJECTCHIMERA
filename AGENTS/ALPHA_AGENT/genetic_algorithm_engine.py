# -*- coding: utf-8 -*-
# ==============================================================================
# == GENETIC ALGORITHM ENGINE - PROJECT CHIMERA ==
# ==============================================================================
# Lokasi: AGENTS/ALPHA_AGENT/genetic_algorithm_engine.py
# Deskripsi: Mesin evolusi untuk menyempurnakan strategi trading secara mandiri.
#            Ia mensimulasikan seleksi alam: memilih yang terbaik, mencampur
#            (crossover), mengubah sedikit (mutasi), dan mengganti yang lemah.
# ==============================================================================

import logging
import random
import copy
import sys
import os

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik dua level untuk mendapatkan direktori root proyek (PROJECTCHIMERA)
# AGENTS/ALPHA_AGENT/ -> PROJECTCHIMERA/
project_root = os.path.dirname(os.path.dirname(current_script_dir))
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, project_root)
# --- AKHIR PENYESUAIAN PATH ---

# Impor modul lain jika diperlukan di masa depan
# Untuk saat ini, tidak ada impor spesifik yang diperlukan dari proyek

class GeneticAlgorithmEngine:
    """
    Mesin yang menerapkan algoritma genetika untuk mengoptimalkan parameter strategi.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi GeneticAlgorithmEngine.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke sistem lain
                          atau konfigurasi jika diperlukan di masa depan.
        """
        self.orchestrator = orchestrator
        # Bisa memuat parameter GA dari config jika diperlukan, misal:
        # self.mutation_rate = self.orchestrator.config.get('ga', {}).get('mutation_rate', 0.1)
        self.mutation_rate = 0.1 # Rate mutasi default 10%
        logging.info("GeneticAlgorithmEngine diinisialisasi.")

    def evolve_strategies(self, strategy_pool: list):
        """
        Menjalankan satu siklus evolusi pada kumpulan strategi.

        Args:
            strategy_pool (list): Daftar dictionary parameter strategi.
                Contoh: [
                    {'rsi_period': 14, 'sma_fast': 50, 'sma_slow': 200, 'fitness': 1.2},
                    {'rsi_period': 10, 'sma_fast': 30, 'sma_slow': 150, 'fitness': 0.8},
                    ...
                ]

        Returns:
            list: Kumpulan strategi yang telah diperbarui setelah satu siklus evolusi.
                  Panjangnya sama dengan input.
        """
        if not strategy_pool or len(strategy_pool) < 2:
            logging.warning("Pool strategi kosong atau terlalu kecil untuk berevolusi.")
            return strategy_pool

        logging.info(f"Memulai evolusi untuk pool dengan {len(strategy_pool)} strategi.")

        # 1. Hitung fitness untuk semua strategi (jika belum ada)
        # Asumsi: Fitness mungkin sudah dihitung sebelumnya dan disimpan.
        # Untuk keamanan, kita pastikan semua memiliki fitness.
        for strategy in strategy_pool:
            if 'fitness' not in strategy or strategy['fitness'] is None:
                 # Placeholder: Hitung fitness menggunakan backtester (belum diimplementasi)
                 strategy['fitness'] = self._calculate_fitness(strategy)

        # 2. Pilih dua parent terbaik
        parent1, parent2 = self._select_parents(strategy_pool)
        if not parent1 or not parent2:
            logging.error("Gagal memilih parent untuk crossover.")
            return strategy_pool # Kembalikan pool tanpa perubahan

        logging.debug(f"Parent terpilih: P1 (fitness: {parent1.get('fitness', 'N/A')}), P2 (fitness: {parent2.get('fitness', 'N/A')})")

        # 3. Lakukan crossover untuk menghasilkan offspring
        offspring = self._crossover(parent1, parent2)
        logging.debug("Crossover selesai.")

        # 4. Terapkan mutasi pada offspring
        self._mutate(offspring)
        logging.debug("Mutasi selesai.")

        # 5. Hitung fitness offspring yang baru
        offspring['fitness'] = self._calculate_fitness(offspring)
        logging.debug(f"Fitness offspring baru: {offspring['fitness']}")

        # 6. Gantikan strategi terburuk dalam pool dengan offspring baru
        self._replace_worst(strategy_pool, offspring)
        logging.info("Evolusi satu siklus selesai.")

        return strategy_pool

    def _calculate_fitness(self, strategy_params: dict):
        """
        (PLACEHOLDER) Menghitung skor 'fitness' untuk sebuah set parameter strategi.
        Skor ini menentukan seberapa baik strategi tersebut (misalnya, berdasarkan
        Sharpe Ratio dari hasil backtest).

        Args:
            strategy_params (dict): Parameter strategi yang akan dievaluasi.

        Returns:
            float: Skor fitness. Semakin tinggi semakin baik.
        """
        # --- INI ADALAH PLACEHOLDER ---
        # Dalam implementasi penuh, di sinilah Anda akan:
        # 1. Menggunakan parameter `strategy_params` untuk mengkonfigurasi strategi.
        # 2. Menjalankan backtester terhadap data historis dengan strategi ini.
        # 3. Menghitung metrik performa seperti Sharpe Ratio, Profit Factor, dll.
        # 4. Mengembalikan metrik tersebut sebagai skor fitness.

        # Untuk tujuan demonstrasi dan pengujian awal, kita bisa menggunakan
        # logika sederhana atau nilai acak.
        # --- CONTOH LOGIKA SEMENTARA ---
        # Misalnya, kita asumsikan strategi dengan RSI period antara 10-20 dan
        # SMA fast antara 40-60 memiliki potensi lebih baik (hanya contoh).
        # try:
        #     rsi_p = strategy_params.get('rsi_period', 0)
        #     sma_f = strategy_params.get('sma_fast', 0)
        #     if 10 <= rsi_p <= 20 and 40 <= sma_f <= 60:
        #         return random.uniform(1.0, 2.0) # Fitness lebih tinggi
        #     else:
        #         return random.uniform(0.1, 1.0) # Fitness lebih rendah
        # except:
        #     return 0.01 # Fitness sangat rendah jika error

        # --- ATAU, UNTUK MULAI, GUNAKAN NILAI ACAK ---
        # Ini akan memungkinkan proses evolusi untuk berjalan, meski belum optimal.
        import random
        return random.uniform(0.01, 2.0)

    def _select_parents(self, strategy_pool: list):
        """
        Memilih dua strategi terbaik dari pool sebagai parent untuk crossover.
        Menggunakan metode seleksi berbasis fitness (semakin tinggi fitness,
        semakin besar kemungkinan terpilih).

        Args:
            strategy_pool (list): Daftar strategi dengan kunci 'fitness'.

        Returns:
            tuple: Dua dictionary strategi terpilih (parent1, parent2).
        """
        if len(strategy_pool) < 2:
             return None, None

        # Salin pool untuk menghindari mengubah yang asli secara tidak sengaja
        pool_copy = copy.deepcopy(strategy_pool)

        # Urutkan berdasarkan fitness menurun
        pool_copy.sort(key=lambda s: s.get('fitness', 0), reverse=True)

        # Pilihan sederhana: pilih dua terbaik
        parent1 = pool_copy[0]
        parent2 = pool_copy[1]

        # --- OPSIONAL: Implementasi Seleksi Roda Roulette untuk variasi lebih baik ---
        # total_fitness = sum(s.get('fitness', 0) for s in pool_copy)
        # if total_fitness > 0:
        #     # Pilih parent1
        #     pick = random.uniform(0, total_fitness)
        #     current = 0
        #     for strategy in pool_copy:
        #         current += strategy.get('fitness', 0)
        #         if current > pick:
        #             parent1 = strategy
        #             break
        #     # Pilih parent2 (bisa sama, tapi biasanya dipilih yang berbeda)
        #     # ... (logika untuk memastikan parent1 != parent2) ...
        # ---

        return parent1, parent2

    def _crossover(self, parent1: dict, parent2: dict):
        """
        Menggabungkan parameter dari dua parent untuk menciptakan offspring baru.
        Metode: Single-point crossover (titik potong acak).

        Args:
            parent1 (dict): Strategi parent pertama.
            parent2 (dict): Strategi parent kedua.

        Returns:
            dict: Dictionary parameter strategi offspring baru.
        """
        # Salin parent1 sebagai dasar offspring
        offspring = copy.deepcopy(parent1)

        # Dapatkan daftar kunci parameter (kecuali 'fitness')
        param_keys = [k for k in parent1.keys() if k != 'fitness']
        if not param_keys:
            logging.warning("Tidak ada parameter untuk di-crossover.")
            return offspring # Kembalikan salinan parent1

        # Tentukan titik potong acak
        # Jika hanya satu parameter, tidak perlu crossover
        if len(param_keys) > 1:
             crossover_point = random.randint(1, len(param_keys) - 1)
        else:
             crossover_point = 1

        # Ambil kunci untuk diambil dari parent2
        keys_from_p2 = param_keys[crossover_point:]

        # Ganti nilai di offspring dengan nilai dari parent2
        for key in keys_from_p2:
            if key in parent2:
                offspring[key] = parent2[key]

        logging.debug(f"Crossover pada titik {crossover_point}. Parameter dari P2: {keys_from_p2}")
        return offspring

    def _mutate(self, strategy: dict):
        """
        Mengubah satu parameter dalam strategi secara acak untuk menjaga variasi genetik.
        Metode: Gaussian Mutation (mengubah nilai numerik dengan noise kecil).

        Args:
            strategy (dict): Strategi (offspring) yang akan dimutasi.
        """
        # Dapatkan daftar kunci parameter (kecuali 'fitness')
        param_keys = [k for k in strategy.keys() if k != 'fitness']
        if not param_keys:
            return

        # Putuskan apakah akan bermutasi berdasarkan mutation_rate
        if random.random() > self.mutation_rate:
            return # Tidak terjadi mutasi

        # Pilih parameter acak untuk dimutasi
        key_to_mutate = random.choice(param_keys)
        original_value = strategy[key_to_mutate]

        # Mutasi hanya untuk tipe data numerik (int, float)
        if isinstance(original_value, (int, float)):
            # Tambahkan noise kecil (misalnya, +/- 10% dari nilai asli)
            mutation_strength = 0.1
            # Hindari mutasi yang membuat nilai 0 atau negatif untuk parameter tertentu
            # Misalnya, periode indikator biasanya > 0
            if original_value > 0:
                change = original_value * random.uniform(-mutation_strength, mutation_strength)
                new_value = original_value + change
                # Pastikan nilai baru tetap positif dan masuk akal
                # Misalnya, bulatkan ke integer terdekat untuk periode
                if isinstance(original_value, int):
                    strategy[key_to_mutate] = max(1, int(round(new_value))) # Minimal 1
                else: # float
                    strategy[key_to_mutate] = max(0.01, new_value) # Minimal 0.01
                logging.debug(f"Mutasi: {key_to_mutate} dari {original_value} menjadi {strategy[key_to_mutate]}")
            else:
                 # Jika nilai asli <= 0, buat nilai baru acak dalam range masuk akal
                 # Misalnya, untuk periode, gunakan antara 5-50
                 if key_to_mutate.endswith('_period') or 'period' in key_to_mutate.lower():
                     strategy[key_to_mutate] = random.randint(5, 50)
                     logging.debug(f"Mutasi (reset): {key_to_mutate} diatur ulang ke {strategy[key_to_mutate]}")
        else:
            # Untuk tipe data non-numerik, bisa diimplementasikan logika mutasi lain
            # Misalnya, mengganti string dengan yang lain dari daftar kemungkinan.
            # Untuk sekarang, kita lewati.
            logging.debug(f"Parameter {key_to_mutate} bukan numerik, dilewati untuk mutasi.")

    def _replace_worst(self, strategy_pool: list, new_strategy: dict):
        """
        Menggantikan strategi dengan fitness terendah dalam pool dengan strategi baru.

        Args:
            strategy_pool (list): Daftar strategi.
            new_strategy (dict): Strategi baru yang akan masuk ke pool.
        """
        if not strategy_pool:
            return

        # Temukan indeks strategi dengan fitness terendah
        worst_index = 0
        worst_fitness = strategy_pool[0].get('fitness', float('inf'))

        for i in range(1, len(strategy_pool)):
            current_fitness = strategy_pool[i].get('fitness', float('inf'))
            if current_fitness < worst_fitness:
                worst_fitness = current_fitness
                worst_index = i

        # Bandingkan fitness strategi baru dengan yang terburuk
        new_fitness = new_strategy.get('fitness', 0)
        if new_fitness > worst_fitness:
            # Ganti strategi terburuk dengan yang baru
            replaced_strategy = strategy_pool[worst_index]
            strategy_pool[worst_index] = new_strategy
            logging.info(f"Strategi terburuk (fitness: {worst_fitness}) diganti dengan offspring baru (fitness: {new_fitness}).")
        else:
            logging.info("Offspring baru tidak lebih baik dari strategi terburuk yang ada. Tidak ada penggantian.")

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Konfigurasi logging dasar untuk debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Karena kelas ini membutuhkan orchestrator, kita tidak bisa menjalankannya secara mandiri
    # tanpa mocking atau instance sebenarnya. Ini hanya untuk memastikan tidak ada syntax error.
    print("genetic_algorithm_engine.py dimuat dengan sukses. Siap untuk diintegrasikan.")
