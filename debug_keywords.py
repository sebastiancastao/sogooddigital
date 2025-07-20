"""
Debug script to test keyword extraction filtering
"""

import json
import re
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def test_keyword_filtering():
    print("🔍 Testing Keyword Filtering Debug")
    print("=" * 50)
    
    # Test content (simulating what might be in the Google Doc)
    test_content = """
    This research document examines artificial intelligence applications in business.
    The study by Dr. Ilia Tretiakov focuses on machine learning algorithms and their
    impact on business intelligence systems. The research methodology includes
    neural network analysis and deep learning frameworks for automated decision making.
    Alessandro Giuseppe and Francesco Antonio contributed to the research with
    neural network optimization techniques that enhance performance.
    """
    
    try:
        # Initialize NLP tools
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        
        print("\n🔬 Testing current NLP keyword extraction...")
        
        # Clean and tokenize text
        cleaned_text = re.sub(r'[^\w\s]', ' ', test_content)
        tokens = word_tokenize(cleaned_text.lower())
        
        # Show all tokens
        print(f"📋 All tokens: {tokens}")
        
        # Remove stopwords and get lemmatized tokens
        filtered_tokens = [
            lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in stop_words and len(token) > 2
        ]
        
        print(f"📋 Filtered tokens (current): {filtered_tokens}")
        
        # Test with improved filtering
        print("\n🔧 Testing improved filtering...")
        
        # Define comprehensive filter lists
        basic_words = {'that', 'this', 'with', 'from', 'they', 'have', 'been', 'were', 'will', 'would', 'could', 'should', 'also', 'more', 'most', 'many', 'some', 'such', 'other', 'than', 'very', 'well', 'good', 'best', 'first', 'last', 'new', 'old', 'long', 'short', 'high', 'low', 'big', 'small', 'large', 'great', 'little', 'much', 'same', 'different', 'right', 'left', 'next', 'early', 'late', 'study', 'research', 'include', 'focus', 'examine', 'document'}
        
        # Known problematic personal names
        known_personal_names = {'tretiakov', 'ilia', 'alessandro', 'giuseppe', 'francesco', 'antonio', 'marco', 'andrea', 'stefano', 'fabio', 'simone', 'matteo', 'roberto', 'giovanni', 'luca', 'davide', 'federico', 'miguel', 'jose', 'carlos', 'juan', 'francisco', 'rafael', 'daniel', 'manuel', 'alejandro', 'pedro', 'pablo', 'luis', 'sergio', 'javier', 'fernando', 'alberto', 'jorge', 'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson', 'thomas', 'taylor', 'moore', 'jackson', 'martin'}
        
        # Apply improved filtering
        improved_filtered_tokens = []
        for token in tokens:
            lemmatized = lemmatizer.lemmatize(token)
            if (token not in stop_words and 
                token.lower() not in basic_words and 
                token.lower() not in known_personal_names and
                len(token) > 3 and  # Minimum 4 characters for academic terms
                not token.isdigit() and
                lemmatized.isalpha()):  # Only alphabetic terms
                improved_filtered_tokens.append(lemmatized)
        
        print(f"📋 Improved filtered tokens: {improved_filtered_tokens}")
        
        # Test TF-IDF extraction
        print("\n🔍 Testing TF-IDF keyword extraction...")
        
        # Custom stopwords including basic words and names
        academic_stopwords = list(stop_words) + list(basic_words) + list(known_personal_names)
        
        try:
            vectorizer = TfidfVectorizer(
                max_features=20, 
                stop_words=academic_stopwords,
                min_df=1,
                ngram_range=(1, 2),  # Include both unigrams and bigrams
                token_pattern=r'\b[a-zA-Z]{4,}\b'  # Minimum 4 characters, alphabetic only
            )
            
            tfidf_matrix = vectorizer.fit_transform([test_content])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            print(f"📊 TF-IDF keywords: {[kw for kw, score in keyword_scores[:10]]}")
            
        except Exception as e:
            print(f"❌ TF-IDF extraction failed: {e}")
        
        # Simulate search queries
        print("\n🔍 Generating academic search queries...")
        
        # Create academic search queries from improved keywords
        search_queries = []
        for keyword in improved_filtered_tokens[:6]:  # Limit to 6 best keywords
            if len(keyword) > 4:  # Focus on meaningful terms
                search_queries.append(f'"{keyword}" research')
        
        print(f"📋 Generated search queries: {search_queries}")
        
        # Create the proper fallback result
        fallback_result = {
            "core_concepts": improved_filtered_tokens[:5],
            "methodological_terms": [],
            "application_areas": [],
            "theoretical_frameworks": [],
            "search_queries": search_queries[:5],
            "reasoning": "Improved fallback extraction with strict filtering",
            "fallback_used": True
        }
        
        print(f"\n✅ Improved fallback result:")
        print(json.dumps(fallback_result, indent=2))
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keyword_filtering() 