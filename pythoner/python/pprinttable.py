# coding: utf-8
from collections import namedtuple

#
#   常用脚本输出工具：表格化输出。
#   1.利用命名元组构建table
#   2.表格化输出数据
#

def build_tuple_table(headers, data_list, filter=None):
    """
        利用命名元组构建数据table
        headers：列表的头部栏
        filter：对data list进行自定义过滤
    """
    Row = namedtuple('Row', headers)
    if filter:
        table = [Row(**d) for d in filter(data_list)]
    else:
        table = [Row(**d) for d in data_list]
    return table


def pprinttable(rows):
    """ 说明：
        根据行数(1)输出不同形状的表格，要求每一行的数据类型均相同！
    """
    if len(rows) > 1:
        headers = rows[0]._fields

        # 列数
        column_lengths = len(rows[0])

        # 取同一列中长度最长的项长度为该列的宽度
        column_widths = []
        for i in range(column_lengths):
            column_widths.append(len(max([str(x[i]) for x in rows]+[headers[i]], key=lambda x:len(str(x)))))

        # 获取每一个字符的格式化字符串(全部按照字符串处理,不考虑整形)
        # '%%':输出% (转义)
        # '%-ns'：输出字符串s，若不够n位，在其后用"空格"补齐n位
        formats = ["%%-%ds" % w for w in column_widths]
        pattern = " | ".join(formats)

        # print header row
        print pattern % tuple(headers)

        # print separator line
        separator = "-+-".join(['-'*w for w in column_widths])
        print separator

        # print data rows
        for line in rows:
            print pattern % tuple(line)

    elif len(rows) == 1:
        row = rows[0]
        header_width = len(max(row._fields, key=lambda x: len(x)))
        for i in range(len(row)):
            print "%*s = %s" % (header_width, row._fields[i],row[i])


if __name__=='__main__':
    data = [{   'name': 'a',
                'age': 12,
                'gender': 'man',
                'score': '123',
                'other': 'none',
            },
            {   'name': 'b',
                'age': 23,
                'gender': 'woman',
                'score': '110',
                'other': 'none',
            },
            {   'name': 'c',
                'age': 120,
                'gender': 'man',
                'score': '60',
                'other': 'none',
            }]
    
    need_fields = ['name', 'age', 'gender']
	
    def get_need_fields(fields):
        for field in fields:
            # do someting
            yield {
                'name': field['name'],
                'age': field['age'],
                'gender': field['gender'],
            }

    table = build_tuple_table(need_fields, data, get_need_fields)
    pprinttable(table)
