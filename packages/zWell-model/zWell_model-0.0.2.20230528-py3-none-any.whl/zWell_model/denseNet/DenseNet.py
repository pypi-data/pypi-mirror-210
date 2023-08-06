# -*- coding: utf-8 -*-
# @Time : 2023/5/15 10:56
# @Author : zhao
# @Email : liming7887@qq.com
# @File : DenseNet.py
# @Project : ZWell-model
import copy

import zWell_model.utils as zu
from zWell_model.allModel import AllModel


class DenseNet(AllModel):
    """
    稠密神经网络对象，其通过稠密层与过渡层组合，共同实现提升网络深度与降低网络复杂度的目的。
    """

    def __init__(self, stride, input_shape, classes,
                 red=True,
                 reg=0.0001, bn_eps=2e-5,
                 bn_mom=0.9, model_layers_num=4,
                 ckp=2, init_k_len=64, dense_len=512
                 ):
        """
        构造出来一个残差神经网络对象
        :param stride: 每一个残差块的卷积步长 需要注意的是，这是一个list，作为每一个残差块的卷积步长。
        :param input_shape: 残差神经网络的输入维度元组
        :param classes: 残差神经网络的分类方式
        :param red: 是否使用单通道方式进行处理
        :param reg: 残差块中的L2正则化系数
        :param bn_eps: 用于避免批量归一化除以0
        :param bn_mom: 定义批量归一化操作时的动态均值的动量
        :param model_layers_num: 残差神经网络层数量
        :param ckp: 卷积层之间的卷积核数量等比数值
        :param init_k_len 第一层残差块中的卷积核数量
        :param dense_len 残差结束之后，全连接神经元第一层的神经元数量
        """
        super().__init__()

        # 检查步长 并 赋值步长
        zu.check_list_len(stride, model_layers_num, "Convolutional step size for each residual block:[stride]")
        self.stride = stride

        self.input_shape = input_shape
        self.classes = classes
        self.red = red
        self.reg = reg
        self.bn_eps = bn_eps
        self.bn_mom = bn_mom
        self.model_layers_num = model_layers_num
        self.ckp = ckp
        self.init_k_len = init_k_len
        self.dense_len = dense_len

    def __rshift__(self, other):
        other.stride = copy.copy(self.stride)
        other.input_shape = self.input_shape
        other.classes = self.classes
        other.red = self.red, other.reg = self.reg
        other.bn_eps = self.bn_eps
        other.bn_mom = self.bn_mom
        other.model_layers_num = other.model_layers_num
        other.ckp = self.ckp
        other.init_k_len = self.init_k_len
        other.dense_len = self.dense_len

    def __str__(self) -> str:
        return "zWell_model.denseNet.DenseNet.DenseNet(\n" \
               f"\tstride={self.stride}\n" \
               f"\tinput_shape={self.input_shape}\n" \
               f"\tclasses={self.classes}\n" \
               f"\tred={self.red}\n" \
               f"\treg={self.reg}\n" \
               f"\tbn_eps={self.bn_eps}\n" \
               f"\tbn_mom={self.bn_mom}\n" \
               f"\tmodel_layers_num={self.model_layers_num}\n" \
               f"\tckp={self.ckp}\n" \
               f"\tinit_k_len={self.init_k_len}\n" \
               f"\tdense_len={self.dense_len}\n" \
               ")"
