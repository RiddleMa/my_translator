# -*- coding: utf-8 -*-
'''
对pdf进行读取操作，并修改格式，使断句重新组成行。
https://blog.csdn.net/zyc121561/article/details/77877912?locationNum=2&fps=1
'''
__author__ = 'yooongchun'

import sys
import importlib
import re
importlib.reload(sys)

from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import *
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

'''
解析pdf文件，获取文件中包含的各种对象
'''



if __name__ == '__main__':
    # pdf_path = r'dd.pdf'
    # parse(pdf_path)
    modify_txt('test')
