import pandas as pd
from pathlib import Path
from typing import Optional, Union
from utils.logger import logger


class DataLoader:
    
    @staticmethod
    def load_csv(
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        **kwargs
    ) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            logger.info(f"Loaded CSV file: {file_path} ({len(df)} rows)")
            return df
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 failed, trying latin-1 encoding for {file_path}")
            df = pd.read_csv(file_path, encoding="latin-1", **kwargs)
            logger.info(f"Loaded CSV file with latin-1: {file_path} ({len(df)} rows)")
            return df
    
    @staticmethod
    def load_excel(
        file_path: Union[str, Path],
        sheet_name: Union[str, int] = 0,
        **kwargs
    ) -> pd.DataFrame:
        df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        logger.info(f"Loaded Excel file: {file_path} ({len(df)} rows)")
        return df
    
    @staticmethod
    def load_json(
        file_path: Union[str, Path],
        **kwargs
    ) -> pd.DataFrame:
        df = pd.read_json(file_path, **kwargs)
        logger.info(f"Loaded JSON file: {file_path} ({len(df)} rows)")
        return df
    
    @staticmethod
    def load_text_files(
        directory: Union[str, Path],
        pattern: str = "*.txt",
        encoding: str = "utf-8"
    ) -> pd.DataFrame:
        directory = Path(directory)
        files = list(directory.glob(pattern))
        
        data = []
        for file_path in files:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                    data.append({
                        "filename": file_path.name,
                        "text": content,
                        "path": str(file_path)
                    })
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        df = pd.DataFrame(data)
        logger.info(f"Loaded {len(df)} text files from {directory}")
        return df
    
    @staticmethod
    def save_dataframe(
        df: pd.DataFrame,
        file_path: Union[str, Path],
        format: str = "csv",
        **kwargs
    ):
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            df.to_csv(file_path, index=False, **kwargs)
        elif format == "excel":
            df.to_excel(file_path, index=False, **kwargs)
        elif format == "json":
            df.to_json(file_path, **kwargs)
        elif format == "pickle":
            df.to_pickle(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved dataframe to {file_path} ({len(df)} rows)")
