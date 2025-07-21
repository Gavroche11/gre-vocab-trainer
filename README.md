# GRE Vocabulary Trainer 📚

A modern, interactive GRE vocabulary learning application built with Python and Streamlit. Master GRE words using scientifically-proven spaced repetition algorithms and engaging study modes with intelligent progress tracking.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.47+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Study Modes
- **📇 Flashcard Mode**: Traditional flashcards with spaced repetition - review word definitions at your own pace
- **📝 Quiz Mode**: Multiple-choice questions testing definition recall with immediate feedback
- **📖 Context Mode**: Fill-in-the-blank exercises using real GRE example sentences

### 🧠 Smart Learning System
- **Spaced Repetition Algorithm**: Reviews words at scientifically optimal intervals for long-term retention
- **Adaptive Difficulty Tracking**: Automatically identifies and prioritizes words you struggle with
- **Intelligent Session Building**: Balances new words with review words based on your progress
- **Unique Word Tracking**: Each word entry has a unique ID to prevent conflicts with duplicate words

### 📊 Progress Analytics
- **Comprehensive Statistics**: Track mastery levels, accuracy rates, and study streaks
- **Performance Visualization**: Interactive charts showing your learning progress over time
- **Difficulty Analysis**: Identify your most challenging words with detailed breakdowns
- **Session Summaries**: Review your performance after each study session

### 📁 Data Management
- **Dynamic CSV Upload**: Upload and switch between different vocabulary files during your session
- **Format Validation**: Automatic validation ensures your CSV files are correctly formatted
- **Persistent Progress**: Automatic saving of all progress in `data/gre_progress.json`
- **Export Functionality**: Export difficult words or create custom study sets
- **Word Search**: Quick lookup functionality for any word in your vocabulary set
- **Dark/Light Mode**: Automatic theme detection for comfortable studying

## 🚀 Installation & Deployment

### Local Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Gavroche11/gre-vocab-trainer.git
cd gre-vocab-trainer
```

2. **Create a virtual environment (recommended):**
```bash
# Using conda
conda create -n gre-vocab-trainer python=3.11
conda activate gre-vocab-trainer

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
streamlit run app.py
```

The application will open automatically in your default web browser at `http://localhost:8501`.

### Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in

3. **Deploy the app:**
   - Click "New app"
   - Select your forked repository
   - Set main file path to `app.py`
   - Click "Deploy!"

4. **Upload your vocabulary:**
   - Once deployed, use the sidebar upload feature to add your CSV file
   - The app will validate and load your vocabulary automatically

### Other Deployment Options

tbw

## 📖 Usage Guide

### Getting Started
1. **Load Vocabulary**: Upload your GRE vocabulary CSV file using the sidebar
2. **Choose Study Mode**: Select from Flashcards, Quiz, or Context exercises
3. **Study Consistently**: The app automatically schedules optimal review intervals
4. **Monitor Progress**: Track your mastery with detailed statistics and visualizations

### Study Session Flow
- Each session intelligently combines new words with review words
- Answer accuracy and response time are automatically tracked
- Words you struggle with are scheduled for more frequent review
- Session summaries provide immediate feedback on your performance

### Understanding the Statistics
- **Mastered**: Words with a streak of 3+ correct answers
- **Learning**: Words you're making progress on (1-2 correct streak)
- **Difficult**: Words with high difficulty scores (≥7)
- **Accuracy Rate**: Overall percentage of correct answers

### Using Different CSV Files
- Upload new vocabulary files anytime using the sidebar
- The app automatically validates CSV format and required columns
- Switch between different vocabulary sets while preserving individual progress
- Download the example template if you need help with formatting

## 📋 CSV File Format

Your vocabulary CSV must include these exact column headers:

```csv
word,definition,part_of_speech,example,word_in_sentence,blanked_example,form
```

