import json

out = {}

out["160"] = "数字图像在计算机中以矩阵形式表示。灰度图像是一个二维矩阵，每个元素对应一个像素的灰度值，取值一般在0到255之间；彩色图像则由红、绿、蓝三个通道的二维数组叠加而成。图像处理的本质就是对这些数值矩阵施加卷积、变换、阈值化等数学运算，从而达到图像增强、特征提取和信息分析的目的。冈萨雷斯等人的经典教材对空域与频域处理方法作了系统阐述[13]，阮秋琦[14]、章毓晋[15]的著作也为本课题提供了理论基础。"

out["161"] = "图像处理方法按处理目的和数学手段大体可分为空间域处理和频率域处理两类。空间域处理直接操作像素值，灰度变换、空域滤波、直方图处理均属此类；频域方法先通过傅里叶变换把图像映射到频率域，在频谱系数上滤波或加权后，再经逆变换回到空间域。形态学操作以集合论为根基，利用结构元素的膨胀、腐蚀等运算探测和修正几何形状；边缘检测则依据灰度一阶梯度极大值或二阶导数过零点标出亮度突变位置。本系统整合的34种算法即按上述处理范式组织成模块。"

out["162"] = "空间域滤波的数学基础是卷积。设图像为f、滤波核为w，二维卷积的做法是：将w在f上按步长逐位平移，每到一个位置便把核内权重与对应邻域像素相乘求和，结果作为输出图像该处的像素值。滤波核的取值直接决定滤波性质：高斯核服从二维高斯分布，中间大、四周小，适合平滑去噪；拉普拉斯核取值有正有负，常用于锐化和增强边缘。直方图统计各灰度级出现的频数，是直方图均衡化、Otsu阈值分割等算法的研究基础；梯度反映灰度变化的方向与快慢，一阶梯度算子（如Sobel）和二阶梯度算子（如Laplacian）构成边缘检测的两类基本方法。图1给出了数字图像矩阵表示与二维卷积运算的示意。"

out["166"] = "OpenCV（Open Source Computer Vision Library）是一套开源的计算机视觉与图像处理软件库，收录了数千个优化后的算法，图像读写、几何变换、滤波、特征检测、目标跟踪、机器学习等均包含在内。它支持C++、Python、Java等多种语言，跨平台能力良好；底层采用SIMD指令集优化和多线程并行计算，性能优势明显[16]。毛星云等[17]和李立宗[18]的教材也为本系统运用OpenCV提供了参考。"

out["167"] = "本系统把OpenCV作为核心算法引擎，主要基于三点考虑。其一，OpenCV算法覆盖全面，本系统所需的34种算法均有成熟的优化实现，无需重复开发；其二，其Python接口简洁，输入输出直接使用NumPy数组，与Streamlit对接时省去了额外的数据格式转换；其三，核心算法由C/C++实现并做了指令级优化，速度足以支撑实时交互。系统借助OpenCV完成了高斯滤波、中值滤波、双边滤波、直方图均衡化、Canny边缘检测、腐蚀膨胀、Otsu阈值分割、傅里叶变换等算法的核心功能。"

out["168"] = "[DELETE]"

out["170"] = "Streamlit是一个面向数据科学和机器学习领域的开源Python框架，内置控件丰富，滑块（slider）、下拉菜单（selectbox）、单选按钮（radio）、文件上传（file_uploader）、标签页（tabs）等一应俱全。它采用“脚本从上到下重新执行”的响应式模式：用户操作控件后，脚本便自动重跑一遍，界面随之刷新。"

out["171"] = "Streamlit的特性与本系统的需求高度契合。图像处理教学系统的核心交互就是“调节参数、观察结果”，而Streamlit的响应式执行方式天然支持这一点：用户一拖动参数滑块，脚本重新执行，算法模块拿新参数重新处理图像，预览随即更新。其会话状态（session_state）机制还可用来缓存处理结果、记录性能数据，为状态管理和性能优化带来了便利。"

out["172"] = "[DELETE]"

out["174"] = "Matplotlib是Python生态中使用最广泛的数据可视化库。本系统用它实现三类可视化：一是绘制灰度直方图及处理前后的直方图对比，算法对像素分布的影响一目了然；二是把算法的中间处理步骤排成图像网格展示，便于学生看清算法的内部过程；三是绘制伽马校正曲线、频率能量分布等数据曲线，把算法中的数学关系以图形方式呈现。"

out["176"] = "NumPy是Python科学计算的基础库，提供高性能的多维数组对象和丰富的数值运算函数。本系统中，图像在底层即以NumPy数组表示和传递，与OpenCV之间可以直接无缝转换。NumPy的向量化计算特性使批量像素操作无需显式循环，伽马校正中查找表的构建、傅里叶变换中幅度谱的计算等都借助NumPy完成。"

out["177"] = "[DELETE]"

out["179"] = "深度学习是机器学习的重要分支，依靠多层神经网络自动从数据中学习层次化的特征表示。图像处理领域最有代表性的模型是卷积神经网络（CNN），其核心思想是利用局部感受野和权值共享，通过卷积运算自动提取从低级边缘纹理到高级语义概念的层级特征。典型CNN由卷积层、池化层和全连接层堆叠而成：卷积层用可学习的卷积核提取局部特征；池化层做下采样，压缩特征图分辨率并增强平移不变性；全连接层把高层特征映射到最终输出类别。"

