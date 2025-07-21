"""
Utility functions for GRE Vocabulary Trainer
"""

import csv
import re
from typing import Dict, List, Optional, Literal
import random


def validate_csv_format(csv_file: str) -> Dict[str, any]:
    """
    Validate that the CSV file has the correct format and required columns.
    
    Returns:
        Dict with 'valid' boolean and 'error' message if invalid
    """
    required_columns = [
        'word', 'definition', 'part_of_speech', 'example',
        'word_in_sentence', 'blanked_example', 'form'
    ]
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Try to read the first few lines to detect format
            sample = f.read(1024)
            f.seek(0)
            
            # Use csv.Sniffer to detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            # Read the header
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Check if all required columns are present
            if not reader.fieldnames:
                return {'valid': False, 'error': 'No header row found in CSV file'}
            
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                return {
                    'valid': False, 
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }
            
            # Check if there's at least one valid row
            rows_checked = 0
            valid_rows = 0
            
            for row in reader:
                rows_checked += 1
                if rows_checked > 10:  # Check only first 10 rows for validation
                    break
                
                # Check if row has content in required fields
                if (row.get('word', '').strip() and 
                    row.get('definition', '').strip() and
                    row.get('example', '').strip()):
                    valid_rows += 1
            
            if valid_rows == 0:
                return {'valid': False, 'error': 'No valid rows found with required data'}
            
            return {'valid': True, 'error': None}
            
    except UnicodeDecodeError:
        return {'valid': False, 'error': 'File encoding error. Please save your CSV as UTF-8'}
    except csv.Error as e:
        return {'valid': False, 'error': f'CSV format error: {str(e)}'}
    except Exception as e:
        return {'valid': False, 'error': f'Error reading file: {str(e)}'}


def load_words_from_csv(csv_file: str) -> List[Dict[str, str]]:
    """
    Load words from CSV file, assigning a unique ID to each row.
    This ID ensures that every entry, even with identical words, is treated
    as a distinct entity throughout the application.
    """
    words = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for i, row in enumerate(reader):
                # Skip rows with missing essential data
                if not (row.get('word', '').strip() and 
                        row.get('definition', '').strip()):
                    continue
                
                words.append({
                    'id': str(i),  # Assign a unique ID based on row index.
                    'word': row.get('word', '').strip(),
                    'definition': row.get('definition', '').strip(),
                    'part_of_speech': row.get('part_of_speech', '').strip(),
                    'example': row.get('example', '').strip(),
                    'blanked_example': row.get('blanked_example', '').strip(),
                    'word_in_sentence': row.get('word_in_sentence', '').strip(),
                    'form': row.get('form', 'base').strip()
                })
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []
    
    return words

def create_multiple_choice_options(correct_word: Dict[str, str], 
                                 all_words: List[Dict[str, str]], 
                                 num_options: int = 4) -> List[Dict[str, str]]:
    """Create multiple choice options for a quiz"""
    options = [correct_word]
    
    # Filter candidates, ensuring we don't pick the exact same entry.
    candidates = [w for w in all_words if w['id'] != correct_word['id']]
    
    pos_matches = [w for w in candidates if w['part_of_speech'] == correct_word['part_of_speech']]
    if len(pos_matches) >= num_options - 1:
        candidates = pos_matches
    
    num_to_select = min(num_options - 1, len(candidates))
    options.extend(random.sample(candidates, num_to_select))
    
    random.shuffle(options)
    return options


def create_blanked_sentence(sentence: str, word: str) -> str:
    """Create a fill-in-the-blank sentence by replacing the word"""
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    blanked = pattern.sub('_____', sentence)
    if blanked == sentence:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        blanked = pattern.sub('_____', sentence)
    return blanked


