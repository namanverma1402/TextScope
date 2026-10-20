import unittest
from similarity import normalize_text, score_pair, compare_documents

class SimilarityTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_text('  HELLO\n World '), 'hello world')
    def test_identical_text_scores_high(self):
        text = 'Python is useful for building web applications.'
        self.assertGreater(score_pair(text, text)['combined_score'], 99)
    def test_empty_text_safe(self):
        self.assertEqual(score_pair('', 'some text')['combined_score'], 0)
    def test_identical_reference_ranks_first(self):
        results = compare_documents('The cat sat on the mat.', [
            {'name':'unrelated','text':'Database normalization reduces redundancy.'},
            {'name':'identical','text':'The cat sat on the mat.'}])
        self.assertEqual(results[0]['name'], 'identical')

if __name__ == '__main__':
    unittest.main()
