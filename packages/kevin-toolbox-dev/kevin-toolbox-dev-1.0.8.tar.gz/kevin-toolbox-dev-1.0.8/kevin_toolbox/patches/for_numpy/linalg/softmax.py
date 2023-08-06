import numpy as np


def softmax(v, axis=-1):
    # 为了数值稳定，减去最大值
    v = v - np.max(v)
    return np.exp(v) / np.sum(np.exp(v), axis=axis, keepdims=True)


if __name__ == '__main__':
    print(softmax(np.asarray([0, 0.1]) * 10))
