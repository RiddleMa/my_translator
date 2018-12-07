from urllib import request, parse
import json
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
对pdf进行读取操作，并修改格式，使断句重新组成行。
https://blog.csdn.net/zyc121561/article/details/77877912?locationNum=2&fps=1
'''
'''
使用翻译工具实现文档翻译。英文-->中文
英文不好，文档翻译起来需要一段一段粘过去看。使用代码把所有文档都翻译成汉语。
参考网址：
https://blog.csdn.net/weixin_42251851/article/details/80489403
'''

# 解析pdf文件函数
def parse_pdf(pdf_path):
    """
    读取pdf文件，保存为
    待修改：如果不能直接读取文字，尝试使用Tesseract (OCR庫)
    :param pdf_path:
    :return:
    """
    fp = open(pdf_path, 'rb')  # 以二进制读模式打开
    # 用文件对象来创建一个pdf文档分析器
    parser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    parser.set_document(doc)
    doc.set_parser(parser)

    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # 用来计数页面，图片，曲线，figure，水平文本框等对象的数量
        num_page, num_image, num_curve, num_figure, num_TextBoxHorizontal = 0, 0, 0, 0, 0

        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages(): # doc.get_pages() 获取page列表
            num_page += 1  # 页面增一
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            for x in layout:
                if isinstance(x,LTImage):  # 图片对象
                    num_image += 1
                if isinstance(x,LTCurve):  # 曲线对象
                    num_curve += 1
                if isinstance(x,LTFigure):  # figure对象
                    '''2018.11.27 修改 发现部分pdf文本被识别为LFTFigure对象，将该文本内容添加入结果'''
                    num_figure += 1
                    # 保存文本内容
                    new_path = pdf_path[:-3]+'txt'
                    with open(new_path, 'a',encoding='utf8') as f:
                        x.get_textboxes()
                        for x_in in x:
                            if isinstance(x_in, LTChar):
                                results = x_in.get_text()
                                f.write(results)

                if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                    num_TextBoxHorizontal += 1  # 水平文本框对象增一
                    # 保存文本内容
                    new_path = pdf_path[:-3]+'txt'
                    with open(new_path, 'a',encoding='utf8') as f:
                        results = x.get_text()
                        f.write(results + '\n')
        print('对象数量：\n','页面数：%s\n'%num_page,'图片数：%s\n'%num_image,'曲线数：%s\n'%num_curve,'水平文本框：%s\n'
              %num_TextBoxHorizontal)

def modify_txt(txt_path):
    """
    修改翻译后的txt文档
    :return:
    """
    with open(txt_path, 'r', encoding='utf8') as f:
        lines = f.readlines()
        new_line = ''
        for line in lines:
            if(line.endswith('-\n')): # -造成词语分割
                line = line.replace('-\n','')
            new_line+=line
        new_line = re.sub(r'\.\n', '.\n\n', new_line)  # 把 .\n保留防止下一行删除
        new_line = re.sub(r'(?<!\n)\n(?!\n)',' ',new_line)  # 删除每行后的单个回车
        new_line = re.sub(r'\n{2,}','\n',new_line)      # 多次回车改为一次
    with open(txt_path[:-4]+ '_mod.txt', 'w', encoding='utf8') as f:
        f.writelines(new_line)

def baidu_tanslator(input_str):
    """
    调用百度翻译接口
    :return:
    """
    req_url = 'https://fanyi.baidu.com/transapi'
    Form_Data = {"query": input_str, 'from': 'en', 'to': 'zh'}
    data = parse.urlencode(Form_Data).encode('utf-8')
    response = request.urlopen(req_url, data)
    html = response.read().decode('utf-8')
    # print(html)  # 可以看出html是一个json格式      translate_results = json.loads(html)      for item in translate_results['data']:          for items in item:              print(item[items])</
    # 可以看出html是一个json格式
    translate_results = json.loads(html)  # 以json格式载入
    if 'error' in translate_results:
        translate_results = 'error'
    else:
        translate_results = translate_results['data'][0]['dst']  # json格式调取
    return translate_results  # 输出结果
def youdao_translator(input_str):
    """
    调用有道翻译接口
    :return:
    """
    req_url = 'http://fanyi.youdao.com/translate'  # 创建连接接口
    # 创建要提交的数据
    Form_Date = {}
    Form_Date['i'] = input_str  # 要翻译的内容可以更改
    Form_Date['doctype'] = 'json'

    data = parse.urlencode(Form_Date).encode('utf-8')  # 数据转换
    response = request.urlopen(req_url, data)  # 提交数据并解析
    html = response.read().decode('utf-8')  # 服务器返回结果读取
    # print(html)
    # 可以看出html是一个json格式
    translate_results = json.loads(html)  # 以json格式载入
    translate_results = translate_results['translateResult'][0]  # json格式调取
    return_results=''
    for sub_result in translate_results:
        return_results+=sub_result['tgt']
    return return_results  # 输出结果

def trans_txt(file_mod,tol='baidu'):
    print('===开始翻译===')
    if tol=='youdao':   #默认使用百度翻译
        translator = youdao_translator
    else:
        translator = baidu_tanslator
    with open(file_mod,'r',encoding='utf8') as f:
        lines = f.readlines()
        new_lines = []
        line_len = len(lines)
        print('共',line_len,'行')
        for i in range(line_len):
            if (i % 10==0):
                print('第',i,'行')
            line_result = translator(lines[i])
            # print(line_result)
            new_lines.append(line_result+'\n')
    print('===翻译结束===')
    with open(file_mod[:-8]+'_'+tol+'.txt','w',encoding='utf8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    file_path = 'pdf/Neural Architectures.pdf'
    txt_path = file_path[:-3]+'txt'
    mod_path = file_path[:-4]+'_mod.txt'

    '''step1:读取pdf文档中的字符，保存为txt文件'''
    # parse_pdf(file_path)
    '''step2:手动修改txt文档，删除不翻译的内容，参照readme'''
    # done = input('参照README.TXT修改txt文档,修改完成请按Enter继续程序')
    '''step3:程序自动修改一部分错误'''
    # modify_txt(txt_path)
    '''step4:使用翻译工具进行翻译'''
    trans_txt(mod_path,tol='baidu')      # baidu
