import re
class ForceSegmentor(object):
    def __init__(self):
        self.forcelist = []

    def load(self, filepath):
        xlen = 0
        with open(filepath, 'r',encoding='UTF-8-sig') as file:
            line = file.readline()
            while line:
                if ('#' in line):
                    line = file.readline().strip()
                    continue
                xlen += 1
                self.forcelist.append(ForceSegmentorItem(line))
                line = file.readline()
        self.compilelist = []
        y = 0
        #xlen = 60
        stop = False
        while not stop:
            comstr = '(?:'
            for x in range(xlen):
                z = y * xlen + x
                if z > len(self.forcelist) - 1:
                    stop = True
                    break
                if x > 0:
                    comstr += '|'
                #待匹配的字符中存在*号等用于正则表达式的特殊字符
                if '*' in self.forcelist[z].get_text():
                    comstr += '\\'
                comstr += self.forcelist[z].get_text()
            comstr += ')'
            self.compilelist.append(re.compile(comstr))
            y += 1

    def find_in_dict(self, sentence):
        de_sentence = sentence
        for compilestr in self.compilelist:
            result = compilestr.search(de_sentence)
            if result:
                # 找到句子中包含的字典中的词
                return result.group()
        return None

    def merge(self, sentence, words):
        result = words
        found_word = self.find_in_dict(sentence)
        if found_word:
            # 可能同一个词在这句话里出现多次
            indexs_start = []
            # 合并的词首尾距离
            index_distance = 0
            index_start = -1
            strm = ''
            for i, word in enumerate(words):
                wl = len(word)
                if (index_start == -1 and word == found_word[0:wl]):
                    index_start = i
                    strm += word
                elif (index_start != -1):
                    strm += word
                    if (strm == found_word):
                        # 已经完全匹配
                        indexs_start.append(index_start)
                        index_distance = i - index_start + 1
                        index_start = -1
                        strm = ''
                    elif (strm not in found_word):
                        # 现在连接得到的多个词是错误的，重新开始匹配
                        index_start = -1
                        strm = ''
            result = []
            i = 0
            while (i < len(words)):
                word = words[i]
                if (i in indexs_start):
                    result.append(found_word)
                    i += index_distance
                else:
                    result.append(word)
                    i += 1
        return result

class ForceSegmentorItem(object):
    def __init__(self, line):
        self.text = line.replace('\n', '')

    def get_text(self):
        return self.text
