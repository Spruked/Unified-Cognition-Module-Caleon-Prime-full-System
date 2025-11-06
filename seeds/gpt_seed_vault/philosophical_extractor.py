#!/usr/bin/env python3
"""
Philosophical Content Extractor for GPT Chat Archive
Extracts conversations containing philosophical themes for memory vault creation.
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from bs4 import BeautifulSoup

class PhilosophicalExtractor:
    def __init__(self):
        # More sophisticated philosophical keywords and phrases
        self.philosophical_themes = {
            'consciousness': {
                'keywords': ['consciousness', 'awareness', 'self-awareness', 'qualia', 'phenomenology', 'mind-body', 'dualism', 'monism'],
                'phrases': ['what is consciousness', 'nature of mind', 'self-awareness', 'experience of consciousness']
            },
            'ethics': {
                'keywords': ['ethics', 'moral philosophy', 'deontology', 'utilitarianism', 'virtue ethics', 'categorical imperative', 'moral relativism'],
                'phrases': ['is it ethical', 'moral dilemma', 'right and wrong', 'ethical theory', 'moral philosophy']
            },
            'philosophy': {
                'keywords': ['philosophy', 'philosophical', 'existentialism', 'phenomenology', 'hermeneutics', 'metaphysics', 'epistemology'],
                'phrases': ['philosophical question', 'deep philosophical', 'philosophy of']
            },
            'reasoning': {
                'keywords': ['reasoning', 'logic', 'rational', 'deductive', 'inductive', 'abductive', 'fallacy', 'argument'],
                'phrases': ['logical reasoning', 'rational thought', 'sound argument', 'logical fallacy']
            },
            'reality': {
                'keywords': ['reality', 'ontology', 'metaphysics', 'existence', 'being', 'truth', 'epistemology', 'knowledge'],
                'phrases': ['nature of reality', 'what is real', 'ultimate reality', 'reality is']
            },
            'existence': {
                'keywords': ['existence', 'existential', 'being', 'purpose', 'meaning of life', 'nihilism', 'absurdism'],
                'phrases': ['meaning of existence', 'why do we exist', 'purpose of life', 'existential crisis']
            },
            'society': {
                'keywords': ['society', 'civilization', 'social contract', 'justice', 'equality', 'freedom', 'rights'],
                'phrases': ['social philosophy', 'political philosophy', 'justice in society', 'ideal society']
            },
            'science_philosophy': {
                'keywords': ['quantum', 'relativity', 'uncertainty principle', 'observer effect', 'many worlds', 'determinism'],
                'phrases': ['philosophy of science', 'quantum philosophy', 'scientific realism', 'theory of relativity']
            }
        }

        self.extracted_content = defaultdict(list)

    def extract_from_html(self, html_file):
        """Extract conversations from HTML export"""
        print("Parsing HTML file...")
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        conversations = []
        conversation_divs = soup.find_all('div', class_=re.compile(r'conversation|chat'))

        if not conversation_divs:
            # Try alternative selectors
            conversation_divs = soup.find_all('div', attrs={'data-conversation-id': True})

        if not conversation_divs:
            # Fallback: look for any div with substantial text content
            all_divs = soup.find_all('div')
            conversation_divs = [div for div in all_divs if len(div.get_text(strip=True)) > 500]

        print(f"Found {len(conversation_divs)} potential conversations")

        for i, conv_div in enumerate(conversation_divs):
            if i % 50 == 0:
                print(f"Processing conversation {i}...")

            conversation_text = conv_div.get_text(separator='\n', strip=True)

            # Extract title if available
            title_elem = conv_div.find(['h3', 'h4', 'title'])
            title = title_elem.get_text(strip=True) if title_elem else f"Conversation {i+1}"

            # Analyze for philosophical content
            self.analyze_conversation(title, conversation_text, i)

        print(f"Completed analysis of {len(conversation_divs)} conversations")

    def analyze_conversation(self, title, text, conv_id):
        """Analyze a conversation for philosophical content"""
        text_lower = text.lower()

        for theme, criteria in self.philosophical_themes.items():
            relevance_score = 0

            # Check for keywords
            keyword_matches = sum(1 for keyword in criteria['keywords'] if keyword in text_lower)
            relevance_score += keyword_matches * 2

            # Check for phrases
            phrase_matches = sum(1 for phrase in criteria['phrases'] if phrase in text_lower)
            relevance_score += phrase_matches * 3

            # Bonus for multiple philosophical indicators
            if keyword_matches >= 2 or phrase_matches >= 1:
                relevance_score += 5

            # Only extract if sufficiently philosophical
            if relevance_score >= 3:
                # Extract relevant segments
                segments = self.extract_philosophical_segments(text, criteria)

                if segments:
                    self.extracted_content[theme].append({
                        'title': title,
                        'conversation_id': f'conv_{conv_id}',
                        'timestamp': datetime.now().timestamp(),
                        'segments': segments,
                        'themes': [theme],
                        'relevance_score': relevance_score
                    })

    def extract_philosophical_segments(self, text, criteria, max_segments=3):
        """Extract the most philosophical segments from a conversation"""
        sentences = re.split(r'[.!?]+', text)
        philosophical_sentences = []

        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if len(sentence_lower) < 20:  # Skip very short sentences
                continue

            # Check if sentence contains philosophical content
            keyword_count = sum(1 for keyword in criteria['keywords'] if keyword in sentence_lower)
            phrase_count = sum(1 for phrase in criteria['phrases'] if phrase in sentence_lower)

            if keyword_count > 0 or phrase_count > 0:
                philosophical_sentences.append({
                    'text': sentence.strip(),
                    'keywords_found': keyword_count,
                    'phrases_found': phrase_count
                })

        # Sort by philosophical density and return top segments
        philosophical_sentences.sort(key=lambda x: x['keywords_found'] + x['phrases_found'] * 2, reverse=True)
        return philosophical_sentences[:max_segments]

    def save_vaults(self, output_dir='seeds/gpt_seed_vault/philosophical_vaults'):
        """Save extracted content to JSON vault files"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        for theme, conversations in self.extracted_content.items():
            # Sort conversations by relevance score
            conversations.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

            vault_data = {
                'theme': theme,
                'extraction_date': datetime.now().isoformat(),
                'total_conversations': len(conversations),
                'conversations': conversations
            }

            filename = f'{theme}_vault.json'
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(vault_data, f, indent=2, ensure_ascii=False)

            print(f"Saved {len(conversations)} conversations to {filename}")

def main():
    extractor = PhilosophicalExtractor()

    # Process the chat.html file
    chat_file = 'chat.html'

    print("Processing GPT chat archive for philosophical content...")

    try:
        extractor.extract_from_html(chat_file)
    except Exception as e:
        print(f"Error processing HTML file: {e}")
        return

    # Save extracted vaults
    extractor.save_vaults()

    print("Philosophical content extraction complete!")

if __name__ == '__main__':
    main()