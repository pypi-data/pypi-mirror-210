# -*- coding: utf-8 -*-
# @Time : 2023/5/15 11:16
# @Author : zhao
# @Email : liming7887@qq.com
# @File : DenseNetV1.py
# @Project : ZWell-model
from keras.layers import Flatten, Dropout

from zWell_model.denseNet import utils
from zWell_model.denseNet.DenseNet import DenseNet


class DenseNetV1(DenseNet):

    def to_keras_model(self, add_fully_connected=True, **args):
        from keras.models import Sequential
        from keras.layers import Dense, Conv2D
        k_len = self.init_k_len

        # 定义模型
        model = Sequential()
        # 添加第一个卷积
        model.add(Conv2D(k_len, (3, 3), strides=(1, 1), padding='same', input_shape=self.input_shape))
        # 添加剩余的稠密块
        if self.ckp == 2:
            for index in range(self.model_layers_num):
                k_len <<= 1
                model.add(Dense(k_len, activation='relu'))
                # 添加过渡
                utils.add_keras_transition(model, filters=k_len, k_size=1, strides=self.stride[index])
        else:
            for index in range(self.model_layers_num):
                k_len *= self.ckp
                model.add(Dense(k_len, activation='relu'))
                # 添加过渡
                utils.add_keras_transition(model, filters=k_len, k_size=1, strides=self.stride[index])

        if add_fully_connected:
            # 准备输出 添加输出层
            model.add(Flatten())
            model.add(Dropout(0.5))
            model.add(Dense(self.dense_len, activation='relu'))
            model.add(Dense(self.classes, activation='softmax'))
        # 返回模型
        return model
