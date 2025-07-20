"""
Core module for GRE Vocabulary Trainer
Handles word management, progress tracking, and spaced repetition logic
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random


class WordManager:
    """Manages vocabulary words and their metadata"""
    
    def __init__(self, words: List[Dict[str, str]]):
        self.words = words
        self._word_index = {w['word']: w for w in words}
    
    def get_word(self, word: str) -> Optional[Dict[str, str]]:
        """Get a word by its name"""
        return self._word_index.get(word)
    
    def get_random_words(self, count: int, exclude: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """Get random words, optionally excluding some"""
        exclude = exclude or []
        available = [w for w in self.words if w['word'] not in exclude]
        return random.sample(available, min(count, len(available)))
    
    def get_words_by_pos(self, part_of_speech: str) -> List[Dict[str, str]]:
        """Get all words with a specific part of speech"""
        return [w for w in self.words if w['part_of_speech'] == part_of_speech]
    
    def search_words(self, query: str) -> List[Dict[str, str]]:
        """Search words by partial match in word or definition"""
        query_lower = query.lower()
        return [
            w for w in self.words
            if query_lower in w['word'].lower() or query_lower in w['definition'].lower()
        ]


class ProgressTracker:
    """Tracks learning progress and implements spaced repetition"""
    
    def __init__(self, progress_file: str = "gre_progress.json"):
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'word_stats': {},
            'sessions': [],
            'total_reviews': 0,
            'streak_days': 0,
            'last_session': None
        }
    
    def save_progress(self):
        """Save progress to file"""
        os.makedirs(os.path.dirname(self.progress_file) if os.path.dirname(self.progress_file) else '.', exist_ok=True)
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_word_stats(self, word: str) -> Dict:
        """Get or create stats for a word"""
        if word not in self.progress['word_stats']:
            self.progress['word_stats'][word] = {
                'correct': 0,
                'incorrect': 0,
                'streak': 0,
                'last_seen': None,
                'difficulty': 0,
                'next_review': None,
                'total_time_ms': 0,
                'review_count': 0
            }
        return self.progress['word_stats'][word]
    
    def calculate_next_review(self, correct_count: int, incorrect_count: int, streak: int) -> datetime:
        """Calculate next review date using spaced repetition algorithm"""
        if incorrect_count > correct_count:
            hours = 4
        elif streak == 0:
            hours = 12
        elif streak == 1:
            hours = 24
        elif streak == 2:
            hours = 72
        elif streak == 3:
            hours = 168  # 1 week
        elif streak == 4:
            hours = 336  # 2 weeks
        else:
            hours = 720  # 1 month
        
        return datetime.now() + timedelta(hours=hours)
    
    def update_word_stats(self, word: str, correct: bool, time_ms: int = 0):
        """Update statistics for a word"""
        stats = self.get_word_stats(word)
        
        if correct:
            stats['correct'] += 1
            stats['streak'] += 1
            stats['difficulty'] = max(0, stats['difficulty'] - 1)
        else:
            stats['incorrect'] += 1
            stats['streak'] = 0
            stats['difficulty'] = min(10, stats['difficulty'] + 2)
        
        stats['last_seen'] = datetime.now().isoformat()
        stats['total_time_ms'] += time_ms
        stats['review_count'] += 1
        
        # Calculate next review
        next_review = self.calculate_next_review(
            stats['correct'], 
            stats['incorrect'], 
            stats['streak']
        )
        stats['next_review'] = next_review.isoformat()
        
        self.progress['total_reviews'] += 1
        self.update_session_info()
        self.save_progress()
    
    def update_session_info(self):
        """Update session and streak information"""
        now = datetime.now()
        last_session = self.progress.get('last_session')
        
        if last_session:
            last_date = datetime.fromisoformat(last_session).date()
            today = now.date()
            
            if today == last_date:
                pass  # Same day, no streak change
            elif today == last_date + timedelta(days=1):
                self.progress['streak_days'] += 1
            else:
                self.progress['streak_days'] = 1
        else:
            self.progress['streak_days'] = 1
        
        self.progress['last_session'] = now.isoformat()
        
        # Add session record
        self.progress['sessions'].append({
            'date': now.isoformat(),
            'reviews': 1
        })
    
    def get_due_words(self, word_list: List[str]) -> List[str]:
        """Get words that are due for review"""
        now = datetime.now()
        due_words = []
        
        for word in word_list:
            stats = self.get_word_stats(word)
            if stats['last_seen'] is None:
                due_words.append(word)
            elif stats['next_review']:
                next_review = datetime.fromisoformat(stats['next_review'])
                if next_review <= now:
                    due_words.append(word)
        
        return due_words
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        total_words = len(self.progress['word_stats'])
        
        if total_words == 0:
            return {
                'total_words_seen': 0,
                'mastered_words': 0,
                'learning_words': 0,
                'difficult_words': 0,
                'total_reviews': 0,
                'streak_days': 0,
                'accuracy_rate': 0,
                'average_difficulty': 0
            }
        
        mastered = sum(1 for stats in self.progress['word_stats'].values() 
                      if stats['streak'] >= 3)
        learning = sum(1 for stats in self.progress['word_stats'].values() 
                      if 1 <= stats['streak'] < 3)
        difficult = sum(1 for stats in self.progress['word_stats'].values() 
                       if stats['difficulty'] >= 7)
        
        total_correct = sum(stats['correct'] for stats in self.progress['word_stats'].values())
        total_attempts = sum(stats['correct'] + stats['incorrect'] 
                           for stats in self.progress['word_stats'].values())
        
        accuracy_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        avg_difficulty = sum(stats['difficulty'] for stats in self.progress['word_stats'].values()) / total_words
        
        return {
            'total_words_seen': total_words,
            'mastered_words': mastered,
            'learning_words': learning,
            'difficult_words': difficult,
            'total_reviews': self.progress['total_reviews'],
            'streak_days': self.progress['streak_days'],
            'accuracy_rate': accuracy_rate,
            'average_difficulty': avg_difficulty,
            'total_correct': total_correct,
            'total_attempts': total_attempts
        }
    
    def get_difficult_words(self, limit: int = 10) -> List[Tuple[str, Dict]]:
        """Get the most difficult words"""
        words_with_stats = [
            (word, stats) for word, stats in self.progress['word_stats'].items()
        ]
        
        # Sort by difficulty, then by error rate
        words_with_stats.sort(
            key=lambda x: (
                x[1]['difficulty'], 
                x[1]['incorrect'] / max(1, x[1]['correct'] + x[1]['incorrect'])
            ),
            reverse=True
        )
        
        return words_with_stats[:limit]


class SpacedRepetitionScheduler:
    """Handles the selection of words for review based on spaced repetition"""
    
    def __init__(self, word_manager: WordManager, progress_tracker: ProgressTracker):
        self.word_manager = word_manager
        self.progress_tracker = progress_tracker
    
    def get_review_session(self, session_size: int = 20, 
                          new_words_ratio: float = 0.3) -> List[Dict[str, str]]:
        """Get a session of words to review"""
        all_word_names = [w['word'] for w in self.word_manager.words]
        due_words = self.progress_tracker.get_due_words(all_word_names)
        
        # Separate into seen and unseen words
        seen_words = []
        unseen_words = []
        
        for word in all_word_names:
            stats = self.progress_tracker.get_word_stats(word)
            if stats['last_seen'] is None:
                unseen_words.append(word)
            elif word in due_words:
                seen_words.append(word)
        
        # Calculate how many new words to include
        new_words_count = int(session_size * new_words_ratio)
        review_words_count = session_size - new_words_count
        
        # Select words for the session
        session_words = []
        
        # Add due words (prioritize by difficulty and how overdue they are)
        if seen_words:
            seen_words_with_priority = []
            now = datetime.now()
            
            for word in seen_words:
                stats = self.progress_tracker.get_word_stats(word)
                if stats['next_review']:
                    overdue_hours = (now - datetime.fromisoformat(stats['next_review'])).total_seconds() / 3600
                else:
                    overdue_hours = 0
                
                priority = stats['difficulty'] + overdue_hours / 24  # Combine difficulty with how overdue
                seen_words_with_priority.append((word, priority))
            
            seen_words_with_priority.sort(key=lambda x: x[1], reverse=True)
            selected_seen = [w[0] for w in seen_words_with_priority[:review_words_count]]
            session_words.extend(selected_seen)
        
        # Add new words
        if unseen_words and len(session_words) < session_size:
            remaining_slots = session_size - len(session_words)
            selected_new = random.sample(unseen_words, min(remaining_slots, len(unseen_words)))
            session_words.extend(selected_new)
        
        # Convert word names to word dictionaries and shuffle
        session_word_dicts = [self.word_manager.get_word(w) for w in session_words]
        random.shuffle(session_word_dicts)
        
        return session_word_dicts