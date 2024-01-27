import sys
import os
import random
import shutil
from pydub.utils import mediainfo
from pydub import AudioSegment

DATASET_VOICE_DIR = r"D:\$SysReset\PJSK语音\PJSK角色语音与对应文本一站式获取\nene\nenewav"  # 数据集干声文件夹
DATASET_LABEL_PATH = (
    r"D:\$SysReset\PJSK语音\PJSK角色语音与对应文本一站式获取\nene\nene_org.txt"  # 数据集标签文件
)
DATASET_SLICER_DIR = r"D:\AI\GPT-SoVITS\dataset\slicer_opt"
TOTAL_SELECT_TIME = 60 * 60
IGNORE_TIME = 2  # 忽略长度小于2秒的文件
OUTPUT_VOICE_DIR = r"D:\AI\GPT-SoVITS\dataset\voice"  # 输出文件夹
OUTPUT_LABEL_PATH = r"D:\AI\GPT-SoVITS\dataset\label.list"  # 输出文件路径
AUDIO_EXTENSIONS = [".mp3", ".wav"]  # 音频文件扩展名
SPEAKER_NAME = "nene"  # 说话人名称
LANGUAGE = "ja"  # 语言


def select_dataset(
    dataset_dir=DATASET_VOICE_DIR,
    total_select_time=TOTAL_SELECT_TIME,
    ignore_time=IGNORE_TIME,
    output_dir=OUTPUT_VOICE_DIR,
):
    """
    @detail 数据集有5h, 但是按照作者的说法1h就到边界效应了, 所以随机选择干声
    @param dataset_dir: 数据集文件夹
    @param total_select_time: 选择的总时长
    @param ignore_time: 忽略长度小于n秒的文件
    @param output_dir: 输出文件夹
    """
    files = [
        f
        for f in os.listdir(dataset_dir)
        if any(f.endswith(ext) for ext in AUDIO_EXTENSIONS)
    ]

    # 随机选择文件，直到总长度达到
    selected_files = []
    total_length = 0
    while total_length < total_select_time:
        file = random.choice(files)
        file_length = float(mediainfo(os.path.join(dataset_dir, file))["duration"])
        if file_length >= ignore_time:
            files.remove(file)  # 从列表中移除已选择的文件，避免重复选择
            selected_files.append(file)
            total_length += file_length
            sys.stdout.write(
                f"\rCurrent total length: {int(total_length)} seconds, target: {total_select_time} seconds"
            )
        sys.stdout.flush()

    # 将选择的文件复制到输出文件夹
    for file in selected_files:
        shutil.copy(os.path.join(dataset_dir, file), output_dir)


def select_label(
    dataset_dir=OUTPUT_VOICE_DIR,
    label_path=DATASET_LABEL_PATH,
    output_path=OUTPUT_LABEL_PATH,
    spkear=SPEAKER_NAME,
    lang=LANGUAGE,
):
    """
    @detail 选择标签
    @param dataset_dir: 数据集文件夹
    @param label_path: 标签文件路径
    @param output_path: 输出文件路径
    @param spkear: 说话人名称
    @param lang: 语言
    """
    # 获取文件夹中所有音频文件的列表
    files = [
        f
        for f in os.listdir(dataset_dir)
        if any(f.endswith(ext) for ext in AUDIO_EXTENSIONS)
    ]

    with open(label_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 创建一个字典，键是文件名（去掉"nene\"的部分），值是标签
    labels = {
        os.path.splitext(line.split("|")[0].replace("nene\\", ""))[0]
        + ".mp3": line.split("|")[1].strip()
        for line in lines
    }

    for file in files:
        # 从字典中获取标签
        if file in labels:
            label = labels[file]
            # 将标签写入文件
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(
                    f"/content/drive/MyDrive/GPT-SoVITS/dataset/voice/{file}|{spkear}|{lang}|{label}\n"
                )
            del labels[file]  # 删除已经分配了标签的文件名
        else:
            # 如果文件名不在字典中，报错
            raise Exception(f"File {file} not found in labels")


# def convert_mp3_to_wav(directory=OUTPUT_VOICE_DIR):
#     for filename in os.listdir(directory):
#         if filename.endswith(".mp3"):
#             mp3_sound = AudioSegment.from_mp3(os.path.join(directory, filename))
#             wav_filename = os.path.splitext(filename)[0] + ".wav"
#             mp3_sound.export(os.path.join(directory, wav_filename), format="wav")


# def delete_mp3_files(directory=OUTPUT_VOICE_DIR):
#     for filename in os.listdir(directory):
#         if filename.endswith(".mp3"):
#             os.remove(os.path.join(directory, filename))


if __name__ == "__main__":
    select_dataset()
    select_label()
