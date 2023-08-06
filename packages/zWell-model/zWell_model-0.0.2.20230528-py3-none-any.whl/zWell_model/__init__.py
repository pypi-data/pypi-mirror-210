# -*- coding: utf-8 -*-
# @Time : 2023/5/13 20:17
# @Author : zhao
# @Email : liming7887@qq.com
# @File : __init__.py.py
# @Project : Keras-model

from zWell_model.convNet.ConvNetV1 import ConvNetV1
from zWell_model.convNet.ConvNetV2 import ConvNetV2
from zWell_model.denseNet.DenseNetV1 import DenseNetV1
from zWell_model.resNet.ResNetV1 import ResNetV1

net_dict1 = {
    'version': '0.0.2.20230528',
    'Cnn1': ConvNetV1,
    'Cnn2': ConvNetV2,
    'RCnn1': ResNetV1,
    'Dn1': DenseNetV1
}


def __getattr__(name: str):
    """
    使用神经网络简称从包中获取到指定的神经网络模型对象的类。
    :param name: 神经网络的简称
    :return: 神经网络的类，还未构造。
    """
    return net_dict1[name]
