import csv
import json
import os

import keras
import re
import jieba
from keras.preprocessing.sequence import pad_sequences
from gensim.models import KeyedVectors
from transformers import TFBertForSequenceClassification
import tensorflow as tf
from transformers import BertTokenizer
bert2 = TFBertForSequenceClassification.from_pretrained(
    os.getenv("WEIBO_SENTIMENT_BERT_PATH", "sentiment_analysis/bert_sentiment2")
)
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese', do_lower_case=True)


def predict_sentiment(text, cn_model, model):
    text = re.sub(r"[\s\.!/_,$%^*(+\"\']+|[+\u2014\uff01\uff0c\u3002\uff1f\u3001~@#\uffe5%\u2026&*\uff08\uff09:]+", "", text)
    # 分词
    cut = jieba.cut(text)
    cut_list = [i for i in cut]
    for i, word in enumerate(cut_list):
        try:
            cut_list[i] = cn_model.key_to_index[word]
        except KeyError:
            cut_list[i] = 0
    # padding
    tokens_pad = pad_sequences([cut_list], maxlen=107,
                               padding='pre', truncating='pre')
    # 预测
    result = model.predict(x=tokens_pad)
    return result[0][0]


def predict_sentiment_bert(content):
    predict_input = tokenizer.encode(content, truncation=True, padding=True, return_tensors="tf")
    tf_output = bert2.predict(predict_input)[0]
    tf_prediction = tf.nn.softmax(tf_output, axis=1)
    return tf_prediction[0].numpy()[1]


def sentiment(user_id, model, cn_model):
    print(user_id)
    dict_blog = {}
    dict_score_comment = {}

    for pinpai in ['huawei']:
        with open('crawl_weibo/weibo/comment' + user_id + pinpai + '.json', 'r', encoding='utf-8') as reader1:
            for row in reader1:
                json_row = json.loads(row)
                comment = json_row['comment']['comment']
                comment_likes = json_row['comment']['likes']
                id = json_row['id']
                if id not in dict_blog:
                    dict_blog[id] = {'content': json_row['content'], 'likes': json_row['likes'],
                                     'time': json_row['time']}
                if comment == "" or "回复@" in comment or comment == "转发微博":
                    score_comment = 0.5
                else:
                    score_comment = predict_sentiment_bert(comment)
                if id not in dict_score_comment:
                    dict_score_comment[id] = [(score_comment, comment_likes)]
                else:
                    dict_score_comment[id].append((score_comment, comment_likes))

        with open(user_id + pinpai + 'output.json', 'w', encoding='utf-8') as writer:
            for id in dict_blog:
                writer.write(json.dumps({'id': id,
                                         'content': dict_blog[id]['content'],
                                         'content_score': predict_sentiment_bert(dict_blog[id]['content']),
                                         'time': dict_blog[id]['time'],
                                         'likes': dict_blog[id]['likes'],
                                         'comment_score': dict_score_comment[id]
                                         }, ensure_ascii=False, default=float))
                writer.write('\n')

def old_sentiment(user_id):
    dict_blog = {}
    dict_score_comment = {}

    with (open('weibo/comment' + user_id + 'csv.json', 'r', encoding='utf-8') as reader1):
        for row in reader1:
            json_row = json.loads(row)
            comment = json_row['comment']['comment']
            comment_likes = json_row['comment']['likes']
            id = json_row['id']
            if id not in dict_blog:
                dict_blog[id] = {'content': json_row['content'], 'likes': json_row['likes'],
                                 'time': json_row['time']}
            if comment == "" or "回复@" in comment or comment == "转发微博":
                score_comment = 0.5
            else:
                score_comment = predict_sentiment_bert(comment)
            if id not in dict_score_comment:
                dict_score_comment[id] = [(score_comment, comment_likes)]
            else:
                dict_score_comment[id].append((score_comment, comment_likes))

    with open(user_id+ 'outputnew.json', 'w', encoding='utf-8') as writer:
        for id in dict_blog:
            writer.write(json.dumps({'id': id,
                                     'content': dict_blog[id]['content'],
                                     'content_score': predict_sentiment_bert(dict_blog[id]['content']),
                                     'time': dict_blog[id]['time'],
                                     'likes': dict_blog[id]['likes'],
                                     'comment_score': dict_score_comment[id]
                                     }, ensure_ascii=False, default=float))
            writer.write('\n')

if __name__ == "__main__":
    # for id in ['2561744167']:
    #     sentiment(id)

    # cn_model = KeyedVectors.load_word2vec_format('sentiment_analysis/sgns.weibo.bigram',
    #                                              binary=False)
    # model = keras.models.load_model("sentiment_analysis/sentiment")
    old_sentiment('6048569942')
    # with open('list_bozhu.txt', 'r', encoding='utf-8') as reader:
    #     for row in reader:
    #         id = row.split()[1]
    #         # if id not in ['2022252207', '2561744167', '5821279480', '7109370363']:
    #         # sentiment(id, model, cn_model)
    #         sentiment(id, bert2, tokenizer)
