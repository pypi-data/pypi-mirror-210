# jatool

A Python package to download and downstream-analysis the Japanese literatures.

## Install 

``` python
pip install jatool
```

## load jatool package

``` python
from jatool.function import *
```

## Download literatures 

You need to input the author and output path. Using ja_download_fiction_author() function.
Example:
``` python
ja_download_fiction_author(author = '島崎藤村',output_path='fiction_download')
```
## Topic model (LDA)

You need to input the path which contains the txt files. Using topic_model_fition_corpus() and topic_model_fition_text().
Example:
``` python
excleded_words = []  #You can choose excleded_words to adjust the Topic model results.i.e. excleded_words = ['人','事','ぬ','やう']
topic_result = topic_model_fition_corpus(folder_path = 'fiction2',topics_num=2,added_stopwords = excleded_words)
#You can adjust the Topic model results using different 'topics_num' parameter.
topic_model_fition_text(input_corpus = topic_result,topics_num=3)
```

## Clustering analysis

You need to input the path which contains the txt files. Using get_features_path() and feature_clustering().
Example:
``` python
features = get_features_path(folder_path = 'fiction_download')
df = feature_clustering(feature_list_result = features,clusters_n =3)

#if plot can't show correctly the japanese words, please install the japanese font, for example 'Yu Gothic'
#Here is the code for font changing

# fpath = '/Your/Fonts/directory/YuGothic.ttf'
# prop = fm.FontProperties(fname=fpath)
# font_dir = ['/Your/Fonts/directory/']
# for font in fm.findSystemFonts(font_dir):
#     fm.fontManager.addfont(font)
# plt.rcParams['font.family'] = 'Yu Gothic'
```

## Emotion analysis

You need to input the specific text. Using get_sentiment_analyzer().
Example:
``` python
sentiment_analyzer = get_sentiment_analyzer()
sentiment_analyzer("私は幸福である。")
```

## Translation 
You need to input the specific text. Using translation_from_jp_to_en(), translation_from_jp_to_cn(), translation_from_lan_to_jp.
Example:
``` python
translation_from_jp_to_en("私は幸福である。")
translation_from_jp_to_cn("私は幸福である。")
translation_from_lan_to_jp('I am happy.')
```
