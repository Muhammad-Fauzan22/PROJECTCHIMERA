# Lokasi: COLLECTIVE_MEMORY/vector_store.py
import chromadb
import logging

class VectorStore:

    def __init__(self, orchestrator):
        logging.info("Menginisialisasi Memori Vektor (ChromaDB)...")
        self.client = chromadb.PersistentClient(path=str(orchestrator.project_root / "COLLECTIVE_MEMORY" / "vector_db"))
        self.collection = self.client.get_or_create_collection(name="chimera_intelligence")
        logging.info(">>> Memori Vektor siap.")

    def add_document(self, text: str, metadata: dict, doc_id: str):
  
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logging.debug(f"Dokumen {doc_id} ditambahkan ke Memori Vektor.")
        except Exception as e:
            logging.error(f"Gagal menambahkan dokumen ke ChromaDB: {e}")

    def query(self, query_text: str, n_results: int = 5):
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0]
        except Exception as e:
            logging.error(f"Gagal melakukan query ke ChromaDB: {e}")
            return []