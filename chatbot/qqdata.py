# coding=utf-8
# Based on code from https://github.com/AlJohri/OpenSubtitles
# by Al Johri <al.johri@gmail.com>
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import os.path
import sys
import json
import re
import pprint
import jieba
from gzip import GzipFile
from tqdm import tqdm
import pickle
import jieba.posseg as pseg
"""
Load the opensubtitles dialog corpus.
"""


class QQData(object):
    """

    """

    def __init__(self, dirName):
        """
        Args:
            dirName (string): directory where to load the corpus
        """

        # Hack this to filter on subset of Opensubtitles
        # dirName = "%s/en/Action" % dirName

        print("Loading QQ conversations in %s." % dirName)
        self.conversations = []
        self.date_re = re.compile(
            r"^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}")
        self.ignore_re = re.compile(r"\s")
        self.conversations = self.loadConversations(dirName)

    def loadConversations(self, dirName):
        """
        Args:
            dirName (str): folder to load
        Return:
            array(question, answer): the extracted QA pairs
        """
        conversations = []
        dirList = self.filesInDir(dirName)
        for filepath in tqdm(dirList, "OpenSubtitles data files"):
            print(filepath)
            if filepath.endswith("txt"):
                try:
                    conversations.extend(self.genList(filepath))
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
        return conversations

    def getConversations(self):
        return self.conversations

    def fromPickle(self, filepath):
        with open(filepath,"rb") as fin:
            conversations = pickle.load(fin)
        return conversations

    def dumptoPickle(self, filepath, conversations):
        with open(filepath, "wb") as fout:
            pickle.dump(conversations, fout)

    def genList(self, filepath):
        skip_head = False  # 跳过最开始的头部
        conversations = []
        context = {}
        current_line = ""
        last_line = ""
        origin_file, ext = os.path.splitext(filepath)
        if os.path.exists(origin_file + ".dump"):
            return self.fromPickle(origin_file + ".dump")
        with open(filepath) as f:
            lines = f.readlines()
            for line in tqdm(lines, "QQ data lines"):
                search_result = self.date_re.search(line)
                if search_result:  # 到达下一对话了
                    if skip_head and last_line and current_line:
                        tmp = {}
                        tmp["lines"] = []
                        tmp["lines"].append(self.getLine(last_line))
                        tmp["lines"].append(self.getLine(current_line))
                        if self.filter(tmp):
                            conversations.append(tmp)
                    skip_head = True
                    last_line = current_line
                    current_line = ""
                else:  # 还在当前对话里
                    current_line += line
        self.dumptoPickle(origin_file + ".dump", conversations)

        return conversations

    def getLine(self, sentence):
        line = {}
        sentence = sentence.replace("[图片]", "")
        sentence = sentence.replace("[表情]", "")
        sentence = re.sub(self.ignore_re, "", sentence)
        words = list(pseg.cut(sentence))
        if len(words) > 10 or len(words) == 0:  # 大于10的句子不要
            return None
        line["text"] = words
        return line

    def filter(self, lines):
        question = lines["lines"][0]
        answer = lines["lines"][1]
        return question and answer

    def filesInDir(self, dirname):
        result = []
        for dirpath, dirs, files in os.walk(dirname):
            for filename in files:
                fname = os.path.join(dirpath, filename)
                result.append(fname)
        return result
if __name__ == '__main__':
    d = QQData("data/qq/")
