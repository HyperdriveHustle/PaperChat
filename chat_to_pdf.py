'''
使用 get_paper_from_pdf 之后，对内容进行分类摘要、embedding存储等
'''
import os
from get_paper_from_pdf import Paper
# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)


def paper_chat(paper):
    '''
    拆分 paper 的部分，
    :return:
    '''
    print("*" * 40)
    print("*" * 40)
    for key, value in paper.section_text_dict.items():
        if key in ['Abstract', 'Introduction',]:
            print("key = {}, value = {}".format(key, value))
            print("*" * 40)


def run():
    path = os.path.join(current_dir, 'data/paper.pdf')
    paper = Paper(path=path)
    paper.parse_pdf()

    paper_chat(paper)



if __name__ == '__main__':
    run()