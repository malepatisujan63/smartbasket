import datetime
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.utils.data_utils import save_artifact, load_artifact
from ml.configs import REGISTRY_DIR, config

class EnterpriseModelRegistry:
    """
    Production MLOps Model Registry.
    Tracks model versions, hyperparameters, evaluation metrics, dataset lineage,
    and manages lifecycle stages (Staging, Champion/Production, Archived).
    """
    def __init__(self, registry_dir: Path = REGISTRY_DIR):
        self.registry_dir = registry_dir
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.registry_dir / "registry_metadata.json"
        self._init_metadata()

    def _init_metadata(self):
        if not self.metadata_file.exists():
            initial_data = {
                "project": config.PROJECT_NAME,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "models": {},
                "production_champions": {}
            }
            save_artifact(initial_data, self.metadata_file)

    def _load_metadata(self) -> Dict[str, Any]:
        data = load_artifact(self.metadata_file)
        return data if isinstance(data, dict) else {"models": {}, "production_champions": {}}

    def _save_metadata(self, data: Dict[str, Any]):
        save_artifact(data, self.metadata_file)

    def register_model(
        self,
        model_name: str,
        model_object: Any,
        metrics: Dict[str, Any],
        hyperparameters: Dict[str, Any],
        dataset_version: str = "v1.0",
        stage: str = "Staging"
    ) -> str:
        """Registers a newly trained model artifact and logs its lineage metadata."""
        data = self._load_metadata()
        
        # Generate semantic version
        existing_versions = data["models"].get(model_name, [])
        version_num = len(existing_versions) + 1
        version_str = f"v{version_num}.0.0"
        
        artifact_filename = f"{model_name}_{version_str}.pkl"
        artifact_path = self.registry_dir / artifact_filename
        
        # Save model pickle
        save_artifact(model_object, artifact_path)
        
        entry = {
            "model_name": model_name,
            "version": version_str,
            "stage": stage,
            "training_date": datetime.datetime.utcnow().isoformat(),
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "dataset_version": dataset_version,
            "artifact_path": str(artifact_path)
        }
        
        if model_name not in data["models"]:
            data["models"][model_name] = []
        data["models"][model_name].append(entry)
        
        # Auto-promote to production if it's the first model or stage is Production
        if stage.lower() == "production" or model_name not in data["production_champions"]:
            self.promote_to_production(model_name, version_str, data=data)
        else:
            self._save_metadata(data)
            
        logger.info(f"Model '{model_name}' ({version_str}) registered successfully in stage '{stage}'.")
        return version_str

    def promote_to_production(self, model_name: str, version_str: str, data: Optional[Dict[str, Any]] = None):
        """Promotes a staging model version to Production Champion status."""
        if data is None:
            data = self._load_metadata()
            
        models = data["models"].get(model_name, [])
        target_entry = next((m for m in models if m["version"] == version_str), None)
        
        if not target_entry:
            logger.error(f"Cannot promote: Model '{model_name}' version '{version_str}' not found.")
            return
            
        # Archive previous champion
        for m in models:
            if m["stage"] == "Production":
                m["stage"] = "Archived"
                
        target_entry["stage"] = "Production"
        data["production_champions"][model_name] = target_entry
        self._save_metadata(data)
        logger.info(f"PROMOTED model '{model_name}' ({version_str}) to Production Champion!")

    def get_production_model(self, model_name: str) -> tuple:
        """Retrieves loaded production model object and its metadata."""
        data = self._load_metadata()
        champ = data["production_champions"].get(model_name)
        if not champ:
            logger.warning(f"No Production Champion found for '{model_name}'.")
            return None, {}
            
        model_obj = load_artifact(Path(champ["artifact_path"]))
        return model_obj, champ

    def list_models(self) -> Dict[str, Any]:
        """Returns full catalog of registered models and production champions."""
        return self._load_metadata()

# Global singleton Model Registry
model_registry = EnterpriseModelRegistry()
