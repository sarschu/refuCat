# refuCat
Categorizes entered items and retrieves items by category search  

Have the following stuff installed:  

## Requirements:

mongodb  
pygermanet  
german hunspell dicts /usr/share/hunspell/de_DE.dic /usr/share/hunspell/de_DE.aff  

Python:  
json  
codecs  
operator  
itertools  
numpy  
pickle  

## Some install tips

sudo apt-get install mongodb  
sudo pip install repoze.lru pygermanet  
sudo apt-get install python-hunspell  


## Usage:

1. mongodb starten!!! mongod --dbpath ./mongodb  


from categorizer import Categorizer  
c = Categorizer()  

save categories of a word to word_data_base  
c.categorize_word('word')  

find all words of a specific category  
c.return_all_elements_of_category('category')  

delete a word from the category data base  
c.delete_word('word')  
