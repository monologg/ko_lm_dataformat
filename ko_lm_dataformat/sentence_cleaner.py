import unicodedata


def _is_control(char):
    """Checks whether `char` is a control character."""
    # (Code from Huggingface Transformers)
    # These are technically control characters but we count them as whitespace
    # characters.
    if char == "\t" or char == "\n" or char == "\r":
        return False
    cat = unicodedata.category(char)
    if cat.startswith("C"):
        return True
    return False


def clean_sentence(sentence, remove_control=True):
    """
    - NFC Normalization
    - Invalid character removal (Some control character)
    - Whitespace cleanup
      - strip()
      - double whitespace, \n, \r, \t -> simple whitespace (" ")
      - Unify all Zs to simple whitespace (" ")
    """
    sentence = unicodedata.normalize("NFC", sentence)

    if remove_control:
        output = []
        for char in sentence:
            if _is_control(char) or ord(char) == 0xFFFD:
                continue
            output.append(char)

        sentence = "".join(output)

    return " ".join(sentence.strip().split())
