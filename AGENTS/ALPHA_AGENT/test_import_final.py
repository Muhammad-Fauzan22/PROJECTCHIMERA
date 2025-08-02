# test_import_final.py

# Impor dari AGENTS
# Di dalam test_import_final.py
from AGENTS.ALPHA_AGENT.alpha_agent import AlphaAgent
#                              ^^^^^^^^^^^^
#                              Nama file (tanpa .py)

# Impor dari COLLECTIVE_MEMORY
from COLLECTIVE_MEMORY.gdrive_synchronizer import GDriveSynchronizer

# Impor dari CONTROL_PANEL
from CONTROL_PANEL.api_manager import APIManager

# Impor dari AI_BRAIN
from AI_BRAIN.llm_router import LLMRouter

# Impor dari SENTIENT_CORE
from SENTIENT_CORE.chimera_orchestrator import ChimeraOrchestrator

# Jika semua impor berhasil, cetak pesan sukses
print("SEMUA IMPOR BERHASIL! Lingkungan pengembangan siap.")