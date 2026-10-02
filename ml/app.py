import os
import nltk
import re
import random
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from tavily import TavilyClient

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Optional, List, Any
import uvicorn

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

app = FastAPI(title="Plagiarism Checker ML Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"}
    )

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Tavily Client
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

FALLBACK_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'in',
    'is', 'it', 'of', 'on', 'or', 'that', 'the', 'to', 'was', 'were', 'with'
}

# ─── Text Preprocessor ───────────────────────────────────────
def preprocess_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    try:
        stop = set(stopwords.words('english'))
    except LookupError:
        # Allow local/offline use when the optional NLTK corpus is unavailable.
        stop = FALLBACK_STOPWORDS
    words = text.split()
    return ' '.join([w for w in words if w not in stop])

# ─── Code Preprocessor ───────────────────────────────────────
def preprocess_code(code):
    if not code:
        return ""
    code = re.sub(r'#.*', '', code)
    code = re.sub(r'\".*?\"|\'.*?\'', 'STR', code)
    code = re.sub(r'\s+', ' ', code).strip()
    return code.lower()

# ─── Similarity Calculator ────────────────────────────────────
def compute_similarity(text1, text2):
    clean1 = preprocess_text(text1)
    clean2 = preprocess_text(text2)
    if not clean1 or not clean2:
        return 0.0
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([clean1, clean2])
    score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return round(float(score) * 100, 2)

# ─── Code Detection ──────────────────────────────────────────
def is_code(text):
    code_keywords = ['def ', 'import ', 'class ', 'function ',
                     'const ', 'var ', 'let ', '=> ', '#!/',
                     'public ', 'private ', 'return ', 'print(']
    return any(kw in text for kw in code_keywords)

# ─── Word Level Analysis ─────────────────────────────────────
def word_level_analysis(text1, text2):
    words1 = set(preprocess_text(text1).split())
    words2 = set(preprocess_text(text2).split())
    if not words1 or not words2:
        return 0.0
    common = words1.intersection(words2)
    return round(len(common) / max(len(words1), len(words2)) * 100, 2)

# ─── Highlights ───────────────────────────────────────────────
def get_highlights(input_text, source_text, threshold=30, max_highlights=50):
    try:
        input_sentences = sent_tokenize(input_text)
        source_sentences = sent_tokenize(source_text)

        if not input_sentences or not source_sentences:
            return []

        # Preprocess sentences
        input_clean = [preprocess_text(s) for s in input_sentences]
        source_clean = [preprocess_text(s) for s in source_sentences]

        all_sentences = input_clean + source_clean

        # Check if there is valid text to vectorize
        if not any(s.strip() for s in all_sentences):
            return []

        # One single TF-IDF matrix for all sentences
        vectorizer = TfidfVectorizer(max_features=10000, stop_words="english")
        matrix = vectorizer.fit_transform(all_sentences)

        input_count = len(input_sentences)
        input_vectors = matrix[:input_count]
        source_vectors = matrix[input_count:]

        # One instant matrix multiplication
        similarities = cosine_similarity(input_vectors, source_vectors)

        matches = []
        for i, row in enumerate(similarities):
            best_index = int(row.argmax())
            best_score = float(row[best_index] * 100)

            if best_score >= threshold:
                matches.append({
                    "input_sentence": input_sentences[i],
                    "matched_sentence": source_sentences[best_index],
                    "score": round(best_score, 2)
                })

        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:max_highlights]

    except Exception as e:
        print(f"Highlight error: {e}")
        return []

def check_web_tavily(input_text):
    if not tavily:
        return []
    try:
        query = input_text[:200]
        response = tavily.search(query=query, max_results=5)
        matched_sources = []
        for result in response.get('results', []):
            content = result.get('content', '')
            url = result.get('url', '')
            title = result.get('title', '')
            if content:
                score = compute_similarity(input_text, content)
                if score > 10:
                    matched_sources.append({
                        "url": url,
                        "title": title,
                        "similarity_score": score,
                        "content": content
                    })
        matched_sources.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matched_sources
    except Exception as e:
        print(f"Tavily error: {e}")
        return []

