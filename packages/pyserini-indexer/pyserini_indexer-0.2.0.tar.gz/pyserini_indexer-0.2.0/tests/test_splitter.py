import itertools
import unittest

from utils import interlace_strings, redundant_splitter

test_document = """
The immune system is a network of biological processes that protects an organism from diseases. It detects and responds to a wide variety of pathogens, from viruses to parasitic worms, as well as cancer cells and objects such as wood splinters, distinguishing them from the organism's own healthy tissue. Many species have two major subsystems of the immune system. The innate immune system provides a preconfigured response to broad groups of situations and stimuli. The adaptive immune system provides a tailored response to each stimulus by learning to recognize molecules it has previously encountered. Both use molecules and cells to perform their functions.



Nearly all organisms have some kind of immune system. Bacteria have a rudimentary immune system in the form of enzymes that protect against viral infections. Other basic immune mechanisms evolved in ancient plants and animals and remain in their modern descendants. These mechanisms include phagocytosis, antimicrobial peptides called defensins, and the complement system. Jawed vertebrates, including humans, have even more sophisticated defense mechanisms, including the ability to adapt to recognize pathogens more efficiently. Adaptive (or acquired) immunity creates an immunological memory leading to an enhanced response to subsequent encounters with that same pathogen. This process of acquired immunity is the basis of vaccination. 
"""


class TestSplitter(unittest.TestCase):
    def test_ensure_max_chars(self):
        """
        Should ensure that each Passage has at most N chars
        """
        sentence_with_many_chars = "This is %s long sentence" % ("very" * 1000)
        max_characters = 100

        splitted = redundant_splitter(
            sentence_with_many_chars * 10, max_characters=max_characters
        )

        self.assertTrue(all(map(lambda x: len(x) <= max_characters, splitted)))

    def test_ensure_max_sentences(self):
        """
        Should ensure that each sentence has at most N chars
        """
        sentence_with_not_many_chars = "This is short sentence."
        sentence_length = len(sentence_with_not_many_chars)
        number_of_sentences = 100
        text = ". ".join(
            itertools.repeat(sentence_with_not_many_chars, number_of_sentences)
        )

        splitted = redundant_splitter(text, max_sentences=sentence_length)

        self.assertTrue(
            all(
                map(lambda x: len(x) <= sentence_length * number_of_sentences, splitted)
            )
        )

    def test_happy_path(self):
        max_chars = 100
        max_sentences = 3

        splitted = redundant_splitter(
            test_document, max_sentences=max_sentences, max_characters=max_chars
        )

        self.assertTrue(
            all(map(lambda x: len(x) <= max_chars * max_sentences, splitted))
        )

    def test_iterlace(self):
        expected = "This is a title\n\nFirst sentence. Next sentence"
        sents = ["This is a title", "First sentence", "Next sentence"]
        joints = ["\n\n", ". "]

        interlaced = interlace_strings(sents, joints)

        self.assertEqual(interlaced, expected)
