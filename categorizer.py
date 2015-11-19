#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import codecs
import hunspell
from operator import itemgetter
from itertools import izip, islice
import re
import numpy as np
import pickle
from pygermanet import load_germanet


class Categorizer:


    
    def __init__(self):
	
	self.cat_dict = json.load(open('categories.json'))
	self.words, self.embeddings = pickle.load(open('polyglot-de.pkl', 'rb'))
	# Special tokens
   	self.Token_ID = {"<UNK>": 0, "<S>": 1, "</S>":2, "<PAD>": 3}
    	self.ID_Token = {v:k for k,v in self.Token_ID.iteritems()}
    	# Noramlize digits by replacing them with #
    	self.DIGITS = re.compile("[0-9]", re.UNICODE)
    	# Number of neighbors to return.
    	self.k = 5
   	# Map words to indices and vice versa
    	self.word_id = {w:i for (i, w) in enumerate(self.words)}
    	self.id_word = dict(enumerate(self.words))
	self.hobj = hunspell.HunSpell('/usr/share/hunspell/de_DE.dic', '/usr/share/hunspell/de_DE.aff')

    def _collect_category(self,word):
	word=self._check_spelling(word)
	categories_gn = self._add_germanet_categories(unicode(word))	
	c_id_word,c_emb= self._cat_embeddings()
	words =self._knn(word,c_emb,c_id_word)	
	categories_d = self._map_to_category(words)
	categories = list(set(categories_gn+categories_d))
	return categories



    def _knn(self,word,c_embeddings,c_id_word):
	print c_embeddings
        word = self._normalize(word, self.word_id)
        if not word:
            return []
        word_index = self.word_id[word]
        indices, distances = self._l2_nearest(word_index,c_embeddings)
        neighbors = [c_id_word[idx] for idx in indices]
	words=[]
        for i, (word, distance) in enumerate(izip(neighbors, distances)):
            words.append(word)
            print i, '\t', word, '\t\t', distance
	return words

    def _add_germanet_categories(self,word):
	gn = load_germanet()
	cats=[]	
	hp = gn.synset(word+'.n.1').hypernym_paths
	print hp
	for h in hp: 
	    print h[-4:-1]
	    for s in h[-4:-1]:		
		cats.append(str(s).split('(')[1].split('.')[0])
	cats = list(set(cats))
	return cats

    def _map_to_category(self,words):
        print words
	categories =[]
	#word was OOV
	if words ==[]:
		categories.append(self._longest_list(self.cat_dict))
	#words found	
	else:
            for word in words:
		print word
                for key in self.cat_dict:
		    if word==key:
			categories.append(word)
	            elif word in self.cat_dict[key]:
			print word
			print key
			categories.append(key)

        return categories

    def _longest_list(self,dicti):
        leng=0
	cat=''
	for key in dicti:
		if len(dicti[key]) > leng:
			cat=key

	return cat


    def _check_spelling(self,word):
	
	if not self.hobj.spell(word):
		word = self.hobj.suggest(word)[0]
	print word
	return word	

    def _cat_embeddings(self):
	c_emb= []
	c_id_word={}
	index=0
	for key in self.cat_dict:
		if key in self.word_id:
			c_id_word[index]=key
			index+=1
			c_emb.append(self.embeddings[self.word_id[key]])
		for v in self.cat_dict[key]:
			if v in self.word_id:
				c_id_word[index]=v
				index+=1	
				c_emb.append(self.embeddings[self.word_id[v]])

	return c_id_word,np.array(c_emb,dtype=np.float32)

    def _case_normalizer(self,word, dictionary):
        """ In case the word is not available in the vocabulary,
        we can try multiple case normalizing procedure.
        We consider the best substitute to be the one with the lowest index,
        which is equivalent to the most frequent alternative."""
        w = word
        lower = (dictionary.get(w.lower(), 1e12), w.lower())
        upper = (dictionary.get(w.upper(), 1e12), w.upper())
        title = (dictionary.get(w.title(), 1e12), w.title())
        results = [lower, upper, title]
        results.sort()
        index, w = results[0]
        if index != 1e12:
            return w
        return word

    def _normalize(self,word, word_id):
    	""" Find the closest alternative in case the word is OOV."""
	if not word in word_id:
	    word = self.DIGITS.sub("#", word)
	if not word in word_id:
	    word = self._case_normalizer(word, word_id)

	if not word in word_id:
	    return None
	return word

	
    def _l2_nearest(self,word_index,c_emb):
        """Sorts words according to their Euclidean distance.
           To use cosine distance, embeddings has to be normalized so that their l2 norm is 1."""

	e = self.embeddings[word_index]
	distances = (((c_emb - e) ** 2).sum(axis=1) ** 0.5)

	sorted_distances = sorted(enumerate(distances), key=itemgetter(1))
	print sorted_distances
	return zip(*sorted_distances[:self.k])

    def categorize_word(self,word):
	inf=open('word_data_base.json','r')
        cat_dict = json.load(inf)
	inf.close()
        cats = self._collect_category(word)
        for cat in cats:
            if cat in cat_dict:
                if word not in cat_dict[cat]:
                    cat_dict[cat].append(word)
            elif cat not in cat_dict:
                cat_dict[cat] =[word]
        with open('word_data_base.json', 'w') as fp:
            json.dump(cat_dict, fp)

    def return_all_elements_of_category(self,cat):
	cat_dict=json.load(open('word_data_base.json'))
	return cat_dict[cat]

    def delete_word(self,word):
	inf=open('word_data_base.json','r')
        cat_dict = json.load(inf)
        inf.close()
	for cat in cat_dict:
		if word in cat_dict[cat]:
			cat_dict[cat].pop(cat_dict[cat].index(word))
        with open('word_data_base.json', 'w') as fp:
            json.dump(cat_dict, fp) 