# ─── AI Detection (Enhanced NLP Heuristics) ───────────────────
def detect_ai_generated(text):
    """
    Analyzes text using linguistic patterns common in LLMs:
    1. Burstiness (Variance in sentence length)
    2. Perplexity Proxy (Word frequency and predictability)
    3. AI-Flavor Vocabulary (Transition words and formal tone)
    4. Sentence Length Uniformity
    """
    words = text.split()
    if len(words) < 25:
        return 0.0
    
    # 1. Vocabulary Analysis (AI-flavor keywords)
    ai_patterns = [
        'delve', 'moreover', 'furthermore', 'in conclusion', 'tapestry', 'testament', 
        'intricate', 'crucial', 'vital', 'navigating', 'landscape', 'realm', 
        'multifaceted', 'underscore', 'noteworthy', 'imperative', 'transformational',
        'it is important to note', 'in the ever-evolving', 'at the end of the day',
        'comprehensive', 'synergy', 'leverage', 'bespoke', 'holistic'
    ]
    keyword_count = sum(1 for kw in ai_patterns if kw in text.lower())
    
    # 2. Burstiness (Sentence Length Variance) & Uniformity
    try:
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            burstiness_score = 50 
        else:
            lengths = [len(s.split()) for s in sentences]
            avg_len = sum(lengths) / len(lengths)
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            
            # AI has low variance (uniform sentence lengths)
            if variance < 10: burstiness_score = 90
            elif variance < 20: burstiness_score = 70
            elif variance < 40: burstiness_score = 40
            else: burstiness_score = 15
            
            # 2b. Average sentence length (AI often uses 15-25 words)
            if 15 <= avg_len <= 25:
                burstiness_score += 10
    except:
        burstiness_score = 50

    # 3. Connective Tissue Density
    transition_words = ['however', 'therefore', 'consequently', 'additionally', 'similarly', 'nonetheless', 'despite']
    transition_count = sum(1 for w in transition_words if w in text.lower())
    transition_density = (transition_count / len(words)) * 1000 # per 1000 words

    # 4. Perplexity Proxy (Lexical Diversity)
    unique_words = set(preprocess_text(text).split())
    lexical_diversity = (len(unique_words) / len(words)) if len(words) > 0 else 0
    # AI has slightly lower lexical diversity than high-quality human writing
    perplexity_score = 100 - (lexical_diversity * 150) # Heuristic scaling
    perplexity_score = max(0, min(100, perplexity_score))

    # Weighted Calculation
    # 35% Burstiness, 25% Keywords, 15% Transitions, 20% Perplexity, 5% Jitter
    score = (burstiness_score * 0.35) + \
            (min(100, keyword_count * 15) * 0.25) + \
            (min(100, transition_density * 6) * 0.15) + \
            (perplexity_score * 0.20)
    
    score += random.uniform(0, 5) # Subtle jitter
    
    return min(100.0, max(0.0, round(score, 2)))

