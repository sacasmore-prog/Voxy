# Updated main.py

class Flashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.flipped = False

    def flip(self):
        self.flipped = not self.flipped

    def display(self):
        if self.flipped:
            return self.answer
        return self.question


class ConceptExtractor:
    def __init__(self, text):
        self.text = text

    def extract_concepts(self):
        # Dummy implementation for extracting concepts
        return self.text.split()  # Replace with actual logic


class FlashcardApp:
    def __init__(self):
        self.flashcards = []

    def add_flashcard(self, question, answer):
        card = Flashcard(question, answer)
        self.flashcards.append(card)

    def display_flashcards(self):
        for card in self.flashcards:
            print(card.display())


# Academic data extraction placeholder
# Add function to extract academic-related Q&A pairs

def extract_academic_data(text):
    concepts = ConceptExtractor(text).extract_concepts()
    q_and_a_pairs = []  # Replace with logic to generate Q&A
    return concepts, q_and_a_pairs


# HTML structure and CSS for Flashcards
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flashcards</title>
    <style>
        .card {
            background: white;
            border: 1px solid #ccc;
            border-radius: 10px;
            width: 200px;
            height: 100px;
            margin: 10px;
            display: inline-block;
            perspective: 1000px;
        }
        .card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.6s;
            transform-style: preserve-3d;
        }
        .card.flipped .card-inner {
            transform: rotateY(180deg);
        }
        .card-front, .card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
        }
        .card-back {
            transform: rotateY(180deg);
        }
    </style>
</head>
<body>
    <div id="flashcards"></div>
    <script>
        // JavaScript to handle card flipping and rendering
        const flashcards = [];  // Array to hold flashcards
        function renderFlashcards() {
            const container = document.getElementById('flashcards');
            flashcards.forEach((card) => {
                const cardElement = document.createElement('div');
                cardElement.className = 'card';
                cardElement.innerHTML = `<div class='card-inner'>
                    <div class='card-front'>${card.question}</div>
                    <div class='card-back'>${card.answer}</div>
                </div>`;
                cardElement.onclick = () => { cardElement.classList.toggle('flipped'); };
                container.appendChild(cardElement);
            });
        }
        document.addEventListener('DOMContentLoaded', renderFlashcards);
    </script>
</body>
</html>
'''

# The above HTML content would be saved in the relevant path
