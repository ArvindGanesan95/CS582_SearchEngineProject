"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import re
import string
from typing import TypeVar, Generic

from nltk.stem import PorterStemmer

# Reference URL : https://www.nltk.org/install.html

T = TypeVar('T')


# An implementation of pipeline design pattern to support preprocessing operations
# Adapted from https://github.com/iluwatar/java-design-patterns
# MIT-License : https://github.com/iluwatar/java-design-patterns/blob/master/LICENSE.md
class PreprocessorPipeline(Generic[T]):
    stop_words_file_path = r'E:\IR\Project - Copy\Preprocessor\stopwords.txt'
    ps = PorterStemmer()
    stop_words_list = list()

    """an abstract method to be defined by the child classes"""

    def execute(self, data: T):
        pass

    # Function to read the stopwords file in the file system
    @staticmethod
    def get_stop_words():
        if len(PreprocessorPipeline.stop_words_list) > 0:
            return PreprocessorPipeline.stop_words_list
        with open(PreprocessorPipeline.stop_words_file_path) as handle:
            file_content = handle.read()
            PreprocessorPipeline.stop_words_list = file_content.split("\n")
            return PreprocessorPipeline.stop_words_list


# Refined classes that forms a part in the pipeline
class CaseConverter(PreprocessorPipeline):
    def execute(self, data: list):
        return data.__getitem__(0).lower()


# Refined classes that forms a part in the pipeline
class Tokenizer(PreprocessorPipeline):
    def execute(self, data: str):
        split_text = data.split()
        return split_text


# Refined classes that forms a part in the pipeline
class StopWordRemoval(PreprocessorPipeline):
    def execute(self, words: list):
        stop_words: list = self.get_stop_words()
        result = list()
        for word in words:
            if not stop_words.__contains__(word):
                result.append(word)
        return result


# Refined classes that forms a part in the pipeline
class RemovePunctuationHandler(PreprocessorPipeline):
    def execute(self, list_of_words: list):
        table = str.maketrans(dict.fromkeys(string.punctuation))
        result = list()
        for word in list_of_words:
            modified_word = word.translate(table)
            if len(modified_word) > 0:
                result.append(word.translate(table))
        return result


# Refined classes that forms a part in the pipeline
class RemoveNumbersHandler(PreprocessorPipeline):
    def execute(self, list_of_words: list):
        table = str.maketrans(dict.fromkeys(string.punctuation))
        result = list()
        for word in list_of_words:
            result.append(re.sub('[0-9]+', '', word))
        return result


# Refined classes that forms a part in the pipeline
class PorterStemmerHandler(PreprocessorPipeline):

    def execute(self, words_list: list):
        result = list()
        for word in words_list:
            result.append(self.ps.stem(word))
        return result


# Refined classes that forms a part in the pipeline
class RemoveWordsHandler(PreprocessorPipeline):
    words_length_to_remove = 2

    def execute(self, words_list: list):
        result = list()
        for word in words_list:
            if len(word) > self.words_length_to_remove:
                result.append(word)
        return result


# The pipeline instantiate class
class Pipeline:
    pipelineSteps: list[PreprocessorPipeline] = list()
    firstStepInput: list = NotImplemented
    was_pipeline_executed_already: bool = False

    def __init__(self):
        self.firstStepInput = list()
        self.pipelineSteps = list()
        self.was_pipeline_executed_already = False

    def add_step(self, step: PreprocessorPipeline):
        if self.was_pipeline_executed_already:
            self.pipelineSteps.clear()
            self.was_pipeline_executed_already = False
        self.pipelineSteps.append(step)

    def execute(self):
        self.was_pipeline_executed_already = True
        for step in self.pipelineSteps:
            result = step.execute(self.firstStepInput)
            self.firstStepInput = result

    def get_result(self):
        return self.firstStepInput.copy()

    def set_initial_data(self, data: str):
        if self.was_pipeline_executed_already:
            self.firstStepInput.clear()
        self.firstStepInput.append(data)
