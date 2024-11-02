import wikipedia
import pandas as pd
import os
import spacy
from spacy.tokens import Token
import sys

modules = ["wikipedia","pandas","tqdm","spacy"]
for name in modules:
    if name not in sys.modules:
        print(f"<!> WARNING ({name}) : make sure you've installed all dependencies (pip install -r requirements.txt) <!>")


class ConsolePedantix():
    
    def __init__(self, page_name = None) -> None:
        os.system("clear")
        print("Loading")
        self.page = self.retrieve_page(page_name)
        self.title = self.page.title

        self.nlp = spacy.load('fr_core_news_md')
        self.last_word = self.nlp("")
        self.found_words = set()
        self.tested_words = set()

        should_show = lambda token: token.lower_ in self.found_words or not token.is_alpha or not token.vector_norm
        Token.set_extension("show", getter=should_show)

        self.doc_title = self.nlp(self.title)
        self.doc = self.nlp(self.page.summary)

        self.to_json()
        pass
    
    def to_json(self):
        return {
            "title": [self.to_token_json(token, i) for i, token in enumerate(self.doc_title)],
            "content": [self.to_token_json(token, i + len(self.doc_title)) for i, token in enumerate(self.doc)],
        }
    
    def to_token_json(self, token, id):
        return {
            "id": id,
            "length": len(token.text),
            "display": token.text if token._.show else None,
            "found": True if token._.show else False,
            "whitespace": token.whitespace_
        }

    def guess_word(self, game_id : str, word : str):
        # check similarity with all tokens from title+content
        self.last_word = self.nlp(word.lower())
        similarity_scores = {}
        if (self.last_word.vector_norm):
            self.tested_words.add(self.last_word)
            for i, token in enumerate([*self.doc_title, *self.doc]):
                sim = self.nlp(word.lower()).similarity(self.nlp(token.lower_)) if token.vector_norm else 0
                if sim == 1:
                    similarity_scores[str(i)] = token.text
                    self.found_words.add(token.lower_)
                elif sim > 0.6:
                    similarity_scores[str(i)] = sim
        
        if self.check_end():
            for i, token in enumerate([*self.doc_title, *self.doc]):
                similarity_scores[str(i)] = token.text
        # map to an object with keys as token index and values as similarity score
        return {
            "word": word,
            "matches": similarity_scores
        }

    def show_image(self):
        from PIL import Image
        import urllib.request

        image_found = False
        for link in self.page.images:
            if str(link).endswith("jpg"):
                image_link = link
                image_found = True
                break
        if image_found:
            urllib.request.urlretrieve(image_link,f"data/{self.page.title}.jpg")
            img = Image.open(f"data/{self.page.title}.jpg")
            img.show()
            os.remove(f"data/{self.page.title}.jpg")

    def retrieve_page(self, page_name = None):
        wikipedia.set_lang("fr")
        if not page_name:
            most_popular_pages = pd.read_csv('./data/pages_les_plus_consultees.csv').iloc[:,2]
            page_name = most_popular_pages.sample(1)
        try:
            page = wikipedia.page(page_name)
            page_found = True
        except wikipedia.exceptions.PageError:
            pass
        return page

    def check_end(self, q_pressed = False):
        return (all(token._.show for token in self.doc_title)) or q_pressed
    
    def show(self):
        os.system("clear")
        print("<!> Commmands <!>")
        print("type a word to guess, hit \\q to give up.\n")
        print("Last word : ", self.last_word, "\n")
        print("\033[1m" + ''.join([self.print_token(token) for token in self.doc_title]) + "\033[0m")
        print(''.join([self.print_token(token) for token in self.doc]))
    
    def print_token(self, token):
        if token._.show:
            color = "\033[92m" if token.lower_ in self.found_words else "\033[0m"
            return self.with_color(token, color)

        else:
            similarity_scores = [(word.similarity(token), word) for word in self.tested_words]
            if not similarity_scores:
                similarity_scores.append((0, None))
            max_sim, max_sim_word = max(similarity_scores, key=lambda x: x[0])
            if max_sim > 0.6:
                return self.with_color(max_sim_word, "\033[91m",  token.whitespace_)

            return '-' * len(token.text) + token.whitespace_

    def with_color(self, token, color, extra_withspace = ''):
        reset_color = "\033[0m"
        return ''.join([color, token.text_with_ws, extra_withspace, reset_color]) 

    def play(self):
        q_pressed : bool = False
        while not self.check_end(q_pressed):
            self.show()
            char_put = str(input())
            q_pressed = (char_put == '\q')
            if not q_pressed:
                self.test_word(char_put)
        if q_pressed:
            print(f"The answer was {self.title} :/")
        else:
            print(f"Congrats 🎉 The answer was {self.title} !")
        print(self.page.url)
        self.show_image()

    def test_word(self, word : str):
        self.last_word = self.nlp(word.lower())
        if (self.last_word.vector_norm):
            self.tested_words.add(self.last_word)
            for token in [*self.doc, *self.doc_title]:
                sim = self.last_word.similarity(self.nlp(token.lower_)) if token.vector_norm else 0
                if sim > 0.8:
                    self.found_words.add(token.lower_)




