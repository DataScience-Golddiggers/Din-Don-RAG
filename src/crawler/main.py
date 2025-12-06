from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from crawl4ai import AsyncWebCrawler

app = FastAPI()

# Hardcoded UnivPM URLs
UNIVPM_URLS = [
    "https://www.univpm.it/Entra/",
    "https://www.univpm.it/Entra/Ateneo",
    "https://www.univpm.it/Entra/Didattica",
    "https://www.univpm.it/Entra/Ricerca"
]

class CrawlRequest(BaseModel):
    urls: Optional[List[str]] = None

@app.post("/crawl")
async def crawl(request: CrawlRequest):
    urls_to_crawl = request.urls if request.urls else UNIVPM_URLS
    
    results = []
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for url in urls_to_crawl:
            try:
                result = await crawler.arun(url=url)
                # result.markdown contains the content converted to markdown (stripping HTML)
                results.append({
                    "url": url,
                    "content": result.markdown,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "error": str(e),
                    "success": False
                })
                
    return {"results": results}

@app.get("/health")
def health():
    return {"status": "ok"}
