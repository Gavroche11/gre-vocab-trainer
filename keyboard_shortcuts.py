"""
Keyboard shortcuts component for Streamlit app
This module provides keyboard navigation functionality
"""

import streamlit as st
import streamlit.components.v1 as components


def inject_keyboard_shortcuts():
    """Inject JavaScript for keyboard shortcuts into the Streamlit app"""
    
    keyboard_js = """
    <script>
    // Wait for the DOM to be ready
    (function() {
        let keyboardListenerAdded = false;
        
        function addKeyboardListener() {
            if (keyboardListenerAdded) return;
            keyboardListenerAdded = true;
            
            document.addEventListener('keydown', function(e) {
                // Don't trigger shortcuts when typing in input fields
                if (e.target.tagName === 'INPUT' || 
                    e.target.tagName === 'TEXTAREA' || 
                    e.target.contentEditable === 'true') {
                    return;
                }
                
                // Find all buttons on the page
                const buttons = Array.from(document.querySelectorAll('button'));
                
                // Flashcard mode shortcuts
                if (e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    // Find and click "Show Definition" button
                    const showBtn = buttons.find(btn => 
                        btn.textContent.includes('Show Definition'));
                    if (showBtn) {
                        showBtn.click();
                        return;
                    }
                }
                
                // Yes/No shortcuts for flashcards
                if (e.key.toLowerCase() === 'y' || e.key === '1') {
                    const yesBtn = buttons.find(btn => 
                        btn.textContent.includes('✅ Yes'));
                    if (yesBtn) {
                        e.preventDefault();
                        yesBtn.click();
                        return;
                    }
                }
                
                if (e.key.toLowerCase() === 'n' || e.key === '2') {
                    const noBtn = buttons.find(btn => 
                        btn.textContent.includes('❌ No'));
                    if (noBtn) {
                        e.preventDefault();
                        noBtn.click();
                        return;
                    }
                }
                
                // Multiple choice shortcuts (A-D or 1-4)
                if (e.key >= '1' && e.key <= '4') {
                    const optionIndex = parseInt(e.key) - 1;
                    const optionBtns = buttons.filter(btn => 
                        btn.textContent.match(/^[A-D]\./));
                    if (optionBtns[optionIndex]) {
                        e.preventDefault();
                        optionBtns[optionIndex].click();
                        return;
                    }
                }
                
                if (e.key.toLowerCase() >= 'a' && e.key.toLowerCase() <= 'd') {
                    const optionIndex = e.key.toLowerCase().charCodeAt(0) - 'a'.charCodeAt(0);
                    const optionBtns = buttons.filter(btn => 
                        btn.textContent.match(/^[A-D]\./));
                    if (optionBtns[optionIndex]) {
                        e.preventDefault();
                        optionBtns[optionIndex].click();
                        return;
                    }
                }
                
                // Navigation shortcuts
                if (e.key === 'Escape') {
                    // Find and click home or back button
                    const homeBtn = buttons.find(btn => 
                        btn.textContent.includes('Home') || 
                        btn.textContent.includes('Back'));
                    if (homeBtn) {
                        e.preventDefault();
                        homeBtn.click();
                    }
                }
            });
        }
        
        // Try to add listener immediately
        addKeyboardListener();
        
        // Also add listener after a delay to ensure DOM is ready
        setTimeout(addKeyboardListener, 500);
        
        // Re-add listener when Streamlit re-renders
        const observer = new MutationObserver(function(mutations) {
            addKeyboardListener();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    })();
    </script>
    """
    
    components.html(keyboard_js, height=0)


def display_keyboard_help():
    """Display keyboard shortcuts help"""
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        ### General Navigation
        - `Esc` - Go back/home
        
        ### Flashcard Mode
        - `Space` or `Enter` - Show definition
        - `Y` or `1` - Mark as known
        - `N` or `2` - Mark as unknown
        
        ### Quiz/Context Mode
        - `A-D` or `1-4` - Select answer option
        
        ### Tips
        - Shortcuts work when not typing in text fields
        - Use number keys for faster response
        """)


def add_keyboard_handler(mode: str = None):
    """
    Add keyboard handler with mode-specific hints
    
    Args:
        mode: Current study mode ('flashcard', 'quiz', 'context')
    """
    inject_keyboard_shortcuts()
    
    # Display mode-specific hints
    if mode == 'flashcard':
        return {
            'show': 'Space',
            'yes': 'Y',
            'no': 'N'
        }
    elif mode in ['quiz', 'context']:
        return {
            'options': ['A', 'B', 'C', 'D'],
            'numbers': ['1', '2', '3', '4']
        }
    
    return None