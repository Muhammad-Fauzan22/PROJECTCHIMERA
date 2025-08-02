import logging
import random
from concurrent.futures import ThreadPoolExecutor

# Impor wrapper hanya ketika diperlukan
def _import_gemini_wrapper():
    from AI_BRAIN.model_wrappers.gemini_wrapper import GeminiWrapper
    return GeminiWrapper

def _import_openrouter_wrapper():
    from AI_BRAIN.model_wrappers.openrouter_wrapper import OpenRouterWrapper
    return OpenRouterWrapper

class LLMRouter:
    """
    Mengelola dan mendistribusikan tugas ke seluruh dewan AI secara paralel.
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.secrets = self.orchestrator.secrets
        self.model_inventory = self._load_model_inventory()
        self.key_indices = {model: 0 for model in self.model_inventory}
        
        # Impor wrapper hanya ketika diperlukan
        self.wrappers = {
            "google": _import_gemini_wrapper(),
            "default": _import_openrouter_wrapper()  # Untuk semua model lain via OpenRouter
        }

    def _load_model_inventory(self):
        """Memuat semua kunci LLM yang tersedia dari secrets.vault."""
        ai_secrets = self.secrets.get('ai_apis', {})
        inventory = {}
        # Iterasi melalui semua entri di bagian [ai_apis]
        for key, value in ai_secrets.items():
            # Kita hanya tertarik pada entri yang merupakan daftar kunci (berakhir dengan '_keys')
            if key.endswith('_keys') and isinstance(value, list):
                # Ambil nama model dari nama kunci (misal: 'google_llm_keys' -> 'google')
                model_name = key.replace('_llm_keys', '')
                inventory[model_name] = value
        logging.info(f"Inventaris model LLM berhasil dimuat: {list(inventory.keys())}")
        return inventory

    def _rotate_key(self, model_name: str):
        """Memutar kunci API untuk satu model dan mengembalikannya."""
        if model_name in self.model_inventory:
            keys = self.model_inventory[model_name]
            if not keys:
                return None
            # Dapatkan indeks saat ini, putar, lalu simpan indeks baru
            current_index = self.key_indices.get(model_name, 0)
            next_index = (current_index + 1) % len(keys)
            self.key_indices[model_name] = next_index
            logging.debug(f"Memutar kunci untuk {model_name} ke indeks {next_index}.")
            return keys[current_index]  # Kembalikan kunci pada indeks saat ini sebelum diputar
        return None

    def select_model_for_task(self, task_type: str):
        """
        Memilih model dan kunci API yang paling sesuai berdasarkan jenis tugas.
        """
        logging.info(f"Memilih model LLM untuk tugas: {task_type}")
        
        # Peta tugas ke model yang direkomendasikan
        task_to_model_map = {
            "fast_sentiment_analysis": "deepseek",
            "deep_market_analysis": "google",      # Gemini
            "code_generation": "anthropic",         # Claude
            "risk_scenario": "anthropic",           # Claude
            "sentiment_psychology": "openai",       # GPT-4o
            "execution_strategy": "deepseek"
        }
        
        model_choice = task_to_model_map.get(task_type, "openai")  # Default ke OpenAI jika tugas tidak dikenal

        api_key = self._rotate_key(model_choice)
        
        # Logika fallback jika model pilihan tidak memiliki kunci API yang valid
        if not api_key:
            logging.warning(f"Tidak ada kunci API yang tersedia untuk model pilihan: {model_choice}. Mencari alternatif...")
            available_models = [m for m, k in self.model_inventory.items() if k]
            if not available_models:
                raise ValueError("Tidak ada kunci API LLM yang dikonfigurasi di secrets.vault.")
            
            model_choice = random.choice(available_models)
            api_key = self._rotate_key(model_choice)

        logging.info(f"Model terpilih: {model_choice}, menggunakan kunci indeks: {self.key_indices[model_choice]}")
        return model_choice, api_key

    def get_council_analysis(self, article_text: str):
        """
        Mengirim tugas analisis ke anggota dewan AI yang relevan secara paralel.
        """
        # Definisikan anggota dewan dan tugas spesifik mereka
        council_tasks = {
            "macro_fundamental": "deep_market_analysis",
            "risk_scenario": "risk_scenario",
            "sentiment_psychology": "sentiment_psychology",
            "execution_strategy": "execution_strategy"
        }
        
        results = {}
        with ThreadPoolExecutor(max_workers=len(council_tasks)) as executor:
            future_to_task = {
                executor.submit(self.run_single_analysis, task_type, article_text): task_name
                for task_name, task_type in council_tasks.items()
            }
            for future in future_to_task:
                task_name = future_to_task[future]
                try:
                    results[task_name] = future.result()
                except Exception as exc:
                    logging.error(f"Tugas analisis dewan '{task_name}' gagal: {exc}")
                    results[task_name] = None
        return results

    def run_single_analysis(self, task_type: str, article_text: str):
        """Menjalankan satu tugas analisis pada model AI yang paling sesuai."""
        model_name, api_key = self.select_model_for_task(task_type)
        
        # Di masa depan, kita akan menggunakan prompt_engineer.py di sini
        prompt = f"Analyze the following article for {task_type}:\n\n{article_text[:2000]}"
        
        WrapperClass = self.wrappers.get(model_name, self.wrappers["default"])
        
        if model_name == "google":
            wrapper = WrapperClass(api_key)
        else:
            wrapper = WrapperClass(api_key, model_name)
            
        return wrapper.generate(prompt)