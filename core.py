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
    """Manages vocabulary words and their metadata using a unique ID for each."""
    
    def __init__(self, words: List[Dict[str, str]]):
        """
        Initializes the WordManager.

        Args:
            words: A list of word dictionaries, each expected to have a unique 'id'.
        """
        self.words = words
        # Main lookup index using the unique ID.
        self._id_index = {w['id']: w for w in words}
    
    def get_word_by_id(self, word_id: str) -> Optional[Dict[str, str]]:
        """Gets a word dictionary by its unique ID."""
        return self._id_index.get(word_id)
    
    def search_words(self, query: str) -> List[Dict[str, str]]:
        """Searches words by a query string in the word or definition."""
        query_lower = query.lower()
        return [
            w for w in self.words
            if query_lower in w['word'].lower() or query_lower in w['definition'].lower()
        ]


class ProgressTracker:
    """
    Tracks learning progress using the unique word ID as the key.
    """
    
    def __init__(self, progress_file: str = "gre_progress.json"):
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Loads progress from a JSON file."""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'word_stats': {}, 'sessions': [], 'total_reviews': 0, 'streak_days': 0, 'last_session': None}
    
    def save_progress(self):
        """Saves the current progress to a JSON file."""
        os.makedirs(os.path.dirname(self.progress_file) if os.path.dirname(self.progress_file) else '.', exist_ok=True)
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_word_stats(self, word_id: str) -> Dict:
        """Gets or creates statistics for a word using its unique ID."""
        if word_id not in self.progress['word_stats']:
            self.progress['word_stats'][word_id] = {
                'correct': 0, 'incorrect': 0, 'streak': 0, 'last_seen': None,
                'difficulty': 0, 'next_review': None, 'total_time_ms': 0, 'review_count': 0
            }
        return self.progress['word_stats'][word_id]
    
    def calculate_next_review(self, correct_count: int, incorrect_count: int, streak: int) -> datetime:
        """Calculates the next review date based on performance."""
        if incorrect_count > correct_count: hours = 4
        elif streak == 0: hours = 12
        elif streak == 1: hours = 24
        elif streak == 2: hours = 72
        elif streak == 3: hours = 168
        elif streak == 4: hours = 336
        else: hours = 720
        return datetime.now() + timedelta(hours=hours)
    
    def update_word_stats(self, word_id: str, correct: bool, time_ms: int = 0):
        """Updates statistics for a word identified by its unique ID."""
        stats = self.get_word_stats(word_id)
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
        stats['next_review'] = self.calculate_next_review(stats['correct'], stats['incorrect'], stats['streak']).isoformat()
        
        self.progress['total_reviews'] += 1
        self.update_session_info()
        self.save_progress()
    
    def update_session_info(self):
        """Updates session and streak information."""
        now = datetime.now()
        last_session = self.progress.get('last_session')
        if last_session:
            last_date = datetime.fromisoformat(last_session).date()
            today = now.date()
            if today == last_date + timedelta(days=1):
                self.progress['streak_days'] = self.progress.get('streak_days', 0) + 1
            elif today != last_date:
                self.progress['streak_days'] = 1
        else:
            self.progress['streak_days'] = 1
        self.progress['last_session'] = now.isoformat()
    
    def get_due_words(self, word_id_list: List[str]) -> List[str]:
        """Gets a list of word IDs that are due for review."""
        now = datetime.now()
        due_word_ids = []
        for word_id in word_id_list:
            stats = self.get_word_stats(word_id)
            if stats.get('last_seen') is None:
                due_word_ids.append(word_id)
            elif stats.get('next_review'):
                if datetime.fromisoformat(stats['next_review']) <= now:
                    due_word_ids.append(word_id)
        return due_word_ids
    
    def get_statistics(self) -> Dict:
        """Gets comprehensive, aggregated statistics."""
        total_words = len(self.progress['word_stats'])
        if total_words == 0:
            return {'total_words_seen': 0, 'mastered_words': 0, 'learning_words': 0, 'difficult_words': 0,
                    'total_reviews': 0, 'streak_days': 0, 'accuracy_rate': 0, 'average_difficulty': 0}
        
        mastered = sum(1 for s in self.progress['word_stats'].values() if s['streak'] >= 3)
        learning = sum(1 for s in self.progress['word_stats'].values() if 1 <= s['streak'] < 3)
        difficult = sum(1 for s in self.progress['word_stats'].values() if s['difficulty'] >= 7)
        total_correct = sum(s['correct'] for s in self.progress['word_stats'].values())
        total_attempts = sum(s['correct'] + s['incorrect'] for s in self.progress['word_stats'].values())
        accuracy_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        avg_difficulty = sum(s['difficulty'] for s in self.progress['word_stats'].values()) / total_words
        
        return {'total_words_seen': total_words, 'mastered_words': mastered, 'learning_words': learning,
                'difficult_words': difficult, 'total_reviews': self.progress.get('total_reviews', 0),
                'streak_days': self.progress.get('streak_days', 0), 'accuracy_rate': accuracy_rate,
                'average_difficulty': avg_difficulty}

    def get_difficult_words(self, limit: int = 10) -> List[Tuple[str, Dict]]:
        """Gets the most difficult words, returning tuples of (word_id, stats)."""
        words_with_stats = list(self.progress['word_stats'].items())
        words_with_stats.sort(
            key=lambda item: (item[1]['difficulty'], item[1]['incorrect'] / max(1, item[1]['correct'] + item[1]['incorrect'])),
            reverse=True
        )
        return words_with_stats[:limit]


class SpacedRepetitionScheduler:
    """Handles word selection for review sessions using unique word IDs."""
    
    def __init__(self, word_manager: WordManager, progress_tracker: ProgressTracker):
        self.word_manager = word_manager
        self.progress_tracker = progress_tracker
    
    def get_review_session(self, session_size: int = 20, new_words_ratio: float = 0.3) -> List[Dict[str, str]]:
        """Constructs a study session using unique word IDs."""
        all_word_ids = [w['id'] for w in self.word_manager.words]
        known_word_ids = set(self.progress_tracker.progress['word_stats'].keys())
        unseen_word_ids = [word_id for word_id in all_word_ids if word_id not in known_word_ids]
        due_word_ids = self.progress_tracker.get_due_words(list(known_word_ids))
        
        num_new_target = int(session_size * new_words_ratio)
        num_review_target = session_size - num_new_target
        
        session_word_ids = []
        
        if due_word_ids:
            due_with_priority = []
            now = datetime.now()
            for word_id in due_word_ids:
                stats = self.progress_tracker.get_word_stats(word_id)
                overdue_hours = 0
                if stats.get('next_review'):
                    overdue_delta = now - datetime.fromisoformat(stats['next_review'])
                    if overdue_delta.total_seconds() > 0:
                        overdue_hours = overdue_delta.total_seconds() / 3600
                priority = stats.get('difficulty', 0) + (overdue_hours / 24)
                due_with_priority.append((word_id, priority))
            
            due_with_priority.sort(key=lambda x: x[1], reverse=True)
            selected_review_ids = [item[0] for item in due_with_priority[:num_review_target]]
            session_word_ids.extend(selected_review_ids)
        
        if len(session_word_ids) < session_size:
            num_slots_for_new = session_size - len(session_word_ids)
            random.shuffle(unseen_word_ids)
            session_word_ids.extend(unseen_word_ids[:num_slots_for_new])
        
        session_word_dicts = [self.word_manager.get_word_by_id(word_id) for word_id in session_word_ids]
        session_word_dicts = [w for w in session_word_dicts if w is not None] # Filter out any None values
        random.shuffle(session_word_dicts)
        
        return session_word_dicts
