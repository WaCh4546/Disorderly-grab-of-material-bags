# Disorderly-grab-of-material-bags
基于双目视觉和工业机器人的物料袋无序抓取

油田钻井时，需要添加钻井液帮助施工，钻井液是钻井的血液，又称钻孔冲洗液。其中含有各种助于钻井施工的成分，如清水、泥浆、无粘土相冲洗液、乳状液、泡沫和压缩空气等。本项目的内容就是基于双目视觉与工业机器人设计一套无序抓取系统，用于油田钻井时向钻孔中添加钻井液原料如钻井液用抗高温抗盐增加粘降滤失剂等等。料袋码放在固定区域，当生产机器钻孔施工时机器人自动选择合适的抓取对象，进行抓料、拆袋、加料等操作。以下是实验室搭建的方案验证环境
![抓料.png](https://github.com/WaCh4546/Disorderly-grab-of-material-bags/blob/main/%E6%8A%93%E6%96%99.png?raw=true)
在本项目内需要解决的问题有以下几点：

①设计基于双目视觉和深度学习的料袋识别定位算法，用以定位料袋的空间位置。

②设计料袋抓取策略，使得机器人可以在一系列候选料袋中，选择最合适的抓取对象，使抓取不会受到临近料袋干扰，不会造成料袋倾塌等问题。

③设计机器人抓取料袋控制程序。

④设计人机交互、安全监测相关程序。



「标注软件」https://www.aliyundrive.com/s/gJAYCSMWdfV 提取码: zm83