# 创空间使用指南

## 入口

https://modelscope.cn/studios

## 免费部署

| 资源 | 免费条件 |
|------|---------|
| CPU | 完全免费，无需条件 |
| GPU | 需"应用搭子 LV2"勋章 |

## 支持框架

- Gradio
- Streamlit
- 自定义 Web 应用

## 创建流程

1. 打开 https://modelscope.cn/studios
2. 点击"创建创空间"
3. 选择框架（Gradio/Streamlit）
4. 编写代码或从模板开始
5. 部署 → 获得公开 URL

## 典型示例

### Gradio 图像分类 Demo

```python
import gradio as gr
from modelscope.pipelines import pipeline

pipe = pipeline('image-classification', model='damo/cv_resnet50_image-classification')

def classify(image):
    result = pipe(image)
    return {r['label']: r['score'] for r in result['scores']}

gr.Interface(fn=classify, inputs=gr.Image(), outputs=gr.Label()).launch()
```

### Streamlit 聊天 Demo

```python
import streamlit as st
from modelscope.pipelines import pipeline

pipe = pipeline('text-generation', model='Qwen/Qwen2-0.5B-Instruct')

st.title("魔搭聊天")
prompt = st.text_input("输入问题")
if prompt:
    result = pipe(prompt)
    st.write(result['text'])
```

## 与 Notebook 的区别

| 特性 | Notebook | 创空间 |
|------|----------|--------|
| 用途 | 开发调试 | 部署上线 |
| 持久化 | 会话级 | 持久运行 |
| 公网访问 | 不可 | 自动生成 URL |
| GPU | 免费 | 需勋章 |