def calculate_similarity_score(word1: str, word2: str) -> float:
    """Calculate a simple similarity score between two words"""
    # Convert to lowercase for comparison
    w1, w2 = word1.lower(), word2.lower()
    
    # Check for exact match
    if w1 == w2:
        return 1.0
    
    # Check for substring
    if w1 in w2 or w2 in w1:
        return 0.8
    
    # Check for common prefix
    common_prefix_len = 0
    for i in range(min(len(w1), len(w2))):
        if w1[i] == w2[i]:
            common_prefix_len += 1
        else:
            break
    
    prefix_score = common_prefix_len / max(len(w1), len(w2))
    
    # Check for common suffix
    common_suffix_len = 0
    for i in range(1, min(len(w1), len(w2)) + 1):
        if w1[-i] == w2[-i]:
            common_suffix_len += 1
        else:
            break
    
    suffix_score = common_suffix_len / max(len(w1), len(w2))
    
    return max(prefix_score, suffix_score)


def format_time_ms(milliseconds: int) -> str:
    """Format milliseconds into a readable string"""
    if milliseconds < 1000:
        return f"{milliseconds}ms"
    elif milliseconds < 60000:
        seconds = milliseconds / 1000
        return f"{seconds:.1f}s"
    else:
        minutes = milliseconds / 60000
        return f"{minutes:.1f}m"


def get_difficulty_label(difficulty: float) -> str:
    """Get a human-readable label for difficulty level"""
    if difficulty <= 2:
        return "Easy"
    elif difficulty <= 4:
        return "Medium"
    elif difficulty <= 6:
        return "Hard"
    elif difficulty <= 8:
        return "Very Hard"
    else:
        return "Extremely Hard"


def get_mastery_label(correct: int, incorrect: int, streak: int) -> str:
    """Get a human-readable label for mastery level"""
    if streak >= 5:
        return "Mastered"
    elif streak >= 3:
        return "Almost Mastered"
    elif streak >= 1:
        return "Learning"
    elif correct > incorrect:
        return "Familiar"
    elif incorrect > 0:
        return "Struggling"
    else:
        return "New"


def export_difficult_words(word_manager, progress_tracker, output_file: str, threshold: int = 7):
    """Export difficult words to a CSV file"""
    difficult_words_ids = [
        item[0] for item in progress_tracker.get_difficult_words(limit=None) 
        if item[1].get('difficulty', 0) >= threshold
    ]
    
    difficult_words_data = []
    for word_id in difficult_words_ids:
        word_dict = word_manager.get_word_by_id(word_id)
        if word_dict:
            stats = progress_tracker.get_word_stats(word_id)
            difficult_words_data.append({
                **word_dict,
                'difficulty': stats.get('difficulty', 0),
                'correct_count': stats.get('correct', 0),
                'incorrect_count': stats.get('incorrect', 0)
            })

    if difficult_words_data:
        difficult_words_data.sort(key=lambda x: x['difficulty'], reverse=True)
        fieldnames = ['id', 'word', 'definition', 'part_of_speech', 'example', 
                     'difficulty', 'correct_count', 'incorrect_count']
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(difficult_words_data)
    
    return len(difficult_words_data)


def create_session_summary(words_reviewed: List[Dict[str, str]], 
                         results: List[bool],
                         time_per_word: List[int]) -> Dict:
    """Create a summary of a study session"""
    correct_count = sum(results)
    total_count = len(results)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    total_time_ms = sum(time_per_word)
    avg_time_ms = total_time_ms / total_count if total_count > 0 else 0
    
    # Find fastest and slowest words
    if time_per_word:
        fastest_idx = time_per_word.index(min(time_per_word))
        slowest_idx = time_per_word.index(max(time_per_word))
        
        fastest_word = words_reviewed[fastest_idx]['word'] if fastest_idx < len(words_reviewed) else None
        slowest_word = words_reviewed[slowest_idx]['word'] if slowest_idx < len(words_reviewed) else None
    else:
        fastest_word = None
        slowest_word = None
    
    return {
        'total_words': total_count,
        'correct': correct_count,
        'incorrect': total_count - correct_count,
        'accuracy': accuracy,
        'total_time_ms': total_time_ms,
        'average_time_ms': avg_time_ms,
        'fastest_word': fastest_word,
        'slowest_word': slowest_word,
        'words_reviewed': [w['word'] for w in words_reviewed]
    }