**Example row:**
```csv
aberrant,markedly different from an accepted norm,adjective,"When the financial director started screaming and throwing food at his co-workers, the police had to come in to deal with his aberrant behavior.",aberrant,"When the financial director started screaming and throwing food at his co-workers, the police had to come in to deal with his <BLANK> behavior.",base
```

**Column descriptions:**
- `word`: The vocabulary word to learn
- `definition`: Clear, concise definition
- `part_of_speech`: Grammar category (noun, verb, adjective, etc.)
- `example`: Complete sentence using the word in context
- `word_in_sentence`: The specific form of the word used in the example
- `blanked_example`: Example sentence with the word replaced by `<BLANK>`
- `form`: Grammatical form used (base, plural, past tense, etc.)

## 🏗️ Project Structure

```
gre-vocabulary-trainer/
├── app.py                    # Main Streamlit application
├── core.py                   # Core logic (WordManager, ProgressTracker, SpacedRepetitionScheduler)
├── utils.py                  # Utility functions (CSV loading, quiz generation, etc.)
├── requirements.txt          # Python dependencies
├── example_vocabulary.csv    # Sample vocabulary file with proper format
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT license
├── README.md                 # This file
└── data/                     # Auto-created directory for progress storage
    └── gre_progress.json     # Your learning progress (auto-generated)
```

## 🔧 Core Components

### WordManager
- Loads and manages vocabulary words with unique ID tracking
- Provides search functionality across words and definitions
- Handles word lookups by unique identifier

### ProgressTracker
- Tracks learning statistics for each word using unique IDs
- Implements spaced repetition scheduling
- Manages study streaks and session history
- Automatically saves progress to JSON file

### SpacedRepetitionScheduler
- Builds intelligent study sessions mixing new and review words
- Prioritizes words based on difficulty and review schedule
- Balances session composition for optimal learning

## 🎨 Customization

### Modifying Spaced Repetition Intervals
Edit the `calculate_next_review` method in `core.py`:
```python
def calculate_next_review(self, correct_count: int, incorrect_count: int, streak: int) -> datetime:
    # Adjust these hour values to change review frequency
    if incorrect_count > correct_count: hours = 4
    elif streak == 0: hours = 12
    elif streak == 1: hours = 24
    # ... continue customizing
```

### Changing Session Size and New Word Ratio
Modify the `get_review_session` parameters in `app.py`:
```python
st.session_state.scheduler.get_review_session(session_size=20, new_words_ratio=0.3)
```

### Styling and Themes
The app includes CSS for both light and dark themes. Modify the styles in `app.py` to customize:
- Color schemes
- Card layouts
- Button styles
- Typography

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear, descriptive commits
4. Add tests if applicable
5. Update documentation as needed
6. Submit a pull request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Write clear docstrings for functions and classes
- Test new features thoroughly
- Update the README if you add new functionality

## 🐛 Troubleshooting

### Common Issues

**"CSV file not found" error:**
- Upload your CSV file using the sidebar file uploader
- Ensure your CSV file has the correct format and required columns
- Check that file encoding is UTF-8
- Try downloading and using the example template

**Progress not saving:**
- Check that the `data/` directory can be created
- Ensure write permissions in the project directory
- Look for error messages in the Streamlit console

**Import errors:**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.11+)
- Try recreating your virtual environment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Spaced repetition algorithm inspired by the SM-2 algorithm
- Example vocabulary includes words commonly found on the GRE (https://s3.amazonaws.com/magoosh.resources/magoosh-gre-1000-words_oct01.pdf)
- Built with ❤️ using Streamlit for the interactive interface
- Progress tracking and analytics powered by Plotly visualizations

## 📞 Support

If you encounter issues or have questions:
- Check the [Issues](https://github.com/Gavroche11/gre-vocab-trainer/issues) page for existing solutions
- Open a new issue with detailed information about your problem
- Contribute improvements back to the community

---

**Happy studying!** 🎓 Build your GRE vocabulary systematically and efficiently with spaced repetition!