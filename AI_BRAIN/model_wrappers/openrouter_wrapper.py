# -*- coding: utf-8 -*-
# ==============================================================================
# ==               WRAPPER OPENROUTER (DEFINITIF) - PROJECT CHIMERA           ==
# ==============================================================================
#
# Lokasi: AI_BRAIN/model_wrappers/openrouter_wrapper.py
# Deskripsi: Menyediakan antarmuka universal untuk berkomunikasi dengan
#            berbagai model LLM melalui OpenRouter API.
#
# ==============================================================================

import requests
import logging
import json

class OpenRouterWrapper: # <--- PASTIKAN NAMA KELAS PERSIS SEPERTI INI
    """
    Wrapper untuk menangani permintaan ke berbagai model via OpenRouter.
    """
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model_name: str):
        """
        Inisialisasi klien OpenRouter.
        
        Args:
            api_key (str): Kunci API OpenRouter (bisa kunci DeepSeek, OpenAI, dll.).
            model_name (str): Nama pendek model (misal: 'deepseek', 'openai').
        """
        self.api_key = api_key
        self.model_name = self._get_full_model_name(model_name)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info(f"Wrapper OpenRouter diinisialisasi untuk model: {self.model_name}")

    def _get_full_model_name(self, short_name: str) -> str:
        """Menerjemahkan nama pendek ke nama model lengkap di OpenRouter."""
        model_map = {
            "deepseek": "deepseek/deepseek-chat",
            "openai": "openai/gpt-4o",
            "anthropic": "anthropic/claude-3.5-sonnet",
            "meta": "meta-llama/llama-3-70b-instruct",
            "xai": "xai-inc/grok-1",
            "cohere": "cohere/command-r-plus",
        }
        return model_map.get(short_name, short_name)

    def generate(self, prompt: str):
        """
        Mengirim prompt ke model yang dipilih via OpenRouter.
        
        Returns:
            dict: Hasil yang sudah di-parse, atau None jika gagal.
        """
        body = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            logging.debug(f"Mengirim permintaan ke OpenRouter untuk model {self.model_name}...")
            response = requests.post(self.API_URL, headers=self.headers, json=body, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            raw_text = data['choices'][0]['message']['content']
            
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()

            return json.loads(clean_text)

        except json.JSONDecodeError as e:
            logging.error(f"Model {self.model_name} tidak mengembalikan JSON yang valid: {e}")
            logging.debug(f"Raw output dari {self.model_name}: {raw_text}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error koneksi ke OpenRouter: {e}")
            return None
        except Exception as e:
            logging.error(f"Terjadi error saat berkomunikasi dengan OpenRouter: {e}", exc_info=True)
            return None