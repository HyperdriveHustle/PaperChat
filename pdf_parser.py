'''
参考 researchGPT 写解析 pdf
    https://github.com/mukulpatnaik/researchgpt/blob/main/main.py
以这篇为例: https://arxiv.org/pdf/2205.10343.pdf
'''
import PyPDF2
import fitz  # PyMuPDF
import io
from PIL import Image
import tabula
import pytesseract


def extract_text(pdf):
    '''
    参考 researchGPT 重新写合并原则，需要考虑以下几点：
        - 在有公式的时候，字体大小可能不一样，不能简单地按照字体大小合并
        - 同一行的文本应该放在一起
    :param pdf:
    :return:
    '''
    number_of_pages = len(pdf.pages)
    print(f"Total number of pages: {number_of_pages}")
    paper_text = []
    for i in range(number_of_pages):
        page = pdf.pages[i]
        page_text = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            '''
            当 pdfplumber 库解析 PDF 文件时，它会将每个页面分成多个文本块，
            并将每个文本块的文本内容、位置、字体等信息传递给名为 visitor_text 的函数，以便后续处理。
            在这个函数中，我们可以通过指定 visitor_text 函数的参数来访问每个文本块的信息。

            在 visitor_body 函数中，我们首先从 tm 参数中获取文本块的 x、y 坐标，
            然后检查文本块是否在页眉和页脚范围内（通过 y 坐标的值来判断），并且忽略长度小于等于 1 的文本块。
            如果文本块不在页眉和页脚范围内，且长度大于 1，
            则将该文本块的字体大小、文本内容、x、y 坐标等信息添加到 page_text 列表中，以便后续处理。

            text: 当前文本块的文本内容。
            cm: 当前文本块的转换矩阵，表示文本在页面上的位置和方向。
            tm: 当前文本块的文本矩阵，表示文本在页面上的位置和方向。
            fontDict: 当前文本块的字体信息。
            fontSize: 当前文本块的字体大小。
            --> 下标：6.9738
            --> 正文：9.9626
            '''
            x = tm[4]
            y = tm[5]
            # ignore header/footer
            # (y > 50 and y < 800)
            print(text)
            if y > 50 and (len(text.strip()) > 1):
                page_text.append({
                    'fontsize': fontSize,
                    'text': text.strip().replace('\x03', ''),
                    'page': i,
                    'x': x,
                    'y': y
                })
                print("> page = {}: {}\n-----------".format(i, page_text[-1]))

        _ = page.extract_text(visitor_text=visitor_body)

        blob_font_size = None
        blob_text = ''
        processed_text = []

        for index, t in enumerate(page_text):
            # x y 坐标一致应该放在同一行
            if index > 0:
                x, y, cur_page = t['x'], t['y'], t['page']
                pre_x, pre_y = page_text[index-1]['x'], page_text[index-1]['y']
                pre_page = page_text[index - 1]['page']
                if y == pre_y and cur_page == pre_page:
                    blob_text += f" {t['text']}"
                    continue

            # 如果当前字号和之前一样，则合并
            if t['fontsize'] == blob_font_size:
                blob_text += f" {t['text']}"
                # 如果长度大于 2000 则存储
                if len(blob_text) >= 2000:
                    # print("blob_text = {}".format(blob_text))
                    processed_text.append({
                        'fontsize': blob_font_size,
                        'text': blob_text,
                        'page': i
                    })
                    blob_font_size = None
                    blob_text = ''
            else:  # 如果字号变了，
                # 如果字号变了，且之前没存储，且现在有有效的文本
                # 就保存之前的结果
                if blob_font_size is not None and len(blob_text) >= 1:
                    # print("processed_text = {}".format(processed_text))
                    processed_text.append({
                        'fontsize': blob_font_size,
                        'text': blob_text,
                        'page': i
                    })
                blob_font_size = t['fontsize']
                blob_text = t['text']

        if len(blob_text) > 0:
            processed_text.append({
                'fontsize': blob_font_size,
                'text': blob_text,
                'page': i
            })
        paper_text += processed_text
    print("Done parsing paper")
    for pt in paper_text:
        print(">> paper_text = {}".format(pt))
    return paper_text


pdf_path = "data/paper.pdf"
with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    extract_text(reader)