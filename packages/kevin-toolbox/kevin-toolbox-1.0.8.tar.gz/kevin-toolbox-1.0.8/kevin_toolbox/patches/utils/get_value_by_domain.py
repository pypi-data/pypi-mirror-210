import re


def get_value_by_name(var, name):
    """
        通过解释名字得到取值方式，然后到 var 中获取对应部分的值。

        参数：
            var:            任意支持索引取值的变量
            name:           <string> 取值方式。
                                由多组 "<解释方式><键>" 组成。
                                解释方式支持以下几种:
                                    "@"     使用 eval() 读取键
                                    ":"     使用 str() 读取键
                                    "|"     依次尝试 str() 和 eval() 两种方式
                                示例:
                                    "@100"      表示读取 var[eval("100")]
                                    ":epoch"    表示读取 var["epoch"]
                                    "|1+1"    表示首先尝试读取 var["1+1"]，若不成功则尝试读取 var[eval("1+1")]
                                假设 var=dict(acc=[0.66,0.78,0.99])，如果你想读取 var["acc"][1] => 0.78，那么可以将 domain 写成：
                                    ":acc@1" 或者 "|acc|1" 等。
                                注意，在 domain 的开头也可以添加任意非解释方式的字符，本函数将直接忽略它们，比如下面的:
                                    "var:acc@1" 和 "xxxx|acc|1" 也能正常读取。
    """
    assert isinstance(name, (str,))

    key_ls = re.split('[:@|]', name)
    # assert len(key_ls) > 0
    flag_idx = len(key_ls[0])
    for key in key_ls[1:]:
        flag = name[flag_idx]
        flag_idx += len(key) + 1
        #
        if flag == "@":
            var = var[eval(key)]
        elif flag == "|":
            try:
                var = var[key]
            except:
                var = var[eval(key)]
        else:  # ":"
            var = var[key]

    return var


if __name__ == '__main__':
    print(get_value_by_name(var=dict(acc=[0.66, 0.78, 0.99]), name="|acc|0"))
    print(get_value_by_name(var=dict(acc=[0.66, 0.78, 0.99]), name="www|acc|0"))
