import os
import time
from datetime import datetime, UTC
from audio_transform import AudioTransform
from audio_split import AudioSplit

def main():
    audio_transform = AudioTransform(
        model_name="base",
        device="cpu",
        compute_type="int8",
        language="en",
        word_timestamps=True
    )
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    # 对音频进行预处理
    audio_dir_path = "../static"
    audio_file = "long-test.mp4"
    audio_name = audio_transform.get_filename_without_extension(audio_file)
    
    preprocessed_audio_dir_path = os.path.join("../temp", f"{audio_name}-{timestamp}")
    os.makedirs(preprocessed_audio_dir_path, exist_ok=True)
    preprocessed_audio_file = f"preprocessed-{audio_name}.mp3"

    preprocessed_audio = audio_transform.preprocess_audio(os.path.join(audio_dir_path, audio_file), output_file=os.path.join(preprocessed_audio_dir_path, preprocessed_audio_file))

    # 调用 Faster Whisper 进行识别
    audio_segments = audio_transform.transcribe_audio(audio_file=os.path.join(preprocessed_audio_dir_path, preprocessed_audio_file))

    # 调用Pydub 进行词、句分割
    audio_split = AudioSplit(
        audio_file=os.path.join(audio_dir_path, audio_file),
        segments=audio_segments,
        sentence_end_fix= 0.2,
        word_end_fix= 0.1
    )
    audio_split_output_dir_path = os.path.join("../output/", f"{audio_name}-{timestamp}")
    os.makedirs(audio_split_output_dir_path, exist_ok=True)

    audio_split.cut_audio_by_sentences(output_dir=os.path.join(audio_split_output_dir_path, "sentences"))
    audio_split.cut_audio_by_words(output_dir=os.path.join(audio_split_output_dir_path, "words"))
    audio_split.save_to_json(audio_split.serialize_sentences(), output_file=os.path.join(audio_split_output_dir_path, "sentences.json"))
    audio_split.save_to_json(audio_split.serialize_words(), output_file=os.path.join(audio_split_output_dir_path, "words.json"))

if __name__ == "__main__":
    main()

