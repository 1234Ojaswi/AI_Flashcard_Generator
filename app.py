import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('models/gemini-2.5-flash')
def generate_flashcards(text, num_cards=10):
    """Generate flashcards from input text using Gemini AI"""
    
    prompt = f"""
    You are an expert educator. Analyze the following text and create {num_cards} flashcards.
    
    TEXT:
    {text}
    
    INSTRUCTIONS:
    - Create clear, concise questions that test understanding
    - Provide accurate, complete answers
    - Cover key concepts from the text
    - Make questions varied (definitions, concepts, applications)
    
    OUTPUT FORMAT (JSON only, no markdown):
    [
        {{"question": "What is...?", "answer": "..."}},
        {{"question": "Explain...", "answer": "..."}}
    ]
    
    Generate exactly {num_cards} flashcards in valid JSON format.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        flashcards = json.loads(response_text)
        return flashcards
    
    except json.JSONDecodeError as e:
        st.error(f"Error parsing AI response: {e}")
        return None
    except Exception as e:
        st.error(f"Error generating flashcards: {e}")
        return None

def save_flashcards(flashcards, filename):
    """Save flashcards to CSV and JSON"""
    if not os.path.exists('flashcards'):
        os.makedirs('flashcards')
    
    # Save as CSV
    df = pd.DataFrame(flashcards)
    csv_path = f'flashcards/{filename}.csv'
    df.to_csv(csv_path, index=False)
    
    # Save as JSON
    json_path = f'flashcards/{filename}.json'
    with open(json_path, 'w') as f:
        json.dump(flashcards, f, indent=2)
    
    return csv_path, json_path

# Streamlit UI
def main():
    st.set_page_config(page_title="AI Flashcard Generator", page_icon="🎴")
    
    st.title("🎴 AI Flashcard Generator")
    st.markdown("Transform your study notes into flashcards instantly!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        num_cards = st.number_input("How many flashcards do you want?", min_value=1, max_value=200, value=10, step=1)
        st.markdown("---")
        st.info("💡 **Tip**: Paste lecture notes, textbook excerpts, or any study material!")
    
    # Main input
    st.subheader("📝 Enter Your Study Material")
    text_input = st.text_area(
        "Paste your notes here:",
        height=200,
        placeholder="Example: Machine learning is a subset of artificial intelligence..."
    )
    
    # Sample text option
    if st.checkbox("Use sample text"):
        text_input = """
        Machine Learning is a subset of Artificial Intelligence that enables computers to learn from data without being explicitly programmed. 
        There are three main types: Supervised Learning (labeled data), Unsupervised Learning (unlabeled data), and Reinforcement Learning (reward-based).
        Common algorithms include Linear Regression, Decision Trees, Neural Networks, and K-Means Clustering.
        Applications range from image recognition to recommendation systems.
        """
        st.text_area("Sample text loaded:", text_input, height=150)
    
    # Generate button
    if st.button("🚀 Generate Flashcards", type="primary"):
        if not text_input or len(text_input) < 50:
            st.warning("⚠️ Please enter at least 50 characters of study material.")
        else:
            with st.spinner("🤖 AI is creating your flashcards..."):
                flashcards = generate_flashcards(text_input, num_cards)
                
                if flashcards:
                    st.success(f"✅ Generated {len(flashcards)} flashcards!")
                    
                    # Display flashcards
                    st.subheader("📚 Your Flashcards")
                    
                    for i, card in enumerate(flashcards, 1):
                        with st.expander(f"Flashcard {i}: {card['question'][:60]}..."):
                            st.markdown(f"**Question:**")
                            st.info(card['question'])
                            st.markdown(f"**Answer:**")
                            st.success(card['answer'])
                    
                    # Save options
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"flashcards_{timestamp}"
                    
                    csv_path, json_path = save_flashcards(flashcards, filename)
                    
                    st.subheader("💾 Download Your Flashcards")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with open(csv_path, 'r') as f:
                            st.download_button(
                                label="📥 Download CSV",
                                data=f.read(),
                                file_name=f"{filename}.csv",
                                mime="text/csv"
                            )
                    
                    with col2:
                        with open(json_path, 'r') as f:
                            st.download_button(
                                label="📥 Download JSON",
                                data=f.read(),
                                file_name=f"{filename}.json",
                                mime="application/json"
                            )
                    
                    st.info(f"✅ Files saved in 'flashcards/' folder")

if __name__ == "__main__":
    main()