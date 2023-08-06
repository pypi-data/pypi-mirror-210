# -*- coding: utf-8 -*-
# @Time : 2023/5/13 20:18
# @Author : zhao
# @Email : liming7887@qq.com
# @File : allModel.py
# @Project : Keras-model


class AllModel:

    def to_keras_model(self, add_fully_connected=True, **args):
        """
        :param add_fully_connected 布尔数值 如果设置为true 代表要添加全连接神经网络部分，如果为False 代表不添加全连接，只添加最基本的架构，暑促部分由外部实现。
        :param args: 获取到模型需要使用的参数数值。
        :return: keras 中的模型对象
        """
        pass

    def __lshift__(self, other):
        """
        左移运算符赋值操作
        :param other: 被赋值的变量 当此变量属于keras库的时候，将会返回一个keras的模型。
        :return: 赋值之后的数值
        """
        from keras import Model
        from keras import Sequential
        t = type(other)
        if t == Model or t == Sequential:
            return self.to_keras_model()
        else:
            return self

    def __rshift__(self, other):
        """
        配置项拷贝
        :param other:已经实例化出来的模型对象
        :return: 根据实例化模型拷贝之后的新模型对象
        """
        pass
