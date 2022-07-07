import numpy as np
import torch



yv, xv = np.meshgrid(np.arange(0, 10), np.arange(0, 10))
# -------------------------------------------------------------------------#
#   xv              128*128,    特征点的x轴坐标
#   yv              128*128,    特征点的y轴坐标
#   flatten()       返回一个折叠为一维的array
# -------------------------------------------------------------------------#
xv, yv = xv.flatten(), yv.flatten()
print(xv)
print(yv)

b = np.array([1,2,3])
s,e,f = b
print(s)
print(e)