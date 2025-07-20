# GRE Vocabulary Trainer 📚

A modern, interactive GRE vocabulary learning application built with Python and Streamlit. Master GRE words using scientifically-proven spaced repetition algorithms and engaging study modes.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.47+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features ✨

### Study Modes
- **📇 Flashcard Mode**: Traditional flashcards with spaced repetition
- **📝 Quiz Mode**: Multiple-choice questions to test your knowledge
- **📖 Context Mode**: Fill-in-the-blank exercises using example sentences

### Smart Learning
- **Spaced Repetition Algorithm**: Reviews words at optimal intervals for long-term retention
- **Adaptive Difficulty**: Tracks which words you struggle with and prioritizes them
- **Progress Tracking**: Comprehensive statistics on your learning journey
- **Study Streaks**: Motivation through daily streak tracking

### Data Management
- **Import/Export**: Upload your own vocabulary CSV files
- **Export Difficult Words**: Create custom word lists based on difficulty
- **Search Functionality**: Quick lookup of any word in your vocabulary set

## Installation 🚀

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Gavroche11/gre-vocab-trainer.git
cd gre-vocabulary-trainer
```

2. Create a conda environment (recommended):
```bash
conda create -n gre-vocab-trainer python=3.11
conda activate gre-vocab-trainer
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage 📖

### Getting Started
1. **Upload Vocabulary**: Use the sidebar to upload your GRE vocabulary CSV file
2. **Choose Study Mode**: Select from Flashcards, Quiz, or Context mode
3. **Study Daily**: The app will automatically schedule reviews using spaced repetition
4. **Track Progress**: Monitor your mastery and identify difficult words

### CSV File Format
The vocabulary CSV file should have the following columns:
- `word`: The vocabulary word
- `definition`: The word's definition
- `part of speech`: Part of speech (noun, verb, adjective, etc.)
- `example`: An example sentence using the word

Example:
```csv
word,definition,part of speech,example
aberrant,markedly different from an accepted norm,adjective,"When the financial director started screaming and throwing food at his co-workers, the police had to come in to deal with his aberrant behavior."
```

### Data Persistence
Your progress is automatically saved in `data/gre_progress.json`. This file tracks:
- Word statistics (correct/incorrect counts)
- Spaced repetition scheduling
- Study streaks
- Session history

## Project Structure 📁

```
gre-vocabulary-trainer/
├── app.py              # Streamlit application
├── core.py             # Core logic (word management, progress tracking)
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data/              # Progress data directory (created automatically)
│   └── gre_progress.json
└── magoosh_gre_words.csv  # Example vocabulary file (optional)
```

## Deployment 🌐

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

### Deploy to Heroku

tbw

## Customization 🎨

### Modifying Study Algorithms

Edit `core.py` to adjust:
- Spaced repetition intervals
- Difficulty calculations
- Session sizing

### Adding New Study Modes

1. Create new render function in `app.py`
2. Add mode to navigation in `render_sidebar()`
3. Implement mode logic

### Styling

Modify the CSS in `app.py` to change:
- Color schemes
- Card layouts
- Button styles

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Inspired by popular GRE prep platforms like Magoosh
- Spaced repetition algorithm based on SM-2
- Built with ❤️ using Streamlit

## Support 💬

If you have any questions or run into issues:
- Open an issue on GitHub
- Check existing issues for solutions
- Contribute improvements back to the community

---

Happy studying! 🎓 May your GRE vocabulary be ever expanding!