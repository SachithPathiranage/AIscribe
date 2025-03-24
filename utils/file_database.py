import os
import json
import pickle
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

class FileDatabase:
    """Simple database for storing processed file results"""
    
    def __init__(self, db_path: str = "data/processed_files"):
        """
        Initialize file database
        
        Args:
            db_path: Path to store processed file data
        """
        self.db_path = db_path
        self.index_file = os.path.join(db_path, "index.json")
        
        # Create database directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize or load index
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                "files": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_index()
    
    def _save_index(self):
        """Save index file"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _generate_file_id(self, file_name: str, file_content: bytes) -> str:
        """Generate unique ID for a file based on name and content hash"""
        content_hash = hashlib.md5(file_content).hexdigest()
        return f"{os.path.splitext(file_name)[0]}_{content_hash[:8]}"
    
    def save_file_results(self, file_name: str, file_content: bytes, results: Dict[str, Any]) -> str:
        """
        Save processed file results
        
        Args:
            file_name: Name of the file
            file_content: Raw content of the file
            results: Analysis results
        
        Returns:
            File ID
        """
        # Generate file ID
        file_id = self._generate_file_id(file_name, file_content)
        
        # Create file record
        file_record = {
            "file_name": file_name,
            "file_type": results.get("file_type", "unknown"),
            "processed_at": datetime.now().isoformat(),
            "results_path": f"{file_id}.pickle"
        }
        
        # Save results to pickle file
        results_path = os.path.join(self.db_path, f"{file_id}.pickle")
        with open(results_path, 'wb') as f:
            pickle.dump(results, f)
        
        # Update index
        self.index["files"][file_id] = file_record
        self._save_index()
        
        return file_id
    
    def get_file_results(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processed file results
        
        Args:
            file_id: File ID
        
        Returns:
            Analysis results or None if not found
        """
        if file_id not in self.index["files"]:
            return None
        
        results_path = os.path.join(self.db_path, self.index["files"][file_id]["results_path"])
        
        if not os.path.exists(results_path):
            return None
        
        with open(results_path, 'rb') as f:
            return pickle.load(f)
    
    def list_files(self, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List processed files
        
        Args:
            file_type: Filter by file type
        
        Returns:
            List of file records
        """
        files = []
        
        for file_id, file_record in self.index["files"].items():
            if file_type is None or file_record["file_type"] == file_type:
                record = file_record.copy()
                record["file_id"] = file_id
                files.append(record)
        
        # Sort by processed_at (newest first)
        files.sort(key=lambda x: x["processed_at"], reverse=True)
        
        return files
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete processed file
        
        Args:
            file_id: File ID
        
        Returns:
            True if file was deleted, False otherwise
        """
        if file_id not in self.index["files"]:
            return False
        
        # Delete results file
        results_path = os.path.join(self.db_path, self.index["files"][file_id]["results_path"])
        if os.path.exists(results_path):
            os.remove(results_path)
        
        # Remove from index
        del self.index["files"][file_id]
        self._save_index()
        
        return True