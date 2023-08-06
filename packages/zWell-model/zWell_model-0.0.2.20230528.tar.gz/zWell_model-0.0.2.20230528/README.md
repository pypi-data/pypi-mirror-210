# ![image](https://github.com/BeardedManZhao/ZWell-model/assets/113756063/87aedd4f-092f-4ff7-9e4a-3749cffedf0d) ZWell-model

# introduce

A deep learning model library that supports various deep network models and transformations to libraries such as Keras.
With this tool, it is easy to construct neural network objects that can be used for any API, saving additional API
learning time.

## Acquisition method

通过 pip 工具进行库的安装，也可以通过GitHub中的源码手动装载。

```shell
pip install zWell-model
```

## Current developments

这里展示的是当前 zWell-model 支持的深度学习模型，以及其支持接入的第三方库等更详细的情况。

| Neural Network Name                   | by reference           | Support access to keras | Supported version |
|---------------------------------------|------------------------|-------------------------|-------------------|
| Basic Convolutional First Edition     | zWell_model.ConvNetV1  | yes                     | v0.0.1.20230514   |
| Basic Convolutional Second Edition    | zWell_model.ConvNetV2  | yes                     | v0.0.1.20230514   |
| Residual Neural Network First Edition | zWell_model.ResNetV1   | yes                     | v0.0.1.20230514   |
| Dense Neural Network First Edition    | zWell_model.DenseNetV1 | yes                     | v0.0.2.20230528   |

# Usage examples

There are many neural network implementations in this library that support conversion to various library model objects.
The following are relevant examples.

## Basic Convolutional Neural Networks

The basic convolutional neural network contains the most basic network structure, which compromises learning speed and
accuracy, and has two versions in total.

### first edition

A convolutional neural network with learning speed as its main core can improve learning speed for a large amount of
data with almost identical features.

```python
import zWell_model

# Obtaining the first type of convolutional neural network
resNet = zWell_model.ConvNetV1(
    # The number of additional convolutional layers to be added above the specified infrastructure is 4. TODO defaults to 1
    model_layers_num=4,
    # Specify the step size in the four convolutional layers
    stride=[1, 2, 1, 2],
    # Specify the input dimension of convolutional neural networks
    input_shape=(None, 32, 32, 3),
    # Specify classification quantity
    classes=10
)
```

### Second Edition

The convolutional neural network, whose core is learning speed and preventing overfitting, can improve learning speed
and model accuracy for a large number of data with diversified features.

```python
import zWell_model

# Obtaining the second type of convolutional neural network
resNet = zWell_model.ConvNetV2(
    # The number of additional convolutional layers to be added above the specified infrastructure is 1. TODO defaults to 1
    model_layers_num=1,
    # Specify the step size in the one convolutional layers
    stride=[1],
    # Specify the input dimension of convolutional neural networks
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)
```

### Example of using basic convolutional neural networks

What is displayed here is the operation of converting the basic convolutional neural network series into models in Keras
and calling them.

```python
# This is an example Python script.
import numpy as np
from keras.datasets import cifar10
from keras.optimizers import Adam
from livelossplot import PlotLossesKeras

import zWell_model

# Obtaining a dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
# Data standardization and dimension expansion
x_train = x_train.astype(np.float32).reshape(-1, 32, 32, 3) / 255.
x_test = x_test.astype(np.float32).reshape(-1, 32, 32, 3) / 255.

# Obtaining the second type of convolutional neural network
resNet = zWell_model.ConvNetV2(
    # The number of additional convolutional layers to be added above the specified infrastructure is 1. TODO defaults to 1
    model_layers_num=1,
    # Specify the step size in the one convolutional layers
    stride=[1],
    # Specify the input dimension of convolutional neural networks
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)

# Converting to the network model of Keras
model = resNet.to_keras_model()
model.summary()

# Start building the model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['acc']
)

# Start training the model
model.fit(
    x=x_train, y=y_train,
    validation_data=(x_test, y_test),
    batch_size=32, epochs=30,
    callbacks=[PlotLossesKeras()],
    verbose=1
)
```

## Residual neural network

You can obtain the general object of the residual neural network object from ZWell model in the following way.

```python
import zWell_model

# Obtaining residual neural network
resNet = zWell_model.ResNetV1(
    # Specify the number of residual blocks as 4 TODO defaults to 4
    model_layers_num=4,
    # Specify the number of output channels in the four residual blocks
    k=[12, 12, 12, 12],
    # Specify the step size in the four residual blocks
    stride=[1, 2, 1, 2],
    # Specify the input dimension of the residual neural network
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)
```

