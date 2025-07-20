"""
Utility functions for GRE Vocabulary Trainer
"""

import csv
import re
from typing import Dict, List, Optional
import random


def load_words_from_csv(csv_file: str) -> List[Dict[str, str]]:
    """Load words from CSV file"""
    words = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append({
                'word': row['word'].strip(),
                'definition': row['definition'].strip(),
                'part_of_speech': row['part of speech'].strip(),
                'example': row['example'].strip()
            })
    return words


def create_multiple_choice_options(correct_word: Dict[str, str], 
                                 all_words: List[Dict[str, str]], 
                                 num_options: int = 4,
                                 match_pos: bool = True) -> List[Dict[str, str]]:
    """Create multiple choice options for a quiz"""
    options = [correct_word]
    
    # Filter candidates
    candidates = [w for w in all_words if w['word'] != correct_word['word']]
    
    if match_pos:
        # Try to match part of speech
        pos_matches = [w for w in candidates if w['part_of_speech'] == correct_word['part_of_speech']]
        if len(pos_matches) >= num_options - 1:
            candidates = pos_matches
    
    # Select random options
    num_to_select = min(num_options - 1, len(candidates))
    options.extend(random.sample(candidates, num_to_select))
    
    # Shuffle and return
    random.shuffle(options)
    return options


def create_blanked_sentence(sentence: str, word: str) -> str:
    """Create a fill-in-the-blank sentence by replacing the word"""
    # Create a pattern that matches the word with different cases
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    
    # Replace with blanks
    blanked = pattern.sub('_____', sentence)
    
    # If no replacement was made, try to find partial matches
    if blanked == sentence:
        # Try to find the word as part of another word
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
    difficult_words = []
    
    for word_dict in word_manager.words:
        stats = progress_tracker.get_word_stats(word_dict['word'])
        if stats['difficulty'] >= threshold:
            difficult_words.append({
                **word_dict,
                'difficulty': stats['difficulty'],
                'correct_count': stats['correct'],
                'incorrect_count': stats['incorrect']
            })
    
    # Sort by difficulty
    difficult_words.sort(key=lambda x: x['difficulty'], reverse=True)
    
    # Write to CSV
    if difficult_words:
        fieldnames = ['word', 'definition', 'part_of_speech', 'example', 
                     'difficulty', 'correct_count', 'incorrect_count']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(difficult_words)
    
    return len(difficult_words)


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