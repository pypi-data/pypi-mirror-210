import json


def json_update(data, target_data: dict):
    for key in list(target_data.keys()):
        if key.startswith('@'):  # 如果key以@开头，则表示该key为替换报文中的key
            path = key.split('@')[1].split('.')[:-1]  # 去掉@，分割path
            name = key.split('@')[1].split('.')[-1]  # 取最后一个key
            target_data[name] = target_data[key]  # 将替换报文中的key替换为目标报文中的key
            target_data.pop(key)  # 删除分割前@字符 替换报文中的key
            data_int = [int(i) if i.isdigit() else i for i in path]  # 处理列表数据，将path中的数字字符串转换为数字
            data_sec = ''.join([str([i]) for i in data_int])  # 将数字字符串替换为数字后重新按照列表的形式拼接path
            try:
                data_res = eval('data' + data_sec)
                update_allvalues(data_res, target_data)
                target_data.pop(name)  # 删除分割后的替换报文中的key
            except TypeError:
                raise TypeError('请检查你的路径是否正确，列表元素需要用数字索引获取')
            except KeyError:
                raise TypeError('请检查你的路径是否正确，大概率是键名有误')
        else:
            update_allvalues(data, target_data)


def update_allvalues(data, kw: dict):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in kw:
                data[k] = kw[k]
            else:
                data[k] = update_allvalues(v, kw)
        return data
    elif isinstance(data, list):
        for k, item in enumerate(data):
            data[k] = update_allvalues(item, kw)
        return data
    elif isinstance(data, str):
        try:  # 兼容报文格式为序列化后的字典："{'name':'lyh'}"
            d = eval(data)
            if isinstance(d, dict):
                return json.dumps(update_allvalues(d, kw))
            else:
                return data
        except NameError:  # 未定义
            return data
        except SyntaxError:  # 'api_version': 'V1.0',
            return data
    else:
        return data


def remove_keys(data, keys: list):
    if isinstance(data, dict):
        for k, v in data.copy().items():  # RuntimeError: dictionary changed size during iteration
            if k in keys:
                data.pop(k)
            else:
                remove_keys(v, keys)
        return data
    elif isinstance(data, list):
        for k, item in enumerate(data):
            data[k] = remove_keys(item, keys)
        return data