Directly convert the obtained residual neural network object into a neural network model object in Keras, enabling it to
be supported by Keras.

```python
# This is an example Python script.
import numpy as np
from keras.datasets import cifar10
from keras.optimizers import Adam
from livelossplot import PlotLossesKeras

import zWell_model

# Obtaining a dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
# data standardization
x_train, x_test = x_train.astype(np.float32) / 255., x_test.astype(np.float32) / 255.

# Obtaining residual neural network
resNet = zWell_model.ResNetV1(
    # Specify the number of residual blocks as 4 TODO defaults to 4
    model_layers_num=4,
    # Specify the number of output channels in the four residual blocks
    k=[12, 12, 12, 12],
    # Specify the step size in the four residual blocks
    stride=[1, 2, 1, 2],
    # Specify the input dimension of the residual neural network
    input_shape=(32, 32, 3),
    # Specify classification quantity
    classes=10
)

# Converting to the network model of Keras
model = resNet.to_keras_model()
model.summary()

# Start building the model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['acc']
)

# Start training the model
model.fit(
    x=x_train, y=y_train,
    validation_data=(x_test, y_test),
    batch_size=32, epochs=30,
    callbacks=[PlotLossesKeras()],
    verbose=1
)
```

## 稠密神经网络

You can obtain dense neural network models from the ZWell mode library in the following way.

```python
import zWell_model

# Obtaining dense neural networks
resNet = zWell_model.dense_net1.DenseNetV1(
    # Specify the number of dense blocks as 3 TODO defaults to 4
    model_layers_num=3,
    # Specify the convolution step size in the transition layer after 2 dense blocks
    stride=[1, 1, 1],
    # Specify the input dimension of a dense neural network
    input_shape=(32, 32, 3),
    #     # Specify classification quantity
    classes=10
)
```

Convert the obtained dense neural network object into a deep neural network object in the Keras library.

```python
# This is an example Python script.
import numpy as np
from keras.datasets import cifar10
from keras.optimizers import Adam
from livelossplot import PlotLossesKeras

import zWell_model

# Obtaining a dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
# data standardization
x_train, x_test = x_train.astype(np.float32) / 255., x_test.astype(np.float32) / 255.

# Obtaining dense neural networks
resNet = zWell_model.dense_net1.DenseNetV1(
    # Specify the number of dense blocks as 3 TODO defaults to 4
    model_layers_num=3,
    # Specify the convolution step size in the transition layer after 2 dense blocks
    stride=[1, 1, 1],
    # Specify the input dimension of a dense neural network
    input_shape=(32, 32, 3),
    #     # Specify classification quantity
    classes=10
)

print(resNet)

# Converting to the network model of Keras
model = resNet.to_keras_model()
model.summary()

# Start building the model
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['acc']
)

# Start training the model
model.fit(
    x=x_train, y=y_train,
    validation_data=(x_test, y_test),
    batch_size=32, epochs=30,
    callbacks=[PlotLossesKeras()],
    verbose=1
)
```

<hr>

## More Actions

### Using abbreviations to obtain neural networks

Starting from version 0.0.2, we can use model aliases to obtain model classes, which are beneficial for simple model
instantiation and reduce code load. Different model abbreviations and instantiation operations are shown below.

| Original name of the model | Model abbreviation |
|----------------------------|--------------------|
| ConvNetV1                  | Cnn1               |
| ConvNetV2                  | Cnn2               |
| ResNetV1                   | RCnn1              |
| DenseNetV1                 | Dn1                |

```python
# This is an example Python script.
import zWell_model as zModel
from zWell_model.allModel import AllModel

# Here, the model object of ConvNetV1 was obtained through abbreviation 
# TODO Cnn1 is an abbreviation
z_model: AllModel = zModel.Cnn1(
    # The number of additional convolutional layers to be added above the specified infrastructure is 4. TODO defaults to 1
    model_layers_num=4,
    # Specify the step size in the four convolutional layers
    stride=[1, 2, 1, 2],
    # Specify the input dimension of convolutional neural networks
    input_shape=(None, 32, 32, 3),
    # Specify classification quantity
    classes=10
)
print(z_model)
print(z_model.to_keras_model())

```
