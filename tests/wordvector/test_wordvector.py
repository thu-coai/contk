import copy

import pytest
import numpy as np
from cotk.dataloader import LanguageGeneration, MSCOCO
from cotk.metric import MetricBase
from cotk.wordvector import WordVector, Glove
import logging

def setup_module():
	import random
	random.seed(0)
	import numpy as np
	np.random.seed(0)

class TestWordVector():
	def base_test_init(self, dl):
		assert isinstance(dl, WordVector)
		assert isinstance(dl.file_id, str)
		assert isinstance(dl.file_path, str)
		WordVector.get_all_subclasses()
		assert WordVector.load_class('Glove') == Glove
		assert WordVector.load_class('not_subclass') == None
		# initialize with none
		wv = Glove(None)
		assert wv.file_id == wv.file_path == None

	def base_test_load(self, dl):
		# test WordVector.load_matrix
		vocab_list = ['the', 'of']
		n_dims = 300
		wordvec = dl.load_matrix(n_dims, vocab_list)
		assert isinstance(wordvec, np.ndarray)
		assert wordvec.shape == (len(vocab_list), n_dims)
		print(wordvec[1])
		assert wordvec[1][0] == -0.076947


		vocab_list = ['the', 'word_not_exist']
		n_dims = 300
		wordvec = dl.load_matrix(n_dims, vocab_list)
		assert isinstance(wordvec, np.ndarray)
		assert wordvec.shape == (len(vocab_list), n_dims)
		assert wordvec[0][0] == 0.04656

		# test WordVector.load_matrix default_embeddings argument
		default_emb_array = np.random.randn(2, 300)
		default_emb_list = list(default_emb_array)
		default_emb_others = tuple(default_emb_list)
		default_emb_array_wrong_dim = np.random.randn(2, 200)
		wordvec = dl.load_matrix(n_dims, vocab_list, default_embeddings=default_emb_array)
		assert wordvec.shape == (len(vocab_list), n_dims)
		assert wordvec[1][0] == default_emb_array[1][0]
		wordvec = dl.load_matrix(n_dims, vocab_list, default_embeddings=default_emb_list)
		assert wordvec.shape == (len(vocab_list), n_dims)
		assert wordvec[1][0] == default_emb_array[1][0]
		with pytest.raises(Exception):
			dl.load_matrix(n_dims, vocab_list, default_embeddings=default_emb_array_wrong_dim)
		with pytest.raises(Exception):
			dl.load_matrix(n_dims, vocab_list, default_embeddings=default_emb_others)

		# test WordVector.load_matrix with different dim
		wordvec = dl.load_matrix(200, vocab_list)
		assert wordvec.shape == (len(vocab_list), 200)
		wordvec = dl.load_matrix(400, vocab_list)
		assert wordvec.shape == (len(vocab_list), 400)

		# test mean and std
		wordvec = dl.load_matrix(n_dims, vocab_list, mean=10, std=0.1)
		assert wordvec.mean(axis=1)[1] > 1
		wordvec = dl.load_matrix(n_dims, vocab_list, mean=np.random.randn(n_dims), std=np.random.randn(n_dims))
		with pytest.raises(ValueError):
			wordvec = dl.load_matrix(n_dims, vocab_list, mean=np.random.randn(500), std=np.random.randn(n_dims))
		with pytest.raises(ValueError):
			wordvec = dl.load_matrix(n_dims, vocab_list, mean=np.random.randn(n_dims), std=np.random.randn(500))
		with pytest.raises(ValueError):
			wordvec = dl.load_matrix(n_dims, vocab_list, mean=np.random.randn(10, 10), std=np.random.randn(n_dims))

		# test WordVector.load_dict
		oov_list = ['oov', 'unk', '']
		for vocab_list in (['the', 'and'], ['the', 'of'], ['the', 'oov'], ['oov'], ['of', 'unk', ''], []):
			wordvec = dl.load_dict(vocab_list)
			assert isinstance(wordvec, dict)
			assert set(wordvec) == set([word for word in vocab_list if word not in oov_list])
			if not wordvec:
				continue
			vec_shape = next(iter(wordvec.values())).shape
			assert len(vec_shape) == 1
			for vec in wordvec.values():
				assert isinstance(vec, np.ndarray)
				assert vec.shape == vec_shape
			if 'the' in wordvec:
				assert (wordvec['the'][-2:] == [-0.20989, 0.053913]).all()
			if 'and' in wordvec:
				assert (wordvec['and'][-2:] == [0.011807, 0.059703]).all()
			if 'of' in wordvec:
				assert (wordvec['of'][-2:] == [-0.29183, -0.046533]).all()

	def base_test_load_none(self, dl):
		vocab_list = ['the', 'word_not_exist']
		n_dims = 300

		wordvec = dl.load_matrix(n_dims, vocab_list, mean=10, std=0.1)
		assert wordvec.shape == (len(vocab_list), n_dims)
		assert wordvec.mean(axis=1)[1] > 1
		wordvec = dl.load_matrix(n_dims, vocab_list, mean=np.random.randn(n_dims), std=np.random.randn(n_dims))
		assert wordvec.shape == (len(vocab_list), n_dims)

		wordvec = dl.load_matrix(n_dims, vocab_list)
		assert wordvec.shape == (len(vocab_list), n_dims)

@pytest.fixture
def load_glove():
	def _load_glove():
		return Glove("./tests/wordvector/dummy_glove/300d")
	return _load_glove

@pytest.fixture
def load_glove_none():
	def _load_glove():
		return Glove(None)
	return _load_glove

class TestGlove(TestWordVector):
	def test_init(self, load_glove):
		super().base_test_init(load_glove())

	def test_load(self, load_glove):
		super().base_test_load(load_glove())

	def test_load_none(self, load_glove_none):
		super().base_test_load_none(load_glove_none())
