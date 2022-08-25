import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
from force_segmentor import *


#The directory of word segmentation models
LTP_DIR = "E:/Project/ltp_data/ltp_data_v3.4.0"

class LTP_Model:
    def __init__(self):
        user_seg = './model/ltp/user_seg.txt'
        user_postag = './model/ltp/user_postag.txt'

        self.segmentor = Segmentor()
        cws_model_path = os.path.join(LTP_DIR, "cws.model")
        self.segmentor.load_with_lexicon(cws_model_path, user_seg)

        self.postagger = Postagger()
        pos_model_path = os.path.join(LTP_DIR, "pos.model")
        self.postagger.load_with_lexicon(pos_model_path, user_postag)

        self.parser = Parser()
        self.parser.load(os.path.join(LTP_DIR, "parser.model"))

        self.forcesegmentor = ForceSegmentor()
        self.forcesegmentor.load('./model/ltp/force_seg.txt')


    def model_release(self):
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()

def get_ltp_info(ltp_model,sentence):
    words_sour = list(ltp_model.segmentor.segment(sentence))  # segmentation

    words = ltp_model.forcesegmentor.merge(sentence, words_sour)  #force segmentation
    postags = list(ltp_model.postagger.postag(words))  # POS tag
    arcs = list(ltp_model.parser.parse(words, postags))  #dependency

    return words,postags,arcs

