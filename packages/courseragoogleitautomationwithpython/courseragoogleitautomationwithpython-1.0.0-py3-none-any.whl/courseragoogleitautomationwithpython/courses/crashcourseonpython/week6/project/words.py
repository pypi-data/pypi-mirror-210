from typing import Dict, Set


class WordsUtil:
    @staticmethod
    def _process_word(word: str) -> str:
        return "".join([char for char in word if char.isalpha()])

    @staticmethod
    def words_in_text(text: str, word_exceptions: Set[str]) -> Dict[str, int]:
        word_tokens = [WordsUtil._process_word(word=token) for token in text.split()]
        word_tokens = [word for word in word_tokens if word not in word_exceptions]

        word_frequencies: Dict[str, int] = {}
        for word in word_tokens:
            word = word.lower()
            if word not in word_frequencies:
                word_frequencies[word] = 0
            word_frequencies[word] += 1
        return word_frequencies


if __name__ == "__main__":
    some_text = "text"
    exceptions = {"a", "the", "to", "if"}
    print(WordsUtil.words_in_text(text=some_text, word_exceptions=exceptions))
