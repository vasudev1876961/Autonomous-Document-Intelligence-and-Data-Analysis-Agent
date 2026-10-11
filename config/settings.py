"""
Global Configuration & Settings for the Autonomous Document Intelligence Agent.
"""
from pathlib import Path
from pydantic import BaseModel, Field
import os

BASE_DIR = Path(__file__).resolve().parent.parent

class AppSettings(BaseModel):
    app_name: str = "Autonomous Document Intelligence and Data Analysis Agent"
    version: str = "1.0.0"
    base_dir: Path = BASE_DIR
    
    # Storage Paths
    data_dir: Path = BASE_DIR / "data"
    sample_docs_dir: Path = BASE_DIR / "data" / "sample_documents"
    processed_dir: Path = BASE_DIR / "data" / "processed"
    evaluation_dir: Path = BASE_DIR / "data" / "evaluation"
    outputs_dir: Path = BASE_DIR / "outputs"
    reports_dir: Path = BASE_DIR / "outputs" / "reports"
    charts_dir: Path = BASE_DIR / "outputs" / "charts"
    
    # Database & Storage
    sqlite_db_path: Path = BASE_DIR / "data" / "processed" / "agent_memory.db"
    vector_store_dir: Path = BASE_DIR / "data" / "processed" / "vector_store"
    
    # Agent Guardrails & Limits
    max_agent_iterations: int = 15
    execution_timeout_seconds: int = 120
    require_hitl_for_discrepancies: bool = True
    
    # Supported File Formats
    supported_extensions: list[str] = [".pdf", ".docx", ".xlsx", ".csv"]

    def ensure_directories(self) -> None:
        """Create all necessary application directories if they do not exist."""
        for path in [
            self.data_dir,
            self.sample_docs_dir,
            self.processed_dir,
            self.evaluation_dir,
            self.outputs_dir,
            self.reports_dir,
            self.charts_dir,
            self.vector_store_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

settings = AppSettings()
settings.ensure_directories()
