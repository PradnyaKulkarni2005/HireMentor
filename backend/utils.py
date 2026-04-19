import re
import string
from functools import lru_cache
from typing import List, Set
from nltk.stem import WordNetLemmatizer

# Initialize NLTK components with fallback
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except LookupError:
    # Fallback stopwords if NLTK data not available
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your',
        'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself',
        'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
        'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
        'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
        'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
        'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now',
        'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn',
        "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't",
        'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
        "weren't", 'won', "won't", 'wouldn', "wouldn't"
    }

lemmatizer = WordNetLemmatizer()

@lru_cache(maxsize=1000)
def lemmatize_word(word: str) -> str:
    """Cache lemmatization for performance."""
    return lemmatizer.lemmatize(word.lower())

def preprocess_text(text: str) -> List[str]:
    """Preprocess text: lowercase, remove punctuation, tokenize, remove stopwords."""
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize
    words = text.split()

    # Remove stopwords and lemmatize
    processed_words = []
    for word in words:
        if word not in stop_words and len(word) > 1:
            processed_words.append(lemmatize_word(word))

    return processed_words

def calculate_similarity(word1: str, word2: str) -> float:
    """Simple word similarity based on edit distance."""
    if word1 == word2:
        return 1.0

    # Simple edit distance
    m, n = len(word1), len(word2)
    if m == 0 or n == 0:
        return 0.0

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if word1[i-1] == word2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )

    max_len = max(m, n)
    return 1 - (dp[m][n] / max_len) if max_len > 0 else 0.0

def expand_keywords_with_synonyms(keywords: List[str], synonyms: dict) -> Set[str]:
    """Expand keywords with their synonyms."""
    expanded = set(keywords)
    for keyword in keywords:
        if keyword in synonyms:
            expanded.update(synonyms[keyword])
    return expanded