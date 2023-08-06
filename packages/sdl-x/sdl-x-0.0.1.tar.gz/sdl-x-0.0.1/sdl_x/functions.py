def getConvolutinSize(h, w, fh, fw, p, s):
    """
    对于填充和步 幅，如何计算输出大小
    :param h: 输入大小为 (H, W)
    :param w:
    :param fh: 滤波器大小为 (FH, FW)
    :param fw:
    :param p: 填充为 P
    :param s: 步幅为 S
    :return: 输出大小
    """
    oh = (h + 2 * p -fh) / s + 1
    oh = (w + 2 * p -fw) / s + 1
