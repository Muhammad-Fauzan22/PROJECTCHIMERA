from transformers import pipeline, Pipeline
import torch
from UTILS.singleton import SingletonMeta

class SentimentAnalyzer(metaclass=SingletonMeta):
    """
    Wrapper Singleton untuk pipeline analisis sentimen dari Hugging Face.
    Memastikan model AI yang berat hanya dimuat ke memori satu kali.
    """
    _pipeline: Pipeline = None

    def __init__(self):
        """
        Inisialisasi akan memuat model saat instance pertama dibuat.
        """
        if self._pipeline is None:
            self._load_pipeline()

    def _load_pipeline(self):
        """Memuat model AI. Terisolasi untuk penanganan error."""
        try:
            model_name = "ElKulako/cryptobert"
            print(f"Inisialisasi model sentimen '{model_name}' untuk pertama kalinya...")
            device = 0 if torch.cuda.is_available() else -1
            self._pipeline = pipeline(
                'sentiment-analysis',
                model=model_name,
                device=device
            )
            print("Model sentimen berhasil dimuat.")
        except Exception as e:
            print(f"KRITIS: Gagal memuat model sentimen: {e}")
            self._pipeline = None

    def analyze(self, text_list: list[str]) -> list[dict]:
        """
        Menganalisis daftar teks dan mengembalikan hasil terstruktur.
        """
        if self._pipeline is None:
            print("ERROR: Model sentimen tidak tersedia.")
            return [{"error": "Model not available"}] * len(text_list)
        
        try:
            return self._pipeline(text_list)
        except Exception as e:
            print(f"ERROR: Terjadi kesalahan saat analisis sentimen: {e}")
            return [{"error": str(e)}] * len(text_list)

if __name__ == "__main__":
    print("Menjalankan tes mandiri untuk SentimentAnalyzer...")
    
    # Instance pertama akan memuat model
    analyzer = SentimentAnalyzer()

    # Instance kedua akan menggunakan kembali model yang sudah ada
    analyzer2 = SentimentAnalyzer()

    test_headlines = [
        "Despite the recent dip, long-term HODLers are accumulating BTC.",
        "Another DeFi protocol has been exploited, millions lost.",
    ]
    
    analysis_results = analyzer.analyze(test_headlines)
    
    print("\n--- Hasil Analisis ---")
    if analysis_results:
        for headline, result in zip(test_headlines, analysis_results):
            print(f"Teks: '{headline}' -> Hasil: {result}")
