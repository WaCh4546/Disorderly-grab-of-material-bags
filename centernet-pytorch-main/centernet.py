import colorsys
import os
import time
from torch import nn

import numpy as np
import torch
import torch.backends.cudnn as cudnn
from PIL import ImageDraw, ImageFont

from nets.centernet import CenterNet_HourglassNet, CenterNet_Resnet50
from utils.utils import cvtColor, get_classes, preprocess_input, resize_image
from utils.utils_bbox import decode_bbox, postprocess


#--------------------------------------------#
#   使用自己训练好的模型预测需要修改3个参数
#   model_path、classes_path和backbone
#   都需要修改！
#   如果出现shape不匹配，一定要注意
#   训练时的model_path和classes_path参数的修改
#--------------------------------------------#
class CenterNet(nn.Module):
    _defaults = {
        #--------------------------------------------------------------------------#
        #   使用自己训练好的模型进行预测一定要修改model_path和classes_path！
        #   model_path指向logs文件夹下的权值文件，classes_path指向model_data下的txt
        #
        #   训练好后logs文件夹下存在多个权值文件，选择验证集损失较低的即可。
        #   验证集损失较低不代表mAP较高，仅代表该权值在验证集上泛化性能较好。
        #   如果出现shape不匹配，同时要注意训练时的model_path和classes_path参数的修改
        #--------------------------------------------------------------------------#
        # "model_path"        : 'model_data/centernet_resnet50_voc.pth',
        "model_path": 'logs/2022_0706final_net.pth',
        # "classes_path"      : 'model_data/voc_classes.txt',
        "classes_path": 'model_data/cls_classes.txt',
        #--------------------------------------------------------------------------#
        #   用于选择所使用的模型的主干
        #   resnet50, hourglass
        #--------------------------------------------------------------------------#
        "backbone"          : 'resnet50',
        #--------------------------------------------------------------------------#
        #   输入图片的大小，设置成32的倍数
        #--------------------------------------------------------------------------#
        "input_shape"       : [512, 512],
        #--------------------------------------------------------------------------#
        #   只有得分大于置信度的预测框会被保留下来
        #--------------------------------------------------------------------------#
        "confidence"        : 0.3,
        #---------------------------------------------------------------------#
        #   非极大抑制所用到的nms_iou大小
        #---------------------------------------------------------------------#
        "nms_iou"           : 0.3,
        #--------------------------------------------------------------------------#
        #   是否进行非极大抑制，可以根据检测效果自行选择
        #   backbone为resnet50时建议设置为True、backbone为hourglass时建议设置为False
        #--------------------------------------------------------------------------#
        "nms"               : True,
        #---------------------------------------------------------------------#
        #   该变量用于控制是否使用letterbox_image对输入图像进行不失真的resize，
        #   在多次测试后，发现关闭letterbox_image直接resize的效果更好
        #---------------------------------------------------------------------#
        "letterbox_image"   : False,
        #-------------------------------#
        #   是否使用Cuda
        #   没有GPU可以设置成False
        #-------------------------------#
        "cuda"              : False
    }

    # cls在python中表示类本身,经测试：该函数可以不写
    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    #---------------------------------------------------#
    #   初始化centernet
    #---------------------------------------------------#
    def __init__(self, **kwargs):
        super(CenterNet, self).__init__()
        self.__dict__.update(self._defaults)  # 自动实例化属性
        for name, value in kwargs.items():
            setattr(self, name, value)
        #---------------------------------------------------#
        #   计算总的类的数量
        #---------------------------------------------------#
        self.class_names, self.num_classes  = get_classes(self.classes_path)

        #---------------------------------------------------#
        #   不同类别的目标画框设置不同的颜色，放在一个列表中
        #---------------------------------------------------#
        hsv_tuples = [(x / self.num_classes, 1., 1.) for x in range(self.num_classes)]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), self.colors))

        self.generate()

    #---------------------------------------------------#
    #   载入模型
    #---------------------------------------------------#
    def generate(self):
        #-----------------------------------------------------------------------------------------#
        #   载入模型与权值,如果self.backbone为['resnet50', 'hourglass']中的元素，则继续执行，否则触发异常
        #-----------------------------------------------------------------------------------------#
        assert self.backbone in ['resnet50', 'hourglass']
        if self.backbone == "resnet50":
            self.net = CenterNet_Resnet50(num_classes=self.num_classes, pretrained=False)
        else:
            self.net = CenterNet_HourglassNet({'hm': self.num_classes, 'wh': 2, 'reg':2})

        device      = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.net.load_state_dict(torch.load(self.model_path, map_location=device),False)
        self.net    = self.net.eval()
        print('{} model, and classes loaded.'.format(self.model_path))

        # 如果电脑上有cuda，则启用多GPU训练，并将网络模型从cpu转移到gpu
        if self.cuda:
            self.net = torch.nn.DataParallel(self.net)
            cudnn.benchmark = True
            self.net = self.net.cuda()

    #---------------------------------------------------#
    #   检测图片
    #---------------------------------------------------#
    def detect_image(self, image):
        #---------------------------------------------------#
        #   计算输入图片的高和宽
        #---------------------------------------------------#
        image_shape = np.array(np.shape(image)[0:2])
        #---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        #---------------------------------------------------------#
        image       = cvtColor(image)
        # print((np.array(image)).shape)
        #---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        #---------------------------------------------------------#
        image_data  = resize_image(image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image)

        #-----------------------------------------------------------#
        #   图片预处理，归一化。获得的photo的shape为[1, 512, 512, 3]
        #-----------------------------------------------------------#
        image_data = np.expand_dims(np.transpose(preprocess_input(np.array(image_data, dtype='float32')), (2, 0, 1)), 0)

        with torch.no_grad():
            images = torch.from_numpy(np.asarray(image_data)).type(torch.FloatTensor)
            if self.cuda:
                images = images.cuda()
            #---------------------------------------------------------#
            #   将图像输入网络当中进行预测！
            #---------------------------------------------------------#
            outputs = self.net(images)
            if self.backbone == 'hourglass':
                outputs = [outputs[-1]["hm"].sigmoid(), outputs[-1]["wh"], outputs[-1]["reg"]]
            #-----------------------------------------------------------#
            #   利用预测结果进行解码
            #-----------------------------------------------------------#
            # outputs = decode_bbox(outputs[0], outputs[1], outputs[2], self.confidence, self.cuda)
            outputs = decode_bbox(outputs[0], outputs[1], outputs[2], outputs[3], self.confidence, self.cuda)
            #-----------------------------------------------------------------------------------------------------------#
            #   对于centernet网络来讲，确立中心非常重要。
            #   对于大目标而言，会存在许多的局部信息。
            #   此时对于同一个大目标，中心点比较难以确定。
            #   使用最大池化的非极大抑制方法无法去除局部框
            #   所以我还是写了另外一段对框进行非极大抑制的代码
            #   实际测试中，hourglass为主干网络时有无额外的nms相差不大，resnet相差较大。
            #   开始进行了resize操作，在postprocess当中还包括了如何通过当前图片的长宽中心点信息展会到原图的长宽中心点信息
            #------------------------------------------------------------------------------------------------------------#
            results = postprocess(outputs, self.nms, image_shape, self.input_shape, self.letterbox_image, self.nms_iou)
            
            #--------------------------------------#
            #   如果没有检测到物体，则返回原图
            #--------------------------------------#
            if results[0] is None:
                return image

            top_label   = np.array(results[0][:, 6], dtype = 'int32')
            top_conf    = results[0][:, 5]
            angle       = results[0][:, 4]
            top_boxes   = results[0][:, :4]
        #---------------------------------------------------------#
        #   设置字体与边框厚度
        #---------------------------------------------------------#
        font = ImageFont.truetype(font='model_data/simhei.ttf', size=np.floor(3e-2 * np.shape(image)[1] + 0.5).astype('int32'))
        thickness = max((np.shape(image)[0] + np.shape(image)[1]) // self.input_shape[0], 1)

        #---------------------------------------------------------#
        #   图像绘制
        #---------------------------------------------------------#
        for i, c in list(enumerate(top_label)):
            predicted_class = self.class_names[int(c)]
            box = top_boxes[i]
            score = top_conf[i]
            angle_ = angle[i]

            top, left, bottom, right = box

            top = max(0, np.floor(top).astype('int32'))
            left = max(0, np.floor(left).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom).astype('int32'))
            right = min(image.size[0], np.floor(right).astype('int32'))

            label = '{} {:.2f} {:.2f}'.format(predicted_class, score, angle_)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)
            label = label.encode('utf-8')
            print(label, top, left, bottom, right)

            center_x = int((right - left) / 2) + left
            center_y = int((bottom - top) / 2) + top
            shape = [(center_x - 10, center_y), (center_x + 10, center_y)]
            draw.line(shape, fill="red", width=2)
            shape = [(center_x, center_y - 10), (center_x, center_y + 10)]
            draw.line(shape, fill="red", width=2)

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):
                draw.rectangle([left + i, top + i, right - i, bottom - i], outline=self.colors[c])

            draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)], fill=self.colors[c])
            draw.text(text_origin, str(label, 'UTF-8'), fill=(0, 0, 0), font=font)
            del draw

        return image

    def get_FPS(self, image, test_interval):
        #---------------------------------------------------#
        #   计算输入图片的高和宽
        #---------------------------------------------------#
        image_shape = np.array(np.shape(image)[0:2])
        #---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        #---------------------------------------------------------#
        image       = cvtColor(image)
        #---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        #---------------------------------------------------------#
        image_data  = resize_image(image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image)
        #-----------------------------------------------------------#
        #   图片预处理，归一化。获得的photo的shape为[1, 512, 512, 3]
        #   添加上batch_size维度
        #-----------------------------------------------------------#
        image_data = np.expand_dims(np.transpose(preprocess_input(np.array(image_data, dtype='float32')), (2, 0, 1)), 0)

        with torch.no_grad():
            images = torch.from_numpy(np.asarray(image_data)).type(torch.FloatTensor)
            if self.cuda:
                images = images.cuda()
            #---------------------------------------------------------#
            #   将图像输入网络当中进行预测！
            #---------------------------------------------------------#
            outputs = self.net(images)
            if self.backbone == 'hourglass':
                outputs = [outputs[-1]["hm"].sigmoid(), outputs[-1]["wh"], outputs[-1]["reg"]]
            #-----------------------------------------------------------#
            #   利用预测结果进行解码
            #-----------------------------------------------------------#
            # outputs = decode_bbox(outputs[0], outputs[1], outputs[2], self.confidence, self.cuda)
            outputs = decode_bbox(outputs[0], outputs[1], outputs[2], outputs[3], self.confidence, self.cuda)
            results = postprocess(outputs, self.nms, image_shape, self.input_shape, self.letterbox_image, self.nms_iou)
            
        t1 = time.time()
        for _ in range(test_interval):
            with torch.no_grad():
                #---------------------------------------------------------#
                #   将图像输入网络当中进行预测！
                #---------------------------------------------------------#
                outputs = self.net(images)
                if self.backbone == 'hourglass':
                    outputs = [outputs[-1]["hm"].sigmoid(), outputs[-1]["wh"], outputs[-1]["reg"]]
                #-----------------------------------------------------------#
                #   利用预测结果进行解码
                #-----------------------------------------------------------#
                # outputs = decode_bbox(outputs[0], outputs[1], outputs[2], self.confidence, self.cuda)
                outputs = decode_bbox(outputs[0], outputs[1], outputs[2], outputs[3], self.confidence, self.cuda)
                results = postprocess(outputs, self.nms, image_shape, self.input_shape, self.letterbox_image, self.nms_iou)
        t2 = time.time()
        tact_time = (t2 - t1) / test_interval
        return tact_time

    def get_map_txt(self, image_id, image, class_names, map_out_path):
        f = open(os.path.join(map_out_path, "detection-results/"+image_id+".txt"),"w") 
        #---------------------------------------------------#
        #   计算输入图片的高和宽
        #---------------------------------------------------#
        image_shape = np.array(np.shape(image)[0:2])
        #---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        #---------------------------------------------------------#
        image       = cvtColor(image)
        #---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        #---------------------------------------------------------#
        image_data  = resize_image(image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image)
        #-----------------------------------------------------------#
        #   图片预处理，归一化。获得的photo的shape为[1, 512, 512, 3]
        #-----------------------------------------------------------#
        image_data = np.expand_dims(np.transpose(preprocess_input(np.array(image_data, dtype='float32')), (2, 0, 1)), 0)

        with torch.no_grad():
            images = torch.from_numpy(np.asarray(image_data)).type(torch.FloatTensor)
            if self.cuda:
                images = images.cuda()
            #---------------------------------------------------------#
            #   将图像输入网络当中进行预测！
            #---------------------------------------------------------#
            outputs = self.net(images)
            if self.backbone == 'hourglass':
                outputs = [outputs[-1]["hm"].sigmoid(), outputs[-1]["wh"], outputs[-1]["reg"]]
            #-----------------------------------------------------------#
            #   利用预测结果进行解码
            #-----------------------------------------------------------#
            outputs = decode_bbox(outputs[0], outputs[1], outputs[2], self.confidence, self.cuda)

            #-------------------------------------------------------#
            #   对于centernet网络来讲，确立中心非常重要。
            #   对于大目标而言，会存在许多的局部信息。
            #   此时对于同一个大目标，中心点比较难以确定。
            #   使用最大池化的非极大抑制方法无法去除局部框
            #   所以我还是写了另外一段对框进行非极大抑制的代码
            #   实际测试中，hourglass为主干网络时有无额外的nms相差不大，resnet相差较大。
            #-------------------------------------------------------#
            results = postprocess(outputs, self.nms, image_shape, self.input_shape, self.letterbox_image, self.nms_iou)
            
            #--------------------------------------#
            #   如果没有检测到物体，则返回原图
            #--------------------------------------#
            if results[0] is None:
                return 

            top_label   = np.array(results[0][:, 5], dtype = 'int32')
            top_conf    = results[0][:, 4]
            top_boxes   = results[0][:, :4]


        for i, c in list(enumerate(top_label)):
            predicted_class = self.class_names[int(c)]
            box             = top_boxes[i]
            score           = str(top_conf[i])

            top, left, bottom, right = box

            if predicted_class not in class_names:
                continue

            f.write("%s %s %s %s %s %s\n" % (predicted_class, score[:6], str(int(left)), str(int(top)), str(int(right)),str(int(bottom))))

        f.close()
        return 
