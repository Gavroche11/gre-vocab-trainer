"""
Streamlit app for GRE Vocabulary Trainer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

from core import WordManager, ProgressTracker, SpacedRepetitionScheduler
from utils import (
    load_words_from_csv, 
    create_multiple_choice_options,
    get_difficulty_label,
    get_mastery_label,
    format_time_ms,
    create_session_summary,
    export_difficult_words
)


# Page configuration
st.set_page_config(
    page_title="GRE Vocabulary Trainer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with dark mode support
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        margin-bottom: 10px;
    }
    
    /* Light mode word card */
    @media (prefers-color-scheme: light) {
        .word-card {
            background-color: #f0f2f6;
            color: #000000;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #e0e0e0;
        }
        .word-card h2, .word-card h3 {
            color: #000000;
        }
    }
    
    /* Dark mode word card */
    @media (prefers-color-scheme: dark) {
        .word-card {
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #404040;
        }
        .word-card h2, .word-card h3 {
            color: #ffffff;
        }
    }
    
    /* Streamlit's native dark mode detection */
    [data-testid="stAppViewContainer"][data-theme="dark"] .word-card {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .word-card h2,
    [data-testid="stAppViewContainer"][data-theme="dark"] .word-card h3 {
        color: #ffffff;
    }
    
    .correct-answer {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
    }
    .incorrect-answer {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Keyboard shortcut hints */
    .keyboard-hint {
        display: inline-block;
        background-color: #e9ecef;
        color: #495057;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 0.85em;
        margin-left: 5px;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .keyboard-hint {
        background-color: #2d3748;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'word_manager' not in st.session_state:
        # Check if CSV file exists
        csv_file = "words_revised.csv"
        if os.path.exists(csv_file):
            words = load_words_from_csv(csv_file)
            st.session_state.word_manager = WordManager(words)
        else:
            st.error(f"CSV file '{csv_file}' not found. Please upload it.")
            st.session_state.word_manager = None
    
    if 'progress_tracker' not in st.session_state:
        st.session_state.progress_tracker = ProgressTracker("data/gre_progress.json")
    
    if 'scheduler' not in st.session_state and st.session_state.word_manager:
        st.session_state.scheduler = SpacedRepetitionScheduler(
            st.session_state.word_manager,
            st.session_state.progress_tracker
        )
    
    # Study session state
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = None
    if 'session_words' not in st.session_state:
        st.session_state.session_words = []
    if 'current_word_idx' not in st.session_state:
        st.session_state.current_word_idx = 0
    if 'session_results' not in st.session_state:
        st.session_state.session_results = []
    if 'session_times' not in st.session_state:
        st.session_state.session_times = []
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = None
    if 'quiz_answer_state' not in st.session_state:
        st.session_state.quiz_answer_state = None
    if 'quiz_options' not in st.session_state:
        st.session_state.quiz_options = None
    if 'quiz_word' not in st.session_state:
        st.session_state.quiz_word = None
    if 'context_answer_state' not in st.session_state:
        st.session_state.context_answer_state = None
    if 'context_options' not in st.session_state:
        st.session_state.context_options = None
    if 'context_word' not in st.session_state:
        st.session_state.context_word = None
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    


def render_sidebar():
    """Render the sidebar with navigation and stats"""
    with st.sidebar:
        st.title("📚 GRE Vocab Trainer")
        
        # Quick stats
        if st.session_state.word_manager:
            stats = st.session_state.progress_tracker.get_statistics()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Words Studied", stats['total_words_seen'])
                st.metric("Accuracy", f"{stats['accuracy_rate']:.1f}%")
            with col2:
                st.metric("Day Streak", f"{stats['streak_days']} 🔥")
                st.metric("Mastered", stats['mastered_words'])
        
        st.divider()
        
        # Navigation
        st.subheader("Study Modes")
        
        if st.button("📇 Flashcard mode", type="primary"):
            start_study_session("flashcard")
        
        if st.button("📝 Quiz Mode", type="primary"):
            start_study_session("quiz")
        
        if st.button("📖 Context Mode", type="primary"):
            start_study_session("context")
        
        st.divider()
        
        st.subheader("Tools")
        
        if st.button("📊 Statistics"):
            st.session_state.current_mode = "statistics"
        
        if st.button("🔍 Word Search"):
            st.session_state.current_mode = "search"
        
        if st.button("📤 Export Difficult Words"):
            st.session_state.current_mode = "export"
        
        st.divider()
        
        # File upload
        st.subheader("Data Management")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file is not None:
            # Save the uploaded file
            with open("magoosh_gre_words.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File uploaded successfully!")
            # Reload the app
            st.rerun()


def start_study_session(mode: str):
    """Start a new study session."""
    st.session_state.current_mode = mode
    st.session_state.session_words = st.session_state.scheduler.get_review_session(20)
    st.session_state.current_word_idx = 0
    st.session_state.session_results = []
    st.session_state.session_times = []
    st.session_state.show_answer = False
    st.session_state.question_start_time = time.time()
    st.session_state.quiz_answer_state = None
    st.session_state.context_answer_state = None


def render_flashcard_mode():
    """Render flashcard study mode"""
    if not st.session_state.session_words:
        st.error("No words to review!")
        return
    
    word_dict = st.session_state.session_words[st.session_state.current_word_idx]
    progress = st.session_state.current_word_idx + 1
    total = len(st.session_state.session_words)
    
    # Progress bar
    st.progress(progress / total)
    st.write(f"Card {progress} of {total}")
    
    # Word card
    st.markdown(f"""
    <div class="word-card">
        <h2>{word_dict['word']}</h2>
        <p><em>{word_dict['part_of_speech']}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_answer:
            if st.button("Show Definition", key="show_def"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            # Show definition and example
            st.markdown(f"""
            <div style="margin-top: 20px;">
                <h4>Definition:</h4>
                <p>{word_dict['definition']}</p>
                <h4>Example:</h4>
                <p><em>{word_dict['example']}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Response buttons
            st.write("Did you know this word?")
            col_yes, col_no = st.columns(2)
            
            with col_yes:
                if st.button("✅ Yes", key="yes_btn"):
                    record_answer(True)
                    st.rerun()
            
            with col_no:
                if st.button("❌ No", key="no_btn"):
                    record_answer(False)
                    st.rerun()


def render_quiz_mode():
    """Render multiple choice quiz mode"""
    if not st.session_state.session_words:
        st.error("No words to review!")
        return

    # Check if an answer has been submitted for the current question
    if st.session_state.quiz_answer_state:
        # If yes, display the result
        state = st.session_state.quiz_answer_state
        word_dict = state['word_dict']
        is_correct = state['is_correct']

        # Redisplay the question card
        st.markdown(f"""
        <div class="word-card">
            <h3>What is the definition of:</h3>
            <h2>{word_dict['word']}</h2>
            <p><em>{word_dict['part_of_speech']}</em></p>
        </div>
        """, unsafe_allow_html=True)

        # Display the result message
        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct definition was: {word_dict['definition']}")
            st.info(f"Example: {word_dict['example']}")

        # Display a button to move to the next question
        if st.button("Next Question", key="next_quiz_q"):
            st.session_state.quiz_answer_state = None
            st.rerun()
        return

    # If no answer has been submitted, display the current question
    word_dict = st.session_state.session_words[st.session_state.current_word_idx]
    progress = st.session_state.current_word_idx + 1
    total = len(st.session_state.session_words)

    # Progress bar
    st.progress(progress / total)
    st.write(f"Question {progress} of {total}")

    # Question card
    st.markdown(f"""
    <div class="word-card">
        <h3>What is the definition of:</h3>
        <h2>{word_dict['word']}</h2>
        <p><em>{word_dict['part_of_speech']}</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Create and display options
    if st.session_state.quiz_word != word_dict['word']:
        st.session_state.quiz_options = create_multiple_choice_options(
            word_dict,
            st.session_state.word_manager.words,
            num_options=4,
        )
        st.session_state.quiz_word = word_dict['word']
    options = st.session_state.quiz_options

    for i, option in enumerate(options):
        btn_label = f"{chr(65+i)}. {option['definition']}"
        if st.button(btn_label, key=f"option_{i}"):
            is_correct = option['word'] == word_dict['word']

            # Record the answer BUT DO NOT ADVANCE THE WORD YET.
            # We advance the word when "Next Question" is clicked.
            record_answer(is_correct)

            # Store the result in the session state
            st.session_state.quiz_answer_state = {
                'is_correct': is_correct,
                'word_dict': word_dict
            }

            # Rerun to show the result message
            st.rerun()


def render_context_mode():
    """Render context/fill-in-the-blank mode"""
    if not st.session_state.session_words:
        st.error("No words to review!")
        return

    # Check if an answer has been submitted for the current question
    if st.session_state.context_answer_state:
        # If yes, display the result
        state = st.session_state.context_answer_state
        word_dict = state['word_dict']
        is_correct = state['is_correct']
        blanked_example = word_dict["blanked_example"].replace("<BLANK>", "_____")

        # Redisplay the question card
        st.markdown(f"""
        <div class="word-card">
            <h3>Fill in the blank:</h3>
            <p style="font-size: 1.2em;">{blanked_example}</p>
            <p><em>{word_dict['part_of_speech']}; {word_dict['form']}</em></p>
        </div>
        """, unsafe_allow_html=True)

        # Display the result message
        if is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer was: {word_dict['word']}")
        
        st.info(f"Full sentence: {word_dict['example']}")
        st.info(f"Definition: {word_dict['definition']}")

        # Display a button to move to the next question
        if st.button("Next Question", key="next_context"):
            st.session_state.context_answer_state = None
            st.rerun()
        return

    # If no answer has been submitted, display the current question
    word_dict = st.session_state.session_words[st.session_state.current_word_idx]
    progress = st.session_state.current_word_idx + 1
    total = len(st.session_state.session_words)

    # Progress bar
    st.progress(progress / total)
    st.write(f"Question {progress} of {total}")

    # Create and display the blanked sentence
    blanked_example = word_dict["blanked_example"].replace("<BLANK>", "_____")
    
    st.markdown(f"""
    <div class="word-card">
        <h3>Fill in the blank:</h3>
        <p style="font-size: 1.2em;">{blanked_example}</p>
        <p><em>{word_dict['part_of_speech']}; {word_dict['form']}</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Create and display options
    if st.session_state.context_word != word_dict['word']:
        st.session_state.context_options = create_multiple_choice_options(
            word_dict,
            st.session_state.word_manager.words,
            num_options=4
        )
        st.session_state.context_word = word_dict['word']
    options = st.session_state.context_options

    for i, option in enumerate(options):
        btn_label = f"{chr(65+i)}. {option['word']}"
        if st.button(btn_label, key=f"context_option_{i}"):
            is_correct = option['word'] == word_dict['word']
            
            # Record the user's answer
            record_answer(is_correct)
            
            # Store the result in the session state to be displayed on the next run
            st.session_state.context_answer_state = {
                'is_correct': is_correct,
                'word_dict': word_dict
            }
            
            # Rerun the script to show the result message
            st.rerun()


def record_answer(correct: bool):
    """Record the answer and update progress using the word's unique ID."""
    time_taken = int((time.time() - st.session_state.question_start_time) * 1000)
    st.session_state.session_times.append(time_taken)
    st.session_state.session_results.append(correct)
    
    # Use the unique ID from the word dictionary for tracking.
    current_word = st.session_state.session_words[st.session_state.current_word_idx]
    word_id = current_word['id']
    
    st.session_state.progress_tracker.update_word_stats(word_id, correct, time_taken)
    
    # Advance to the next word.
    st.session_state.current_word_idx += 1
    st.session_state.show_answer = False
    st.session_state.question_start_time = time.time()
    
    if st.session_state.current_word_idx >= len(st.session_state.session_words):
        st.session_state.current_mode = "session_complete"


def render_session_complete():
    """Render session completion screen"""
    st.balloons()
    st.success("🎉 Session Complete!")
    
    # Create session summary
    summary = create_session_summary(
        st.session_state.session_words,
        st.session_state.session_results,
        st.session_state.session_times
    )
    
    # Display summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Accuracy", f"{summary['accuracy']:.1f}%")
        st.metric("Words Reviewed", summary['total_words'])
    
    with col2:
        st.metric("Correct", summary['correct'], delta=f"+{summary['correct']}")
        st.metric("Incorrect", summary['incorrect'], delta=f"-{summary['incorrect']}")
    
    with col3:
        st.metric("Avg Time/Word", format_time_ms(int(summary['average_time_ms'])))
        st.metric("Total Time", format_time_ms(summary['total_time_ms']))
    
    # Show word-by-word results
    st.subheader("Word-by-Word Results")
    
    results_df = pd.DataFrame({
        'Word': [w['word'] for w in st.session_state.session_words],
        'Result': ['✅ Correct' if r else '❌ Incorrect' for r in st.session_state.session_results],
        'Time': [format_time_ms(t) for t in st.session_state.session_times],
        'Definition': [w['definition'] for w in st.session_state.session_words]
    })
    
    st.dataframe(results_df, use_container_width=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📇 New Flashcard Session"):
            start_study_session("flashcard")
            st.rerun()
    
    with col2:
        if st.button("📝 New Quiz Session"):
            start_study_session("quiz")
            st.rerun()
    
    with col3:
        if st.button("📖 New Context Session"):
            start_study_session("context")
            st.rerun()


def render_statistics():
    """Render the statistics dashboard, using word IDs for lookups."""
    st.title("📊 Learning Statistics")
    stats = st.session_state.progress_tracker.get_statistics()
    
    # Overview metrics (no changes needed here)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Words Studied", stats['total_words_seen'], f"of {len(st.session_state.word_manager.words)}")
    with col2: st.metric("Mastered Words", stats['mastered_words'], f"{stats['mastered_words']/len(st.session_state.word_manager.words)*100:.1f}%" if len(st.session_state.word_manager.words) > 0 else "")
    with col3: st.metric("Overall Accuracy", f"{stats['accuracy_rate']:.1f}%")
    with col4: st.metric("Study Streak", f"{stats['streak_days']} days 🔥")
    st.divider()
    
    # Charts (no changes needed here)
    col1, col2 = st.columns(2)
    
    with col1:
        # Mastery distribution
        mastery_data = {
            'Status': ['Mastered', 'Learning', 'New', 'Difficult'],
            'Count': [
                stats['mastered_words'],
                stats['learning_words'],
                len(st.session_state.word_manager.words) - stats['total_words_seen'],
                stats['difficult_words']
            ]
        }
        
        fig_mastery = px.pie(
            mastery_data, 
            values='Count', 
            names='Status',
            title='Word Mastery Distribution',
            color_discrete_map={
                'Mastered': '#28a745',
                'Learning': '#ffc107',
                'New': '#17a2b8',
                'Difficult': '#dc3545'
            }
        )
        st.plotly_chart(fig_mastery, use_container_width=True)
    
    with col2:
        # Study activity over time
        sessions = st.session_state.progress_tracker.progress.get('sessions', [])
        if sessions:
            session_df = pd.DataFrame(sessions)
            session_df['date'] = pd.to_datetime(session_df['date']).dt.date
            daily_reviews = session_df.groupby('date')['reviews'].sum().reset_index()
            
            fig_activity = px.bar(
                daily_reviews,
                x='date',
                y='reviews',
                title='Daily Study Activity',
                labels={'reviews': 'Words Reviewed', 'date': 'Date'}
            )
            st.plotly_chart(fig_activity, use_container_width=True)

    st.subheader("Most Difficult Words")
    # This method now returns a list of (word_id, stats_dict)
    difficult_words = st.session_state.progress_tracker.get_difficult_words(10)
    
    if difficult_words:
        diff_data = []
        for word_id, stats in difficult_words:
            # Use the ID to get the full word details.
            word_dict = st.session_state.word_manager.get_word_by_id(word_id)
            if word_dict:
                total_attempts = stats.get('correct', 0) + stats.get('incorrect', 0)
                accuracy = f"{stats['correct'] / total_attempts * 100:.0f}%" if total_attempts > 0 else "N/A"
                diff_data.append({
                    'Word': word_dict['word'],
                    'Part of Speech': word_dict['part_of_speech'],
                    'Definition': word_dict['definition'],
                    'Difficulty': get_difficulty_label(stats.get('difficulty', 0)),
                    'Accuracy': accuracy
                })
        if diff_data:
            st.dataframe(pd.DataFrame(diff_data), use_container_width=True)



def render_word_search():
    """Render word search interface, using word IDs for stats lookup."""
    st.title("🔍 Word Search")
    search_query = st.text_input("Search for a word or definition:", key="search_input")
    
    if search_query:
        results = st.session_state.word_manager.search_words(search_query)
        if results:
            st.write(f"Found {len(results)} matching words:")
            for word_dict in results:
                # Use the unique ID of the specific entry to get its stats.
                word_id = word_dict['id']
                stats = st.session_state.progress_tracker.get_word_stats(word_id)
                
                with st.expander(f"{word_dict['word']} ({word_dict['part_of_speech']}) - {word_dict['definition'][:30]}..."):
                    st.write(f"**Definition:** {word_dict['definition']}")
                    st.write(f"**Example:** *{word_dict['example']}*")
                    if stats['last_seen']:
                        col1, col2, col3 = st.columns(3)
                        with col1: st.metric("Mastery", get_mastery_label(stats['correct'], stats['incorrect'], stats['streak']))
                        with col2: st.metric("Accuracy", f"{stats['correct']/(stats['correct']+stats['incorrect'])*100:.0f}%" if (stats['correct']+stats['incorrect']) > 0 else "N/A")
                        with col3: st.metric("Difficulty", get_difficulty_label(stats['difficulty']))
        else:
            st.info("No matching words found.")


def render_export():
    """Render export interface."""
    st.title("📤 Export Difficult Words")
    st.write("Export words above a certain difficulty threshold to a CSV file.")
    difficulty_threshold = st.slider("Difficulty Threshold", min_value=1, max_value=10, value=7)
    if st.button("Export to CSV"):
        from datetime import datetime
        output_file = f"difficult_words_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        count = export_difficult_words(
            st.session_state.word_manager,
            st.session_state.progress_tracker,
            output_file,
            difficulty_threshold
        )
        if count > 0:
            st.success(f"Exported {count} difficult words to {output_file}")
            with open(output_file, 'r', encoding='utf-8') as f:
                st.download_button("Download CSV", f.read(), file_name=output_file, mime="text/csv")
        else:
            st.info(f"No words found with difficulty >= {difficulty_threshold}")


def main():
    """Main app function"""
    init_session_state()
    render_sidebar()
    
    # Check if word manager is loaded
    if not st.session_state.get('word_manager'):
        st.error("Please upload the GRE vocabulary CSV file using the sidebar.")
        return
    
    # Render current mode
    if st.session_state.current_mode == "flashcard":
        render_flashcard_mode()
    elif st.session_state.current_mode == "quiz":
        render_quiz_mode()
    elif st.session_state.current_mode == "context":
        render_context_mode()
    elif st.session_state.current_mode == "session_complete":
        render_session_complete()
    elif st.session_state.current_mode == "statistics":
        render_statistics()
    elif st.session_state.current_mode == "search":
        render_word_search()
    elif st.session_state.current_mode == "export":
        render_export()
    else:
        # Welcome screen
        st.title("📚 Welcome to GRE Vocabulary Trainer")
        st.write("Master GRE vocabulary with spaced repetition and interactive exercises!")
        
        st.info("""
        ### How to get started:
        1. Choose a study mode from the sidebar
        2. Review words using flashcards, quizzes, or context exercises
        3. Track your progress with detailed statistics
        4. Focus on difficult words with smart scheduling
        """)
        
        # Quick start buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📇 Flashcard mode", type="primary", use_container_width=True):
                start_study_session("flashcard")
                st.rerun()
        
        with col2:
            if st.button("📝 Quiz mode", type="primary", use_container_width=True):
                start_study_session("quiz")
                st.rerun()
        
        with col3:
            if st.button("📖 Context mode", type="primary", use_container_width=True):
                start_study_session("context")
                st.rerun()


if __name__ == "__main__":
    main()