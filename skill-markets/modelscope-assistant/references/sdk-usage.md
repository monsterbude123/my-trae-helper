# SDK 使用速查

## 安装

```bash
pip install modelscope
```

## Pipeline API（一行推理）

```python
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# NLP 示例：情感分析
nlp_pipe = pipeline(Tasks.sentiment_classification, model='damo/nlp_structbert_sentiment-classification_chinese-base')
result = nlp_pipe('这个电影真好看')
# → {'labels': ['正面'], 'scores': [0.99]}

# CV 示例：图像分类
cv_pipe = pipeline(Tasks.image_classification, model='damo/cv_resnet50_image-classification')
result = cv_pipe('path/to/image.jpg')

# 语音示例：语音识别
asr_pipe = pipeline(Tasks.auto_speech_recognition, model='damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch')
result = asr_pipe('path/to/audio.wav')

# 多模态：图文描述
mm_pipe = pipeline(Tasks.image_captioning, model='damo/ofa_image-caption_muge_base_zh')
result = mm_pipe('path/to/image.jpg')
```

## 模型下载

```python
from modelscope import snapshot_download

# 下载到指定目录
model_dir = snapshot_download('damo/nlp_structbert_sentiment-classification_chinese-base',
                               cache_dir='./my_models')

# CLI 方式
# modelscope download --model damo/nlp_structbert_sentiment-classification_chinese-base --local_dir ./checkpoint
```

## 数据集下载

```python
from modelscope import dataset_snapshot_download

dataset_dir = dataset_snapshot_download('OpenDataLab/Fashion-MNIST', local_dir='./dataset')

# CLI 方式
# modelscope download --dataset OpenDataLab/Fashion-MNIST --local_dir ./dataset
```

## 数据集加载

```python
from modelscope.msdatasets import MsDataset

# 加载数据集
ds = MsDataset.load('damo/zh_cls_fudan-news', subset_name='default', split='train')
for item in ds:
    print(item)
```

## 模型上传

```python
from modelscope.hub.api import HubApi

api = HubApi()
api.login()  # 需要先登录

# 创建模型仓库 → 网页端操作更直观
# 上传文件：网页端 / CLI / SDK 均支持
```