# ─── Main Analyze Function ───────────────────────────────────
def analyze_text(input_text, reference_text=None, check_ai=False, exclude_quotes=False, exclude_bib=False, check_web=True):
    # Apply Filters
    processed_input = input_text
    
    if exclude_quotes:
        # Remove text between various types of quotes
        processed_input = re.sub(r'["“].*?["”]', '', processed_input)
        processed_input = re.sub(r"'.*?'", '', processed_input)

    if exclude_bib:
        # Truncate at bibliography markers
        bib_markers = [
            r'\nreferences\n', r'\nbibliography\n', r'\nworks cited\n',
            r'\nreferences\r\n', r'\nbibliography\r\n', r'\nworks cited\r\n'
        ]
        lower_text = processed_input.lower()
        earliest_pos = len(processed_input)
        for marker in bib_markers:
            match = re.search(marker, lower_text)
            if match and match.start() < earliest_pos:
                earliest_pos = match.start()
        processed_input = processed_input[:earliest_pos]

    result = {
        "score": 0,
        "word_match": 0,
        "sentence_match": 0,
        "type_detected": "text",
        "matched_sources": [],
        "highlights": [],
        "summary": "",
        "ai_score": 0.0
    }

    # Detect type
    if is_code(processed_input):
        result["type_detected"] = "code"
        clean1 = preprocess_code(processed_input)
        clean2 = preprocess_code(reference_text) if reference_text else ""
    else:
        result["type_detected"] = "text"
        clean1 = preprocess_text(processed_input)
        clean2 = preprocess_text(reference_text) if reference_text else ""

    all_scores = []

    # Direct comparison
    if reference_text:
        try:
            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform([clean1, clean2])
            tfidf_score = round(
                float(cosine_similarity(matrix[0], matrix[1])[0][0]) * 100, 2
            )
        except:
            tfidf_score = 0.0

        word_score = word_level_analysis(processed_input, reference_text)
        direct_score = round((tfidf_score * 0.7) + (word_score * 0.3), 2)
        highlights = get_highlights(processed_input, reference_text)

        result["word_match"] = word_score
        result["sentence_match"] = tfidf_score
        result["highlights"] = highlights
        result["matched_sources"].append({
            "url": "direct_comparison",
            "title": "Reference Document",
            "similarity_score": direct_score
        })
        all_scores.append(direct_score)

    # Web check via Tavily
    if check_web:
        web_matches = check_web_tavily(processed_input)
        result["matched_sources"].extend(web_matches)
        for match in web_matches:
            all_scores.append(match["similarity_score"])
            # Generate highlights from top web source
            if match["similarity_score"] > 20 and not result["highlights"]:
                web_content = match.get("content", "")
                if web_content:
                    result["highlights"] = get_highlights(processed_input, web_content)

    # Final score
    if all_scores:
        result["score"] = max(all_scores)
    
    # Summary
    score = result["score"]
    if score >= 70:
        result["summary"] = "High plagiarism detected! Most content is copied."
    elif score >= 40:
        result["summary"] = "Medium plagiarism detected. Some content matches."
    elif score >= 10:
        result["summary"] = "Low plagiarism detected. Minor similarities found."
    else:
        result["summary"] = "Original content! No significant plagiarism found."
 
    # AI Detection
    if check_ai:
        result["ai_score"] = detect_ai_generated(processed_input)

    return result

# ─── FastAPI Request Model ────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text: Optional[str] = ""
    reference: Optional[str] = None
    check_ai: Optional[bool] = False
    check_web: Optional[bool] = True
    exclude_quotes: Optional[bool] = False
    exclude_bib: Optional[bool] = False
    exclude_bibliography: Optional[bool] = False

    model_config = {"extra": "allow"}

# ─── FastAPI Routes ───────────────────────────────────────────
@app.post("/analyze")
async def analyze_endpoint(payload: AnalyzeRequest):
    try:
        input_text = payload.text if payload.text is not None else ""
        if not input_text or not input_text.strip():
            return JSONResponse(status_code=400, content={"error": "No text provided"})

        reference_text = payload.reference
        check_ai = bool(payload.check_ai)
        exclude_quotes = bool(payload.exclude_quotes)
        exclude_bib = bool(payload.exclude_bib or payload.exclude_bibliography)
        check_web = True if payload.check_web is None else bool(payload.check_web)

        result = analyze_text(
            input_text=input_text,
            reference_text=reference_text,
            check_ai=check_ai,
            exclude_quotes=exclude_quotes,
            exclude_bib=exclude_bib,
            check_web=check_web
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok", "service": "Plagiarism Checker ML Service (FastAPI)"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Python ML Server (FastAPI) running on port {port}!")
    uvicorn.run(app, host="0.0.0.0", port=port)
