"""
Script to fix the keyword extraction by improving the fallback
"""

import re

def fix_keyword_extraction():
    print("🔧 Fixing keyword extraction...")
    
    # Read the file
    with open('google_scholar_research_agent.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the _fallback_keyword_extraction method and improve it
    # Look for the section that creates search queries
    pattern = r'(\s+# Add TF-IDF keywords as search queries\s+if nlp_keywords\.get\("tfidf_keywords"\):\s+search_queries\.extend\(nlp_keywords\["tfidf_keywords"\]\[:5\]\).*?return \{\s+"core_concepts": nlp_keywords\.get\("tfidf_keywords", \[\]\)\[:5\],.*?"fallback_used": True\s+\})'
    
    # The replacement code with proper filtering
    replacement = '''
            # Apply strict filtering to prevent personal names and basic words
            filtered_keywords = []
            basic_words = {'that', 'this', 'with', 'from', 'they', 'have', 'been', 'were', 'will', 'would', 'could', 'should', 'also', 'more', 'most', 'many', 'some', 'such', 'other', 'than', 'very', 'well', 'good', 'best', 'first', 'last', 'new', 'old', 'long', 'short', 'high', 'low', 'big', 'small', 'large', 'great', 'little', 'much', 'same', 'different', 'right', 'left', 'next', 'early', 'late', 'study', 'research', 'include', 'focus', 'examine', 'document'}
            
            # Known problematic personal names
            known_personal_names = {'tretiakov', 'ilia', 'alessandro', 'giuseppe', 'francesco', 'antonio', 'marco', 'andrea', 'stefano', 'fabio', 'simone', 'matteo', 'roberto', 'giovanni', 'luca', 'davide', 'federico', 'miguel', 'jose', 'carlos', 'juan', 'francisco', 'rafael', 'daniel', 'manuel', 'alejandro', 'pedro', 'pablo', 'luis', 'sergio', 'javier', 'fernando', 'alberto', 'jorge', 'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson', 'thomas', 'taylor', 'moore', 'jackson', 'martin'}
            
            # Filter TF-IDF keywords
            for keyword in nlp_keywords.get("tfidf_keywords", []):
                if (keyword.lower() not in basic_words and 
                    keyword.lower() not in known_personal_names and
                    len(keyword) > 3 and
                    not keyword.isdigit() and
                    keyword.replace(' ', '').isalpha()):
                    filtered_keywords.append(keyword)
            
            # Filter bigrams
            for bigram in nlp_keywords.get("bigrams", []):
                if (len(bigram) > 5 and
                    not any(word.lower() in basic_words for word in bigram.split()) and
                    not any(word.lower() in known_personal_names for word in bigram.split()) and
                    bigram.replace(' ', '').isalpha()):
                    filtered_keywords.append(bigram)
            
            # Filter entities (exclude personal names completely)
            for entity in nlp_keywords.get("entities", []):
                if (entity.lower() not in basic_words and
                    entity.lower() not in known_personal_names and
                    len(entity) > 3 and
                    not entity.isdigit() and
                    entity.replace(' ', '').isalpha()):
                    filtered_keywords.append(entity)
            
            # Create academic search queries from filtered keywords
            search_queries = []
            for keyword in filtered_keywords[:6]:  # Limit to 6 best keywords
                # Add academic context to improve search quality
                if len(keyword.split()) == 1:
                    # Single word - add academic context
                    search_queries.append(f'"{keyword}" research')
                else:
                    # Multi-word phrase - use as is
                    search_queries.append(keyword)
            
            # Remove duplicates and limit
            search_queries = list(dict.fromkeys(search_queries))[:5]
            
            logger.warning(f"AI keyword extraction failed, using filtered NLP fallback. Filtered keywords: {filtered_keywords[:8]}")
            logger.info(f"Generated search queries: {search_queries}")
            
            return {
                "core_concepts": filtered_keywords[:5],
                "methodological_terms": [],
                "application_areas": [],
                "theoretical_frameworks": [],
                "search_queries": search_queries,
                "reasoning": "Fallback extraction using filtered NLP techniques with strict personal name and basic word filtering",
                "fallback_used": True
            }'''
    
    # Find the specific section to replace
    # Look for the line with "Add TF-IDF keywords as search queries"
    search_start = content.find("# Add TF-IDF keywords as search queries")
    if search_start == -1:
        print("❌ Could not find the target section to replace")
        return False
    
    # Find the end of the return statement
    search_end = content.find('"fallback_used": True', search_start)
    if search_end == -1:
        print("❌ Could not find the end of the target section")
        return False
    
    # Find the closing brace
    closing_brace = content.find('}', search_end)
    if closing_brace == -1:
        print("❌ Could not find the closing brace")
        return False
    
    # Replace the section
    new_content = content[:search_start] + replacement.strip() + content[closing_brace+1:]
    
    # Write the updated content back
    with open('google_scholar_research_agent.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully updated the keyword extraction fallback")
    return True

if __name__ == "__main__":
    success = fix_keyword_extraction()
    if success:
        print("🎉 Keyword extraction has been fixed!")
    else:
        print("❌ Failed to fix keyword extraction") 