out["180"] = "深度学习框架方面，本系统选用PyTorch。PyTorch是基于动态计算图的开源深度学习库，张量运算、自动微分、GPU加速是它的三大核心能力；动态图机制使网络结构能在运行时灵活构建和调试，教学演示时可以实时观察前向传播过程。配套的torchvision库给出了MobileNetV2、DeepLabV3等经典网络的结构定义，并附带在ImageNet、COCO等大规模数据集上预训练好的权重参数。"

out["181"] = "本系统深度学习模块的设计建立在预训练模型与迁移学习之上。在ImageNet等大规模数据集上预训练过的网络已学到丰富的通用视觉特征，把它作为特征提取器迁移到新任务，即使样本很少效果也往往不错。具体来看，MobileNetV2是面向移动端的轻量级卷积网络，靠深度可分离卷积把参数量和计算量大幅压缩；DeepLabV3则用空洞卷积结合空间金字塔池化融合多尺度上下文信息，是语义分割领域的代表性网络。"

out["182"] = "有了上述技术打底，本系统搭建了深度学习算法模块，覆盖图像分类、语义分割、图像超分辨率和自定义图像分类四类任务，并配套实现了模型训练流水线。学生不仅能拿预训练模型做推理，还能亲手训练轻量级卷积网络，对深度学习的完整工作流程理解得也更全面。"

out["184"] = "本章围绕本系统涉及的相关技术与理论基础作了说明。首先介绍数字图像的矩阵表示方式和图像处理的主要范式，为后续算法实现打下基础；接着分别阐述OpenCV、Streamlit、Matplotlib和NumPy四个关键技术库的特点及其分工——OpenCV作为算法引擎承担核心计算，Streamlit负责交互界面构建，Matplotlib完成数据可视化，NumPy提供底层数组运算支持；最后介绍卷积神经网络和PyTorch框架的基本原理，为深度学习模块的设计与实现铺好理论道路。这些技术选型合理、分工明确，为系统的设计与实现奠定了技术基础。"

# Abstracts
out["50"] = "图像处理是计算机视觉与人工智能的基础技术，在医疗影像、工业检测、安防监控、自动驾驶等领域应用广泛。但传统图像处理课程多依托数学公式与静态图片讲解，算法原理抽象、处理过程无法直观展示，初学者理解难度大，如何把抽象算法转化为可交互、可视化的形式，成为图像处理教学中亟待解决的问题。"

out["51"] = "为此，本文设计并实现了一套基于OpenCV与Streamlit的图像处理算法交互式演示系统。系统采用Python开发，依托OpenCV实现图像处理算法，使用Streamlit搭建Web交互界面，并以Matplotlib完成可视化。平台集成滤波、图像增强、边缘检测、形态学操作、阈值分割、图像变换六大类共34种常用算法，另设深度学习模块覆盖四种任务，支持通过滑块、下拉框等组件实时调节参数并预览效果；针对重点算法提供中间过程可视化、直方图对比、频域分析等教学视图，配套算法原理、核心代码、参数说明与应用场景介绍。系统采用四层模块化架构，通过图像缩放、结果缓存等机制提升响应性能。测试表明，算法平均处理耗时约3ms，满足低于300ms的实时性指标，各模块运行稳定，可有效辅助图像处理课程教学与自主学习，具有实用价值。"

out["60"] = "Image processing is a fundamental technology in computer vision and artificial intelligence, widely used in medical imaging, industrial inspection, security monitoring and autonomous driving. Traditional courses rely on mathematical formulas and static images, making abstract algorithms hard for beginners to grasp; turning them into interactive, visual forms is an urgent teaching problem."

out["61"] = "To address this, this paper designs and implements an interactive demonstration system for image processing algorithms based on OpenCV and Streamlit. Developed in Python, the system implements algorithms with OpenCV, builds the web interface with Streamlit, and performs visualization with Matplotlib. The platform integrates 34 common algorithms in six categories, plus a deep learning module covering four tasks, and supports real-time parameter adjustment through sliders and dropdown boxes. For key algorithms, it provides teaching views such as intermediate-step visualization, histogram comparison and frequency-domain analysis, along with principles, core code and application scenarios. With a four-layer modular architecture, image scaling and result caching, the average processing time is about 3 ms, below the 300 ms real-time target; the system runs stably and effectively supports course teaching and self-directed learning."

ch2_keys = ["160","161","162","166","167","168","170","171","172","174","176","177","179","180","181","182","184"]
total = 0
for k in ch2_keys:
    v = out[k]
    if v == "[DELETE]":
        print(k, "DELETE")
    else:
        n = len(v)
        total += n
        flag = "" if 80 <= n <= 280 else "  <-- OUT OF RANGE"
        print(k, n, flag)
print("CH2 TOTAL:", total)
print("50 len:", len(out["50"]))
print("51 len:", len(out["51"]))
print("CN ABS TOTAL:", len(out["50"]) + len(out["51"]))
w60 = len(out["60"].split())
w61 = len(out["61"].split())
print("60 words:", w60, "61 words:", w61, "EN ABS TOTAL:", w60 + w61)

with open(r"d:\1\bishe\_out_C.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("written")
