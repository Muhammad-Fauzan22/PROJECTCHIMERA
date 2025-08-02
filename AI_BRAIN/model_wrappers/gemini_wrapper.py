# -*- coding: utf-8 -*-
# ==============================================================================
# ==                  WRAPPER GOOGLE GEMINI (DEFINITIF) - PROJECT CHIMERA     ==
# ==============================================================================
#
# Lokasi: AI_BRAIN/model_wrappers/gemini_wrapper.py
# Deskripsi: Menyediakan antarmuka standar untuk berkomunikasi dengan
#            Google Gemini Pro API.
#
# ==============================================================================

import google.generativeai as genai
import logging
import json

class GeminiWrapper: # <--- PASTIKAN NAMA KELAS PERSIS SEPERTI INI
    """
    Wrapper untuk menangani permintaan ke Google Gemini Pro API.
    """
    def __init__(self, api_key: str):
        """
        Inisialisasi klien Gemini.
        
        Args:
            api_key (str): Kunci API untuk Google Gemini.
        """
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logging.info("Wrapper Gemini berhasil diinisialisasi.")
        except Exception as e:
            logging.critical(f"Gagal mengkonfigurasi Gemini: {e}", exc_info=True)
            raise ConnectionError("Gagal inisialisasi Gemini Wrapper.")

    def generate(self, prompt: str):
        """
        Mengirim prompt ke Gemini dan mem-parsing respons JSON.
        
        Args:
            prompt (str): Prompt yang akan dikirim ke model.
            
        Returns:
            dict: Hasil yang sudah di-parse dalam format dictionary, atau None jika gagal.
        """
        try:
            logging.debug("Mengirim permintaan ke Gemini...")
            response = self.model.generate_content(prompt)
            raw_text = response.text
            
            # Membersihkan dan mem-parsing output JSON dari model
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            
            return json.loads(clean_text)
            
        except json.JSONDecodeError as e:
            logging.error(f"Gemini tidak mengembalikan JSON yang valid: {e}")
            logging.debug(f"Raw output dari Gemini: {raw_text}")
            return None
        except Exception as e:
            logging.error(f"Terjadi error saat berkomunikasi dengan Gemini: {e}", exc_info=True)
            return None