import numpy as np
import pandas as pd


def Match_mz_value(lib, data, ppm):
    lib = str(lib)
    data = str(data)
    lib = pd.read_csv(f'{lib}', header=0, low_memory=False)
    data = pd.read_csv(f'{data}', header=0, low_memory=False)
    list = pd.DataFrame()
    list['lib'] = lib
    list['up'] = (ppm / 1000000) * list['lib'] + list['lib']
    list['low'] = -((ppm / 1000000) * list['lib'] - list['lib'])
    list['m/z'] = np.nan
    for i in range(len(lib)):
        for j in range(len(data)):
            if list.loc[i, 'up'] > data[j] > list.loc[i, 'low']:
                if [abs(list.loc[i, 'lib'] - list.loc[i, 'm/z']) > abs(list.loc[i, 'lib'] - data[j])] or list.loc[
                    i, 'm/z'] == np.nan:
                    list.loc[i, 'number'] = j + 3
                    list.loc[i, 'm/z'] = data[j]
                    list.loc[i, 'error_ppm'] = (abs(list.loc[i, 'lib'] - data[j]) / list.loc[i, 'lib']) * 1000000
    list.to_csv('Match_mz_value.csv')
    return list


def get_lib(lib: str):
    lib = str(lib)
    lib = pd.read_csv(f'{lib}', header=0, low_memory=False)
    lib.fillna('unknow', inplace=True)
    # 创建一个lib1，和lib有相同列名的空表
    lib1 = pd.DataFrame(columns=lib.columns)
    last_formula = '0'
    last_name = '0'
    for i in lib.index:
        if lib.loc[i, 'Formula'] != last_formula:
            # 在lib1中添加一行
            lib1.loc[i] = lib.loc[i]
            last_formula = lib.loc[i, 'Formula']
            last_name = lib.loc[i, 'Name']
        else:
            if lib.loc[i, 'Name'] != last_name:
                lib1.loc[i] = lib.loc[i]
                last_name = lib.loc[i, 'Name']
                last_formula = lib.loc[i, 'Formula']
    lib = lib1
    lib1 = pd.DataFrame(columns=lib.columns)
    last_formula = '0'
    last_name = '0'
    # 合并相同有Formula的Name，并去除相同Formula的相同的Name
    for i in lib.index:
        if lib.loc[i, 'Formula'] != last_formula:
            lib1.loc[i] = lib.loc[i]
            last_formula = lib.loc[i, 'Formula']
            last_name = lib.loc[i, 'Name']
        else:
            if lib.loc[i, 'Name'] != last_name:
                lib.loc[i, 'Name'] = last_name + '&' + lib.loc[i, 'Name']
                lib1.loc[i] = lib.loc[i]
                last_name = lib.loc[i, 'Name']
                last_formula = lib.loc[i, 'Formula']
    lib1 = lib1.drop_duplicates(subset=['Formula'], keep='last')  # 删除重复的Formula
    lib1 = lib1.reset_index(drop=True)
    # 保存lib1
    lib1.to_csv(f'{lib}' + "-1.csv", index=False)
    return lib1