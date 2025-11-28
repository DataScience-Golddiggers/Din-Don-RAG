import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.logger import logger


def create_directory_structure():
    logger.info("Creating directory structure...")
    
    directories = [
        config.RAW_DATA_DIR,
        config.PROCESSED_DATA_DIR,
        config.CLEANED_DATA_DIR,
        config.MODELS_DIR,
        config.LOGS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        gitkeep.touch(exist_ok=True)
        logger.info(f"✓ Created: {directory}")
    
    logger.info("✓ Directory structure created successfully!")


def create_env_file():
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        logger.info("✓ .env file already exists")
        return
    
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        logger.info("✓ Created .env from .env.example")
    else:
        logger.warning("✗ .env.example not found")


def check_dependencies():
    logger.info("Checking dependencies...")
    
    required_packages = [
        'numpy',
        'pandas',
        'sklearn',
        'nltk',
        'matplotlib',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package}")
        except ImportError:
            missing.append(package)
            logger.error(f"✗ {package}")
    
    if missing:
        logger.warning(f"Missing packages: {', '.join(missing)}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    logger.info("✓ All dependencies installed!")
    return True


def download_nltk_resources():
    logger.info("Downloading NLTK resources...")
    
    import nltk
    resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
    
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
            logger.info(f"✓ {resource}")
        except Exception as e:
            logger.error(f"✗ {resource}: {e}")
    
    logger.info("✓ NLTK resources downloaded!")


def main():
    print("\n" + "=" * 50)
    print("🍃 ALLMond Project Initialization")
    print("=" * 50 + "\n")
    
    create_directory_structure()
    print()
    
    create_env_file()
    print()
    
    deps_ok = check_dependencies()
    print()
    
    if deps_ok:
        try:
            download_nltk_resources()
        except ImportError:
            logger.warning("NLTK not installed, skipping resource download")
    
    print("\n" + "=" * 50)
    print("✓ Project initialization complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Review and edit .env file")
    print("2. Place your data in data/raw/")
    print("3. Run: jupyter notebook")
    print("4. Open notebooks/nlp_pipeline.ipynb")
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
