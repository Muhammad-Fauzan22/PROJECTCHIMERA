# -*- coding: utf-8 -*-
# ==============================================================================
# ==                 SINKRONISASI GOOGLE DRIVE - PROJECT CHIMERA              ==
# ==============================================================================
#
# Lokasi: COLLECTIVE_MEMORY/gdrive_synchronizer.py
# Deskripsi: Mengelola koneksi dan operasi upload/download ke Google Drive.
#
# ==============================================================================

import os
import io
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Jika mengubah cakupan ini, hapus file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

class GDriveSynchronizer: # <-- NAMA KELAS YANG BENAR
    """
    Menangani semua interaksi dengan Google Drive API.
    """
    def __init__(self, orchestrator):
        """
        Inisialisasi dan otentikasi ke Google Drive.
        
        Args:
            orchestrator (ChimeraOrchestrator): Instance orkestrator utama.
        """
        logging.info("Menginisialisasi QuantumSync: Sinkronisasi Memori Kolektif...")
        self.orchestrator = orchestrator
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Proses otentikasi OAuth2. Akan membuka browser saat pertama kali dijalankan.
        """
        creds_path = self.orchestrator.project_root / "CONTROL_PANEL" / "CONFIG" / "credentials.json"
        token_path = self.orchestrator.project_root / "CONTROL_PANEL" / "CONFIG" / "token.json"

        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logging.warning(f"Gagal me-refresh token, perlu otorisasi ulang: {e}")
                    self._run_flow(creds_path, token_path)
            else:
                self._run_flow(creds_path, token_path)
            
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())
        
        try:
            self.service = build("drive", "v3", credentials=self.creds)
            logging.info("Koneksi ke Google Drive API berhasil.")
        except Exception as e:
            logging.critical(f"Gagal membangun layanan Google Drive: {e}", exc_info=True)
            raise ConnectionError("Tidak dapat terhubung ke Google Drive.")

    def _run_flow(self, creds_path, token_path):
        """Menjalankan alur otorisasi interaktif."""
        logging.warning("Kredensial tidak ditemukan atau tidak valid. Memulai alur otentikasi baru...")
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        self.creds = flow.run_local_server(port=0)

    def upload_data_as_csv(self, dataframe, filename, folder_id=None):
        """
        Mengubah DataFrame pandas menjadi CSV dan mengunggahnya ke Google Drive.
        
        Args:
            dataframe (pd.DataFrame): Data yang akan diunggah.
            filename (str): Nama file di Google Drive (misal: "market_data_20240728.csv").
            folder_id (str, optional): ID folder di Google Drive. Jika None, akan diunggah ke root.
        
        Returns:
            str: ID file yang baru diunggah, atau None jika gagal.
        """
        try:
            logging.info(f"Mempersiapkan unggahan file '{filename}' ke Google Drive...")
            csv_buffer = io.StringIO()
            dataframe.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]
                
            media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv', resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logging.info(f"File '{filename}' berhasil diunggah dengan ID: {file_id}")
            return file_id
            
        except Exception as e:
            logging.error(f"Gagal mengunggah file '{filename}' ke Google Drive: {e}", exc_info=True)
            return None