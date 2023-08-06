import pandas as pd
import urllib.request
import ssl
import zipfile
import os
import glob
import datetime
import chardet
import spacy
#ja_ginza

from gensim import corpora, models
#pip install matplotlib
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler

import seaborn as sns

from matplotlib import font_manager

from matplotlib import font_manager as fm

from sklearn.cluster import AgglomerativeClustering

from transformers import AutoModel, AutoTokenizer
import xformers
import fugashi
import torch 
import transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

import urllib
import hashlib
import random
import requests
import time

import json
from hashlib import md5



##################青空文库下载链接文本处理#######################
fiction_database_file = 'fiction_info_new.txt'
fiction_df = pd.read_csv(fiction_database_file, delimiter='\t') # 读取txt
fiction_df['副題'] = fiction_df['副題'].str.replace('\u3000', ' ') # 去除全角空格 
fiction_df['author_fiction'] = fiction_df['author'] + '_' +fiction_df['作品名']  # 添加 author_fiction
fiction_df['author_fiction_subname'] = fiction_df['author'] + '_' + fiction_df['作品名'] + '_' + fiction_df['副題']# 添加 author_fiction_subname
fiction_df.columns
author_list = fiction_df['author'] # 添加作者
fiction_df['url'] = fiction_df['テキストファイルURL'] # 添加url下载链接
# 整理list
unique_author_list = list(set(author_list))
unique_author_fiction_list = list(set(fiction_df['author_fiction']))
unique_author_fiction_subname_list = list(set(fiction_df['author_fiction_subname']))

########################

############################小函数##########################
def unzip_file(filepath): ##解压zip函数
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(filepath))
    os.remove(filepath)

def rename_recent_txt(filepath,new_filename):
    # 获取文件夹中所有的txt文件，选择最近修改的文件
    recent_file = None
    recent_time = datetime.datetime.min
    for file_name in os.listdir(filepath):
        if file_name.endswith('.txt'):
            file_path = os.path.join(filepath, file_name)
            modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if modified_time > recent_time:
                recent_file = file_path
                recent_time = modified_time

    # 将文件重命名为'bbb.txt'
    if recent_file is not None:
        os.rename(recent_file, os.path.join(filepath, new_filename))

def get_author_list():
    print(unique_author_list)
    
    
