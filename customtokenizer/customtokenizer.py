import re
from typing import Any, Dict, List, Text

from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message
from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)

class CustomTokenizer(Tokenizer):

    provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]

    defaults = {
        # Flag to check whether to split intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Text will be tokenized with case sensitive as default
        "case_sensitive": False,
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        if not self.case_sensitive:
            text = text.lower()
            
        words = re.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w@]+(?=[^0-9\s])|",
            " ",
            text,
        ).split()

        return self._convert_words_to_tokens(words, text)