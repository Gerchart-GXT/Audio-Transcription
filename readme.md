# 基于Faster-Whisper和LLM的语言学习听写助手
## 项目背景
最近被专四的dictation和conversation按在地上摩擦，找到了一些简单的听写材料，但奈何每次都得手动暂停/播放来流出整句听写的时间，并且想回退反复听总是要么多倒要么少退，很是恼人。于是就简单写个应用来实现听力材料的分句和分词，希望对我的听力学习有所帮助（狗头）
## 项目技术简介
1. `Faster-Whisper`
* 这个好东西，比O`penAI`的`Whisper`快很多，并且只需要`Python`环境就能跑。即使跑在CPU上，`medium`的模型速度也不赖，识别准确度也很高
2. 肯定是前后端分离了
* 后端简单`python`写写，`flask`包一下
* 前端配合着`Claude`写个静态页面，然后把三件套合成大西瓜挂给`nginx`就行了
3. 随便找个LLM进行一个分句（`Deepseek V3`这么便宜，肯定用它啊）
## 处理流程
1. 音频文件输入后，进行一些Normalize，主要是`Faster-Whisper`要求输入采样率`16K`，`Pydub`处理一下即可
2. 交给`Faster-Whisper`进行语音识别，开启一下`word`识别
3. 交给LLM重新对识别结果进行分句，保证最后每个segment都是完整的一句话
4. 根据分句结果将音频文件进行裁切，同时也裁出每个单词，前端直接访问即可
## 使用介绍
1. 上传音频，`Select`后`upload`即可，`reset`清空
![1743177042684.png](https://picture.imgxt.com/local/1/2025/03/28/67e6c554632d5.png)
2. 等待后端转写分句完成，最好别刷新
![1743177071259.png](https://picture.imgxt.com/local/1/2025/03/28/67e6c5718a02e.png)
3. 刷新列表后选择对应的音频文件，即可进行使用。
* 点击最上方`play`播放全文，后有进度条可直达
* 点击Sentence的`play`即可播放该句
* 点击Sentence的`div`即可显示当前句文本
* 点击Sentence的`Expand words`即可展开单词，选择对应单词单击可听该词语音
![1743177189655.png](https://picture.imgxt.com/local/1/2025/03/28/67e6c5e72af57.png)
4. 列表中点击对应音频文件的`delete`即可将已处理的该文件删掉
5. `Clear Temp Cache`是用来清除预处理时的缓存的，不会删除已处理的文件
## 长图预览
![1743177217393.png](https://picture.imgxt.com/local/1/2025/03/28/67e6c60422b6a.png)
## 部署
1. 安装好`Python3.12`
2. 创建`venv`
3. `pip`安装`requirement.txt`依赖
4. 进入src目录`python3 app.py`运行即可，或者`gunicorn -w 4 -b 0.0.0.0:5000 app:app`也行
5. 本地打开`front/index.html`进行使用即可