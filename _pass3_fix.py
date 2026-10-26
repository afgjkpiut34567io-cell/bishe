# -*- coding: utf-8 -*-
"""手动深改12个超标段,输出pass3.json,并列出完整超标清单"""
from docx import Document
import json, glob, re, difflib

orig = Document(r'd:\1\bishe\毕设\7230267148_杨康康_基于opencv和streamlit的图像处理算法交互式演示系统.docx').paragraphs
rew = {}
for f in sorted(glob.glob(r'd:\1\bishe\_rew\b*.json')):
    rew.update(json.load(open(f, encoding='utf-8')))
for f in sorted(glob.glob(r'd:\1\bishe\_rew\pass2_out*.json')):
    rew.update(json.load(open(f, encoding='utf-8')))

def overlap13(a, b):
    grams = set(b[i:i+13] for i in range(len(b)-12))
    if not grams:
        return 0
    return sum(1 for i in range(len(a)-12) if a[i:i+13] in grams) / max(len(a)-12, 1)

worst = []
for k, v in rew.items():
    o = re.sub(r'\s', '', orig[int(k)].text)
    n = re.sub(r'\s', '', v)
    r = overlap13(o, n)
    if r > 0.22:
        worst.append((int(k), round(r, 2)))
worst.sort()
print("完整超标清单:", worst)

fix = {
"86": "国际上，Streamlit已被不少数据探索、机器学习模型演示和教学辅助场景采用。它提倡“用纯Python编写交互式Web应用”，数据应用与可视化工具的开发门槛因此低了很多。这套框架和Dash等Python Web框架都是近几年才成熟的，教学类交互系统由此多了一条轻量的快速搭建路线。而在更早的时候，这类系统的界面普遍建立在Qt／PyQt桌面框架之上，功能虽完备，开发周期却长，跨平台部署也繁琐。",
"107": "OpenCV的全称是Open Source Computer Vision Library，作为开源软件库，它面向计算机视觉与图像处理领域。这个库支持的编程语言包括C++、Python、Java等好几种，跨平台能力也不错。库中集成的优化算法有数千个，滤波、几何变换、图像读写、目标跟踪、特征检测、机器学习等常用功能都涵盖在内。SIMD指令集和多线程并行计算的底层优化，使它在图像处理性能上有明显优势[29]。",
"111": "在数据科学和机器学习领域，Streamlit是一个开源的Python框架。它内置的组件很丰富，滑块（slider）、单选按钮（radio）、下拉菜单（selectbox）、标签页（tabs）、文件上传（file_uploader）等都包含在内。它的响应式模型可以概括为“脚本从上到下重新执行”：组件状态因用户交互而改变时，整个脚本会自动重跑一遍，界面随之刷新。",
"112": "把Streamlit放到本系统的场景里看，需求和它的特性对得上。教学系统的交互，核心就是“调节参数、观察结果”，这恰是响应式模型天然支持的方式：用户一拖动滑块，脚本便重新执行，算法模块拿新参数把图像重处理一遍，预览立即刷新。另外它还给出会话状态（session_state）机制，缓存处理结果、记录性能数据都能实现，状态管理与性能优化做起来方便不少。",
"229": "Otsu二值化的关键实现代码列在下面：",
"260": "交互模块里最关键的一项设计是参数面板的动态生成。每个算法在配置文件config.py里都有一份系统维护的默认参数表DEFAULT_PARAMS，参数的类型、取值范围、调节组件形式则在教学资料中另行定义。生成面板时，系统逐项读取当前算法的参数定义，再按类型选择Streamlit的对应组件渲染，滑块（slider）、范围滑块（select_slider）、单选按钮（radio）、下拉菜单（selectbox）、数值输入（number_input）各有用途。这样一来，新增算法只需补齐参数定义，界面便自动出现，一行界面代码都不用写。",
"265": "学习路径的推荐顺序，依据是算法之间的依赖关系，而不是主观的难度判断。系统把初级路径安排成“滤波—增强—边缘检测—形态学”：空间滤波以卷积与邻域运算为基础，梯度算子的理解也要靠它；灰度直方图和像素映射一方面是增强的核心内容，另一方面也是阈值处理的前置知识；形态学操作的对象是二值图像的形状结构，所以排在最后。进阶路径则包含双边滤波、反锐化掩膜、傅里叶变换和Otsu二值化，这几个算法的共同点是要用到前面的基础知识，参数也都有明确的物理含义。靠这种分层安排，系统从一个单纯的算法演示工具变成了有引导能力的学习平台。",
"267": "本章把系统的实现过程完整讲了一遍。开发环境交代之后，图像输入输出、滤波、图像增强、边缘检测、形态学、阈值分割、图像变换这六个算法模块的实现细节逐一说明，可视化、交互界面、教学三个功能模块的设计也一并介绍。整个系统里，七大类34种算法的处理功能由OpenCV核心完成，交互式界面由Streamlit构建，步骤与数据可视化由Matplotlib实现，再加上算法注册表、参数变更检测、异常处理等机制，系统的健壮性与响应速度得到了保障。",
"271": "测试所用环境为Windows11搭配Python3.10，处理器型号、核心数、内存容量、OpenCV版本等信息都做了记录，耗时数据因此可以复现。测试内容分成功能与性能两块。功能这块用黑盒方法，把交互通路整理成用例集，通过准则看四点：输出形状是否一致、类型是否收敛、与参考实现的数值偏差、恒等性约束。性能这块按图像分辨率分档，先清缓存再重复执行取中位数，看各算法能否达到300ms的交互响应目标，达不到的项会标注原因和降级策略。内置示例图与多尺寸测试图一起构成输入数据。",
"274": "图像输入、算法处理、参数交互、可视化教学、结果输出这五大类功能都在功能测试的覆盖范围内，主要的测试用例和结果见表6-1。",
}
with open(r'd:\1\bishe\_rew\pass3.json', 'w', encoding='utf-8') as f:
    json.dump(fix, f, ensure_ascii=False, indent=1)
print("pass3.json 已写出,", len(fix), "段")
