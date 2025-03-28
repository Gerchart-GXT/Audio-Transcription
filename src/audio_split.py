import os
import json

from pydub import AudioSegment

class AudioSplit:
    def __init__(self, audio_file, segments, sentence_end_fix = 0.0, word_end_fix = 0.0):
        """
        构造函数
        :param audio_file: 音频文件路径
        :param segments: 包含句子和单词时间戳的 segment 对象
        """
        self.audio_file = audio_file
        self.segments = segments
        self.audio = AudioSegment.from_file(audio_file)
        self.sentence_end_fix = sentence_end_fix
        self.word_end_fix = word_end_fix

    def cut_audio(self, start_time, end_time, output_path):
        """
        根据起始时间和终止时间切割音频，并保存到指定路径
        :param start_time: 起始时间（秒）
        :param end_time: 终止时间（秒）
        :param output_path: 输出文件路径
        """
        start_ms = int(start_time * 1000)  # 转换为毫秒
        end_ms = int(end_time * 1000)      # 转换为毫秒
        segment_audio = self.audio[start_ms:end_ms]
        segment_audio.export(output_path, format="mp3")
        print(f"Saved {output_path}")

    def cut_audio_by_sentences(self, output_dir="output_sentences"):
        """
        根据 segment 的句子划分切割音频，并保存每个句子
        :param output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        for i, segment in enumerate(self.segments):
            output_path = os.path.join(output_dir, f"sentence_{i+1}.mp3")
            self.cut_audio(segment.start, segment.end + self.sentence_end_fix, output_path)

    def cut_audio_by_words(self, output_dir="output_words"):
        """
        根据 segment 的单词划分切割音频，并保存每个单词
        :param output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        for i, segment in enumerate(self.segments):
            os.makedirs(os.path.join(output_dir, f"sentence_{i+1}"), exist_ok=True)
            for j, word in enumerate(segment.words):
                output_path = os.path.join(os.path.join(output_dir, f"sentence_{i+1}"), f"word_{j+1}.mp3")
                self.cut_audio(word.start, word.end + self.sentence_end_fix, output_path)

    def serialize_sentences(self):
        """
        将句子分割结果序列化为简单数据结构
        :return: 包含句子内容、起始时间和终止时间的列表
        """
        sentences = []
        for segment in self.segments:
            sentences.append({
                "text": segment.text,
                "start": segment.start,
                "end": segment.end + self.sentence_end_fix
            })
        return sentences

    def serialize_words(self):
        """
        将单词分割结果序列化为简单数据结构
        :return: 包含单词内容、起始时间和终止时间的列表
        """
        words = []
        for segment in self.segments:
            for word in segment.words:
                words.append({
                    "text": word.word,
                    "start": word.start,
                    "end": word.end + self.word_end_fix
                })
        return words
    
    def save_to_json(self, data, output_file):
        """
        将数据保存为 JSON 文件
        :param data: 要保存的数据（列表或字典）
        :param output_file: 输出文件路径
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved to {output_file}")