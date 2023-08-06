
from keystem._kmeans import KMeans



import pandas as pd
import numpy as np

import spacy
# Load the spacy model that you have installed

import nltk
from keybert import KeyBERT



class KeyStem:
    def __init__(
        self,
        spacy_ln='en_core_web_md',
        kw_model = 'all-MiniLM-L6-v2',
        clust_distance = 1.9
    ):
        try:
            self.nlp = spacy.load(spacy_ln)
        except:
            import spacy.cli
            spacy.cli.download(spacy_ln)
            self.nlp = spacy.load(spacy_ln)
            
        try:
            nltk.tokenize.sent_tokenize(' some text')
        except:
            nltk.download('punkt')
            
        self.kw_model = KeyBERT(kw_model)
        self.clust_distance = clust_distance
        self.kmeans = KMeans(max_distance=clust_distance)
    

    # with open(r'D:\Users\NKiran\Downloads\text_file\text file\Battery supplies.txt', 'rb') as f:
    #     text = f.read().decode()


    def preprocess(
        self,
        text, 
        pos=True
    ):
        text = text.lower()
        doc = self.nlp(text)
        tags = []
        for i in range(len(doc)):
            if pos:
                if doc[i].pos_ in [ 'DET', 'PROPN', 'NOUN']:
                    tags.append(doc[i])
            else: 
                tags.append(doc[i])
                
        return tags 

    def get_keygroups(
        self,
        text,
        by_sents=False,
        pos=True,
        keyword_thresh = 0.3
    ):
        if isinstance(text, list) and text:
            keywords = text
            keywords = [(k, 1) for k in keywords]
        else:
            if by_sents:    
                # text = rashes_text
                sents = nltk.tokenize.sent_tokenize(text)

                keywords = []
                for sent in sents:
                    phrases = self.kw_model.extract_keywords(sent, keyphrase_ngram_range=(1, 2), stop_words=None)
                    keywords.extend([p for p in phrases if p[1]>keyword_thresh])
                # keywords =[k[0] for k in keywords]
            else:
                keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
                keywords =[k for k in keywords if k[1]>keyword_thresh]
                
        res = pd.DataFrame()
        res['keywords'] = keywords
        res['text'] = [p[0] for p in res['keywords']]
        # res['text'] = keywords

        res['features'] = res['text'].apply(lambda x: self.preprocess(x, pos=pos))
        res = res.reset_index(drop=True)
        word_frame = res#[['features','keywords']]
        word_frame = word_frame.explode('features')
        word_frame = word_frame.reset_index()
        # word_frame['frame_index'] = word_frame.reset_index
        features = np.vstack([i.vector for i in word_frame['features']])


        clusters, centroids = self.kmeans.predict(features)


        for c_id, cluster in enumerate(clusters):
            word_frame.loc[cluster, 'cluster'] = c_id
            
            
        word_frame1 = word_frame.groupby(['index', 'keywords']).agg({
            'features':lambda x: ' '.join([y.text for y in x]),
            'cluster':lambda x: x.tolist()
        })
        word_frame1 = word_frame1.explode('cluster')
        word_frame1 = word_frame1.reset_index()



        word_frame1['score'] = word_frame1['keywords'].str[1]

        frames = []
        for gid, fr in word_frame1.groupby('cluster'):
            fr = fr.sort_values('score', ascending=False)
            fr['label'] = fr['features'].iloc[0]
            frames.append(fr)

        result_frame = pd.concat(frames)

        return result_frame








