from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import json
import shutil 
from datetime import datetime, UTC
from audio_transform import AudioTransform
from audio_split import AudioSplit

app = Flask(__name__)
CORS(app)  

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
TEMP_FOLDER = "temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}"
        file_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}-{file.filename}")
        file.save(file_path)
        
        # Process the audio
        audio_transform = AudioTransform(
            model_name="medium",
            device="cpu",
            compute_type="int8",
            language=None,
            word_timestamps=True
        )
        
        preprocessed_audio_dir_path = os.path.join("temp", f"{filename}")
        os.makedirs(preprocessed_audio_dir_path, exist_ok=True)
        preprocessed_audio_file = f"preprocessed-{filename}.mp3"
        audio_transform.preprocess_audio(file_path, output_file=os.path.join(preprocessed_audio_dir_path, preprocessed_audio_file))
        
        audio_segments = audio_transform.transcribe_audio(audio_file=os.path.join(preprocessed_audio_dir_path, preprocessed_audio_file))
        
        audio_split = AudioSplit(
            audio_file=file_path,
            segments=audio_segments,
            sentence_end_fix=0.2,
            word_end_fix=0.1
        )
        
        audio_split_output_dir_path = os.path.join(OUTPUT_FOLDER, f"{filename}")
        os.makedirs(audio_split_output_dir_path, exist_ok=True)
        audio_split.cut_audio_by_sentences(output_dir=os.path.join(audio_split_output_dir_path, "sentences"))
        audio_split.cut_audio_by_words(output_dir=os.path.join(audio_split_output_dir_path, "words"))
        audio_split.save_to_json(audio_split.serialize_sentences(), output_file=os.path.join(audio_split_output_dir_path, "sentences.json"))
        audio_split.save_to_json(audio_split.serialize_words(), output_file=os.path.join(audio_split_output_dir_path, "words.json"))
        
        return jsonify({"message": "File processed successfully", "output_dir": audio_split_output_dir_path}), 200

@app.route('/get-original-audio/<timestamp>', methods=['GET'])
def get_original_audio(timestamp):
    try:
        # 在 uploads 文件夹中查找匹配的文件
        for upload_file in os.listdir(UPLOAD_FOLDER):
            if upload_file.startswith(timestamp + "-"):
                upload_file_path = os.path.join(UPLOAD_FOLDER, upload_file)
                if os.path.exists(upload_file_path):
                    return send_from_directory(os.path.dirname(upload_file_path), os.path.basename(upload_file_path))
        return jsonify({"error": "Original audio file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-processed-file/<timestamp>', methods=['DELETE'])
def delete_processed_file(timestamp):
    try:
        # 删除 output 文件夹中的对应文件夹
        output_folder_path = os.path.join(OUTPUT_FOLDER, timestamp)
        if os.path.exists(output_folder_path):
            shutil.rmtree(output_folder_path)  # 递归删除文件夹

        # 删除 uploads 文件夹中的对应文件
        for upload_file in os.listdir(UPLOAD_FOLDER):
            if upload_file.startswith(timestamp + "-"):
                upload_file_path = os.path.join(UPLOAD_FOLDER, upload_file)
                if os.path.exists(upload_file_path):
                    os.remove(upload_file_path)
                break  # 找到匹配的文件后跳出循环

        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-temp', methods=['DELETE'])
def clear_temp():
    try:
        if os.path.exists(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)  # 递归删除缓存文件夹
            os.makedirs(TEMP_FOLDER)    # 重新创建空文件夹
        return jsonify({"message": "Temp folder cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/processed-files', methods=['GET'])
def get_processed_files():
    try:
        processed_files = []
        
        # 遍历 output 文件夹中的所有文件夹
        for timestamp_folder in os.listdir(OUTPUT_FOLDER):
            output_folder_path = os.path.join(OUTPUT_FOLDER, timestamp_folder)
            
            # 检查是否是文件夹且包含必要的文件
            if os.path.isdir(output_folder_path):
                sentences_path = os.path.join(output_folder_path, "sentences.json")
                words_path = os.path.join(output_folder_path, "words.json")
                
                if os.path.exists(sentences_path) and os.path.exists(words_path):
                    # 在 uploads 文件夹中查找匹配的文件
                    for upload_file in os.listdir(UPLOAD_FOLDER):
                        if upload_file.startswith(timestamp_folder + "-"):
                            # 提取原始文件名
                            original_filename = upload_file[len(timestamp_folder) + 1:]
                            
                            # 添加到处理文件列表
                            processed_files.append({
                                "folder_name": original_filename,  # 原始文件名
                                "timestamp": timestamp_folder,     # 时间戳文件夹名
                                "sentences_file": sentences_path,
                                "words_file": words_path
                            })
                            break  # 找到匹配的文件后跳出循环
        
        return jsonify({"processed_files": processed_files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/results/<output_dir>', methods=['GET'])
def get_results(output_dir):
    sentences_path = os.path.join(OUTPUT_FOLDER, output_dir, "sentences.json")
    words_path = os.path.join(OUTPUT_FOLDER, output_dir, "words.json")
    
    if not os.path.exists(sentences_path) or not os.path.exists(words_path):
        return jsonify({"error": "Results not found"}), 404
    
    with open(sentences_path, 'r') as f:
        sentences = json.load(f)
    with open(words_path, 'r') as f:
        words = json.load(f)
    
    return jsonify({"sentences": sentences, "words": words}), 200

@app.route('/audio/<output_dir>/sentences/<filename>', methods=['GET'])
def get_sentence_audio(output_dir, filename):
    audio_path = os.path.join(OUTPUT_FOLDER, output_dir, "sentences", f"sentence_{filename}.mp3")
    print(audio_path)

    if not os.path.exists(audio_path):
        return jsonify({"error": "Sentence audio file not found"}), 404
    return send_from_directory(os.path.dirname(audio_path), os.path.basename(audio_path))

@app.route('/audio/<output_dir>/words/<sentence_id>/<filename>', methods=['GET'])
def get_word_audio(output_dir, sentence_id, filename):
    audio_path = os.path.join(OUTPUT_FOLDER, output_dir, "words", f"sentence_{sentence_id}",  f"word_{filename}.mp3")
    print(audio_path)
    if not os.path.exists(audio_path):
        return jsonify({"error": "Word audio file not found"}), 404
    return send_from_directory(os.path.dirname(audio_path), os.path.basename(audio_path))

if __name__ == '__main__':
    app.run(debug=True)