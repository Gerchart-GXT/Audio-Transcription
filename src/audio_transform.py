import os
from pydub import AudioSegment
from faster_whisper import WhisperModel

class AudioTransform:
    def __init__(self, model_name="base", device="cpu", compute_type="int8", language=None, 
                 beam_size=5, best_of=5, patience=1, length_penalty=1.0, temperature=0.0, 
                 compression_ratio_threshold=2.4, log_prob_threshold=-1.0, no_speech_threshold=0.6, 
                 condition_on_previous_text=True, initial_prompt=None, word_timestamps=True, 
                 prepend_punctuations="\"'“¿([{-", append_punctuations="\"'.。,，!！?？:：”)]}、"):
        """
        构造函数
        :param model_name: 模型名称（如 "base", "medium", "large"）
        :param device: 设备类型（如 "cpu", "cuda"）
        :param compute_type: 计算类型（如 "int8", "float16"）
        :param language: 音频语言（如 "en", "zh"），如果为 None 则自动检测
        :param beam_size: Beam 搜索的大小
        :param best_of: Beam 搜索的候选数量
        :param patience: Beam 搜索的耐心值
        :param length_penalty: 长度惩罚系数
        :param temperature: 采样温度
        :param compression_ratio_threshold: 压缩比阈值
        :param log_prob_threshold: 对数概率阈值
        :param no_speech_threshold: 无语音段阈值
        :param condition_on_previous_text: 是否基于前文进行条件化
        :param initial_prompt: 初始提示文本
        :param word_timestamps: 是否返回单词时间戳
        :param prepend_punctuations: 前置标点符号
        :param append_punctuations: 后置标点符号
        """
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.beam_size = beam_size
        self.best_of = best_of
        self.patience = patience
        self.length_penalty = length_penalty
        self.temperature = temperature
        self.compression_ratio_threshold = compression_ratio_threshold
        self.log_prob_threshold = log_prob_threshold
        self.no_speech_threshold = no_speech_threshold
        self.condition_on_previous_text = condition_on_previous_text
        self.initial_prompt = initial_prompt
        self.word_timestamps = word_timestamps
        self.prepend_punctuations = prepend_punctuations
        self.append_punctuations = append_punctuations
        # 加载模型
        self.model = WhisperModel(
            model_name, device=device, compute_type=compute_type
        )
    def get_filename_without_extension(self, file_path):
        """
        获取不包含后缀的文件名
        :param file_path: 文件路径
        :return: 不包含后缀的文件名
        """
        return os.path.splitext(os.path.basename(file_path))[0]

    def preprocess_audio(self, audio_file, output_file=None, normalize=True, sample_rate=16000):
        """
        对音频进行预处理
        :param audio_file: 输入音频文件路径
        :param output_file: 输出音频文件路径（如果为 None，则返回 AudioSegment 对象）
        :param normalize: 是否对音频进行标准化
        :param sample_rate: 目标采样率
        :return: 如果 output_file 为 None，返回 AudioSegment 对象；否则返回 None
        """
        # 加载音频
        audio = AudioSegment.from_file(audio_file)
        # 标准化音频
        if normalize:
            audio = audio.normalize()
        # 重采样音频
        audio = audio.set_frame_rate(sample_rate)
        # 保存或返回处理后的音频
        if output_file:
            audio.export(output_file, format="mp3")
            return None
        else:
            return audio

    def transcribe_audio(self, audio_file, **kwargs):
        """
        调用 Faster Whisper 对音频进行识别
        :param audio_file: 音频文件路径
        :param kwargs: 可覆盖构造函数的参数
        :return: 包含识别结果的 segments 对象
        """
        # 合并构造函数参数和传入参数
        params = {
            "language": self.language,
            "beam_size": self.beam_size,
            "best_of": self.best_of,
            "patience": self.patience,
            "length_penalty": self.length_penalty,
            "temperature": self.temperature,
            "compression_ratio_threshold": self.compression_ratio_threshold,
            "log_prob_threshold": self.log_prob_threshold,
            "no_speech_threshold": self.no_speech_threshold,
            "condition_on_previous_text": self.condition_on_previous_text,
            "initial_prompt": self.initial_prompt,
            "word_timestamps": self.word_timestamps,
            "prepend_punctuations": self.prepend_punctuations,
            "append_punctuations": self.append_punctuations,
        }
        params.update(kwargs)
        # 调用 Faster Whisper 进行识别
        segments, _ = self.model.transcribe(audio_file, **params)
        return list(segments)