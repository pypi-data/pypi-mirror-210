# -*- coding: utf-8 -*-
# @Time : 2023/5/15 11:47
# @Author : zhao
# @Email : liming7887@qq.com
# @File : utils.py
# @Project : ZWell-model


def add_keras_transition(model, filters, k_size=2, strides=2):
    """
    向模型中添加一个 keras的平均池化层
    :param model: 需要杯添加层的模型
    :param filters: 卷积核数量
    :param k_size: 当前过滤层中的卷积核数量
    :param strides 当前过滤层中的卷积步长
    """
    from keras.layers import BatchNormalization, Conv2D, AveragePooling2D
    model.add(BatchNormalization())
    model.add(Conv2D(filters=filters, kernel_size=k_size, strides=strides))
    model.add(AveragePooling2D(pool_size=2))