def read_aozora_file(txt):
    # 读取文件并自动判断编码
    import chardet
    def read_text_file(file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            text = raw_data.decode(encoding)
        return text
    # 处理文本
    def process_text(text):
        # 删除 '-------------------------------------------------------' 前的内容
        separator = '-------------------------------------------------------'
        if separator in text:
            text = text.split(separator, 1)[1]

        # 删除 '底本：' 后的内容
        keyword = '底本：'
        if keyword in text:
            text = text.split(keyword, 1)[0]

        return text
    # 读取文本文件并处理
    file_path = txt
    text = read_text_file(file_path)
    processed_text = process_text(text)
    return(processed_text)


####################

#################################下载函数########################
def ja_download_fiction(author,fiction_name,sub_name='',all = False,output_path='fiction_download'):
    ########To do: download the specific fiction#####
    #######################################1.判断输入是否合法##################################
    ################判断作者author是否合法
    if author in unique_author_list:
        print(f'{author} is in the author list!')
    else:
        raise ValueError(f'{author} is not in the author list!')

    ################判断作品fiction_name是否合法
    author_fiction = author + '_' + fiction_name
    if author_fiction in unique_author_fiction_list:
        print(f'{author_fiction} is in the author fiction list!')
    else:
        raise ValueError(f'{author_fiction} is not in the author fiction list!')

    #########判断作品是否独立，如果不独立，显示可供选择的篇目
    if sub_name == '':
        #如果sub_name为空，则判断是否有分卷
        all_author_fiction_list = fiction_df['author_fiction']
        counts = fiction_df['author_fiction'].value_counts()
        count_author_fiction_input = counts[author_fiction]
        if count_author_fiction_input == 1:
            url =fiction_df.loc[fiction_df['author_fiction'] == author_fiction, 'url']
            url = url.to_list()[0]
            file_name = fiction_df.loc[fiction_df['author_fiction'] == author_fiction, 'fiction_new_name']
            file_name =  file_name.to_list()[0]
            file_path = output_path + '/' + os.path.basename(url)
            urllib.request.urlretrieve(url, file_path) #下载
            unzip_file(file_path)   #解压
            # 重命名
            rename_recent_txt(output_path,file_name)
            print( 'Downloading is done')
            #latest_file = max(glob.glob(os.path.join(output_path, '*')), key=os.path.getmtime)
            #os.rename(latest_file, os.path.join(output_path, file_name))

        else:
            subname_option = fiction_df.loc[fiction_df['author_fiction'] == author_fiction, '副題']
            subname_option = subname_option.to_list()
            print('Input fiction has more than one option in AOZARA database.')
            print('You can adjust "sub_name" parameter using these option:'  )
            print(subname_option)
            print(f'Choose one subname to download the fiction!')
            #raise ValueError(f'Choose one subname to download the fiction!')
    else:
        # 如果sub_name为不为空，则判断分卷是否合法，合法则下载，否则报错
        author_fiction_subname = author + '_' + fiction_name + '_' + sub_name
        if author_fiction_subname in unique_author_fiction_subname_list:
            print(f'{author_fiction_subname} is in the author fiction subname list!')

            url = fiction_df.loc[fiction_df['author_fiction_subname'] == author_fiction_subname, 'url']
            url = url.to_list()[0]
            file_name = fiction_df.loc[fiction_df['author_fiction_subname'] == author_fiction_subname, 'fiction_new_name']
            file_name = file_name.to_list()[0]
            file_path = output_path + '/' + os.path.basename(url)
            urllib.request.urlretrieve(url, file_path)  # 下载
            unzip_file(file_path)  # 解压
            # 重命名
            rename_recent_txt(output_path,file_name)
            print( 'Downloading is done')
        else:
            subname_option = fiction_df.loc[fiction_df['author_fiction'] == author_fiction, '副題']
            subname_option = subname_option.to_list()
            print('Input fiction has more than one option in AOZARA database.')
            print('You can adjust "sub_name" parameter using these option:')
            print(subname_option)
            print(f'Choose one subname to download the fiction!')
            raise ValueError(f'{author_fiction_subname} is not in the author fiction subname list!')



#################################下载函数--下载作者的所有作品########################
def ja_download_fiction_author(author,output_path='fiction_download'):
    ########To do: download the specific fiction#####
    #####################################0.创建输出目录#######################################
    # 指定要检查的路径
    path = output_path
    # 检查路径是否存在
    if not os.path.exists(path):
        # 如果路径不存在，创建它
        os.makedirs(path)
        print(f"path'{path}' created successfully！")
    else:
        print(f"path'{path}' existed！")
    
    #######################################1.判断输入是否合法##################################
    ################判断作者author是否合法
    if author in unique_author_list:
        print(f'{author} is in the author list!')
    else:
        raise ValueError(f'{author} is not in the author list!')
    
    
    ########################################2.获得改作者的所有小说##############################
            
    url_list = fiction_df.loc[fiction_df['author'] == author, 'url']
    for url in url_list:
        file_name = fiction_df.loc[fiction_df['url'] == url, 'fiction_new_name']
        file_name = file_name.to_list()[0]
        file_path = output_path + '/' + os.path.basename(url)
        urllib.request.urlretrieve(url, file_path)  # 下载
        unzip_file(file_path)  # 解压
        # 重命名
        rename_recent_txt(output_path,file_name)
        print( file_name + ' downloading is done')

        
##############################分词###########################
import spacy
nlp = spacy.load('ja_ginza')
def ja_tokenize(content):
    import spacy

    # 加载Ginza模型

    # 运行分词和词性标注
    doc = nlp(content)

    # 遍历分词和词性标注的结果
    text_list = []
    tag_list = []
    for token in doc:
        text_list.append(token.text)
        tag_list.append(token.tag_)
        #print(token.text, token.lemma_, token.pos_, token.tag_)
    
    #token_df = pd.DataFrame({'text': text_list, 'tag': tag_list})
    return([text_list,tag_list])


nlp = spacy.load('ja_ginza')

def ja_tokenize_text(content):
    

    # 加载Ginza模型
    # 运行分词和词性标注
    doc = nlp(content)

    # 遍历分词和词性标注的结果
    text_list = []
    tag_list = []
    for token in doc:
        text_list.append(token.text)
        tag_list.append(token.tag_)
        #print(token.text, token.lemma_, token.pos_, token.tag_)
    
    #token_df = pd.DataFrame({'text': text_list, 'tag': tag_list})
    return(text_list)

def ja_tokenize_tag(content):
    import spacy

    # 加载Ginza模型
    # 运行分词和词性标注
    doc = nlp(content)

    # 遍历分词和词性标注的结果
    text_list = []
    tag_list = []
    for token in doc:
        text_list.append(token.text)
        tag_list.append(token.tag_)
        #print(token.text, token.lemma_, token.pos_, token.tag_)
    
    #token_df = pd.DataFrame({'text': text_list, 'tag': tag_list})
    return(tag_list)


################分段分词#########################
#content1 = read_aozora_file('fiction_download/61141_悪の帝王_奥増夫_04-第４話-モリソン号賠償金.txt')

def segment_tokenize(content):
    #分段
    #content_split_list = content.split('\r\n')
    segment_size = 15000
    content_split_list = [content[i:i+segment_size] for i in range(0, len(content), segment_size)]

    
    text_list = []
    for content_split in content_split_list:
        text = ja_tokenize_text(content_split)
        text_list.extend(text)
    return(text_list)

def segment_tokenize_tag(content):
    #分段
    #content_split_list = content.split('\r\n')
    segment_size = 15000
    content_split_list = [content[i:i+segment_size] for i in range(0, len(content), segment_size)]

    text_list = []
    for content_split in content_split_list:
        text = ja_tokenize_tag(content_split)
        text_list.extend(text)
    return(text_list)



# ##stopwords
# with open('stopwords_list_new.txt', 'r', encoding='utf-8') as file:
#     stopwords_list = [line.strip() for line in file]

# stopwords_list_add = ['\u3000','一','-']
# stopwords_list.extend(stopwords_list_add)
# #去除函数
# def remove_stopwords(text, stopwords):
#     result = [word for word in text if word not in stopwords]
#     return result

########主题模型##########
def topic_model_fition_corpus(folder_path,suffix = '*txt',topics_num=3,added_stopwords = []):
    print('Starting topic model programme.')
    #读取所有路径下的txt文件
    path =  folder_path + '/' + suffix #  'fiction_download/*.txt'
    txt_files = glob.glob(path)
    
    # 读取txt并并入text_list=[]
    text_list = []
    txt_list = []
    content_tokenize_list = []
    for txt in txt_files:
        with open(txt, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            file_encoding = result['encoding']
            if file_encoding == None:
                print(txt +' can not be encoded. Skip this file.')
                continue
        print(txt + 'is being tokenized.')
        txt_list.append(txt) 
        content = read_aozora_file(txt)
        text_token = segment_tokenize(content)
        content_tokenize_list.append(text_token)
    #return(content_tokenize_list)    
    #return([text_list,txt_list])

        # 去除停用词
    with open('stopwords_list_new.txt', 'r', encoding='utf-8') as file:
        stopwords_list = [line.strip() for line in file]

    stopwords_list_add = ['\u3000','一','-','み','り','ゝ','ふ','ひ','／','く','＼','す','やう','さま','る','ど','よ','め','ね','ま','人','事','ぬ','やう','さま','る','ど','よ','め','ね','ま','\r\n','樣','ぞ','とて','なれ','たる','わ','とて','ひと','あ','いふ','じ','\r\n\u3000','-','―']
    
    stopwords_list.extend(stopwords_list_add)
    stopwords_list.extend(added_stopwords)
    #去除函数
    def remove_stopwords(text, stopwords):
        result = [word for word in text if word not in stopwords]
        return result
    #循环去除
    content_tokenize_list_remove_stopwords = [ remove_stopwords(text = content_tokenize, stopwords = stopwords_list )  for content_tokenize in content_tokenize_list ]
    documents = content_tokenize_list_remove_stopwords

    # 构建词典
    dictionary = corpora.Dictionary(documents)

    # # 将文本转换为向量表示
    corpus = [dictionary.doc2bow(tokens) for tokens in documents]
    return([corpus,dictionary])

def topic_model_fition_text(input_corpus,topics_num=3):
    # # 构建主题模型
    lda_model = models.LdaModel(input_corpus[0], num_topics=topics_num, id2word=input_corpus[1])

    # # 打印主题模型结果
    print('Print Topic Model result:')
    for topic in lda_model.show_topics():
        print(topic)
    
    return(lda_model)
    
    
###########聚类分析###################
def get_fiction_features(content):
    #
    text_token = segment_tokenize(content)
    tag_token = segment_tokenize_tag(content)
    data = {'text': text_token, 'tag': tag_token}
    token_df = pd.DataFrame(data)
    token_df['first_tag'] = [  tag.split('-')[0] for tag in token_df['tag'].tolist()]
    #token_df['first_tag'] = token_df['tag'].split
    #形容词、形容动词（没有）、名词、副词、助词、助动词、动词、连体词、mvr、品词、指示词、句长
    #['副詞', '接続詞', '連体詞', '感動詞', '代名詞', '記号', '形状詞', '名詞', '補助記号', '助動詞', '動詞', '接頭辞', '接尾辞', '形容詞', '空白', '助詞']
    #形容词
    xingrongci_n = token_df['first_tag'].str.contains('形状詞').sum()
    #名词
    mingci_n = token_df['first_tag'].str.contains('名詞').sum()
    #副词
    fuci_n = token_df['first_tag'].str.contains('副詞').sum()
    #助词
    zhuci_n = token_df['first_tag'].str.contains('助詞').sum() #助动词是不是助词--不是
    #助动词
    zhudongci_n = token_df['first_tag'].str.contains('助動詞').sum() 
    #动词
    dongci_n = token_df['first_tag'].str.contains('動詞').sum() 
    #连体词
    liantici_n = token_df['first_tag'].str.contains('動詞').sum() 
    #MVR 形容词+副词+连词/动词
    mvr = (xingrongci_n + fuci_n + liantici_n) / dongci_n
    #品词
    pinci_n = token_df[~token_df['first_tag'].str.contains('記号|空白')].shape[0]
    #指示词list
    zhishici_list = ['これ','それ','あれ','どれ','ここ','そこ','あそこ','どこ','こいつ','そいつ','あいつ','どいつ','こちら','そちら','あちら','どちら','こっち','そっち','あっち','どっち','この','その','あの','どの','こんあ','そんな','あんな','どんな','こう','そう','ああ','どう']
    zhishici_n = token_df['text'].isin(zhishici_list).sum()
    #句长 先求句子数
    def get_juzi_n(df):
        juzi_n = 0
        biaodian = ['」','。','……','！','？'] #标点
        list_data = df['text'].tolist()  # 你的列表数据
        biaodian = ['」', '。', '……', '！', '？']#标点
        previous_element = None

        for element in list_data:
            if element in biaodian and previous_element not in biaodian:
                # 符合条件的操作
                #print(f"当前元素 '{element}' 符合条件")
                juzi_n = juzi_n +1
            # 更新上一个元素
            previous_element = element
        return(juzi_n)
            
    juzi_n = get_juzi_n(df = token_df)
    juchang = token_df.shape[0] / juzi_n
    
    #词数
    cishu = token_df.shape[0]
    return([xingrongci_n/cishu, mingci_n/cishu, fuci_n/cishu, zhuci_n/cishu, zhudongci_n/cishu, liantici_n/cishu, pinci_n/cishu, mvr, zhishici_n/cishu, juchang,cishu])

#################得到路径下所有txt文件的属性#############
import chardet    
def get_features_path(folder_path,suffix = '*txt',clusters_n = 3):
    import seaborn as sns
    from sklearn.cluster import AgglomerativeClustering


    #读取所有路径下的txt文件
    path =  folder_path + '/' + suffix #  'fiction_download/*.txt'
    txt_files = glob.glob(path)
    # 读取txt并并入text_list=[]
    text_list = []
    txt_list = []
    #content_tokenize_list = [] #不需要分词
    content_list = []
    for txt in txt_files:
        with open(txt, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            file_encoding = result['encoding']
            if file_encoding == None:
                print(txt +' can not be encoded. Skip this file.')
                continue
        print(txt + ' is processing.')
        txt_list.append(txt) 
        content = read_aozora_file(txt)
        content_list.append(content)
        #text_token = segment_tokenize(content)
        #content_tokenize_list.append(text_token)
    #对content循环
    features_list = [get_fiction_features(content=content) for content in content_list]
    
    print('get all features from all txt.')
    return([features_list,txt_list])    
############聚类分析##################
#feature_list_result = get_features_path(folder_path = 'fiction_download',suffix = '*会津八一*txt')
def feature_clustering(feature_list_result,clusters_n = 3):
    feature_list_df = pd.DataFrame(feature_list_result[0]) #列表保存的第一个元素转成df
    #feature_list_df = pd.DataFrame(features_list)
    new_rownames_list = [ (os.path.basename(file_path)).replace('.txt', '') for file_path in feature_list_result[1]]

    feature_list_df.index = new_rownames_list
    new_colnames = ['xingrongci_ratio','mingci_ratio','fuci_ratio','zhuci_ratio','zhudongci_ratio','liantici_ratio','pinci_ratio','mvr','zhishici_ratio','juchang','cishu']
    feature_list_df.columns = new_colnames

    # fpath = '/Users/slv/Library/Fonts/YuGothic-1.ttf'
    # prop = fm.FontProperties(fname=fpath)
    # font_dir = ['/Users/slv/Library/Fonts/']
    # for font in fm.findSystemFonts(font_dir):
    #     fm.fontManager.addfont(font)
    # plt.rcParams['font.family'] = 'Yu Gothic'

    df = feature_list_df # 创建 DataFrame
    scaler = MinMaxScaler() # 创建最小-最大标准化对象
    normalized_data = scaler.fit_transform(df) # 对指标进行最小-最大标准化
    df_normalized = pd.DataFrame(normalized_data, columns=df.columns, index=df.index)# 转换为 DataFrame
    print(df_normalized)# 打印标准化后的数据
    #sns.heatmap(df_normalized, annot=True, cmap='RdYlBu')# 绘制热图
    #plt.show()# 显示图形

    
    # 进行聚类
    clustering = AgglomerativeClustering(n_clusters=clusters_n)  # 设置聚类的簇数
    labels = clustering.fit_predict(df_normalized)

    # 绘制热图并加上聚类信息
    sns.clustermap(df_normalized, row_cluster=True, col_cluster=True, #row_colors=labels, col_colors=labels, 
                   cmap='viridis')

    # 显示图形
    plt.show()
    return(df_normalized)  #返回聚类数据矩阵

#################emotion analysis##################
def get_sentiment_analyzer():
    from transformers import AutoModel, AutoTokenizer
    import xformers
    import fugashi
    import torch 
    import transformers
    model = AutoModel.from_pretrained("kit-nlp/bert-base-japanese-sentiment-cyberbullying")
    tokenizer = AutoTokenizer.from_pretrained("kit-nlp/bert-base-japanese-sentiment-cyberbullying")
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from transformers import pipeline
    sentiment_analyzer = pipeline("sentiment-analysis",
                                  model="kit-nlp/bert-base-japanese-sentiment-cyberbullying",
                                  tokenizer="kit-nlp/bert-base-japanese-sentiment-cyberbullying")
    return(sentiment_analyzer)


#sentiment_analyzer = get_sentiment_analyzer()
# sentiment_analyzer("私は幸福である。")


############################翻译######################################
def translation_from_jp_to_en(text):
    import requests
    import random
    import json
    from hashlib import md5
    import pandas as pd
    
    # Set your own appid/appkey.
    appid = '20230405001629367'
    appkey = 'SXgLcp_HNY8_nYdsx0uu'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'auto'
    to_lang =  'en'
    
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    
    query = text

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    
    df = pd.DataFrame(result['trans_result'])
    content_list = df['dst'].tolist()
    return(''.join(content_list))


#translation_from_jp_to_en('私は幸福である。')

def translation_from_jp_to_cn(text):
    import requests
    import random
    import json
    from hashlib import md5
    import pandas as pd
    
    # Set your own appid/appkey.
    appid = '20230405001629367'
    appkey = 'SXgLcp_HNY8_nYdsx0uu'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'auto'
    to_lang =  'cn'
    
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    
    query = text

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    
    df = pd.DataFrame(result['trans_result'])
    content_list = df['dst'].tolist()
    return(''.join(content_list))


def translation_from_lan_to_jp(text):
    import requests
    import random
    import json
    from hashlib import md5
    import pandas as pd
    
    # Set your own appid/appkey.
    appid = '20230405001629367'
    appkey = 'SXgLcp_HNY8_nYdsx0uu'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'auto'
    to_lang =  'jp'
    
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    
    query = text

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    
    df = pd.DataFrame(result['trans_result'])
    content_list = df['dst'].tolist()
    return(''.join(content_list))