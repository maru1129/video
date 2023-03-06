import os
import numpy as np
import librosa
from pydub import AudioSegment
import cv2
from moviepy.editor import *



file_path = "[VIDEOFILE_PATH]"
save_path = "[VIDEOFILE_SAVE_PATH]"
cutsound_tmp_path = save_path[:-4]+"_tmp.mp3"  # 処理した音声の一時保存ファイル
cutvideo_tmp_path = save_path[:-4]+"_tmp.mp4"  # 処理した動画の一時保存ファイル
min_setting = 0 # 無音の設定値（配列番号）



#動画ファイルから音声を読み込む
sound = AudioSegment.from_file(file_path)

## dbに変換
np_sound = np.array(sound.get_array_of_samples()) / 32768.0   # 正規化
db_npsound = librosa.amplitude_to_db(np_sound)

threshold = sorted(set(db_npsound))[min_setting]     # 無音の閾値設定  (ex: [-100.0, -90.3, -84.2, -80.76 ...] )
tsound = np_sound[db_npsound>threshold]


tsound = tsound*32768.0
tsound = AudioSegment(
    tsound.astype("int16").tobytes(),
    sample_width=sound.sample_width, 
    frame_rate=sound.frame_rate, 
    channels=sound.channels,
)
tsound.export(cutsound_tmp_path, format="mp3")


# 動画処理
video = cv2.VideoCapture(file_path)

# 動画の無音区間以外を抽出
video_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
sound_block = len(sound.get_array_of_samples()) // video_frame
tsound_num = np.array(np.where(db_npsound>threshold))
tvideo_frame = np.unique(tsound_num // sound_block)


# 幅と高さを取得
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)

#フレームレート(1フレームの時間単位はミリ秒)の取得
frame_rate = int(video.get(cv2.CAP_PROP_FPS))

# 保存用
fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
writer = cv2.VideoWriter(cutvideo_tmp_path, fmt, frame_rate, size)

for i in tvideo_frame:
    video.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, image = video.read()
    # if i == tvideo_frame[i]
        ### ここに加工処理などを記述する ###
    writer.write(image)

writer.release()
video.release()

clip = VideoFileClip(cutvideo_tmp_path)
clip.write_videofile(save_path,audio=cutsound_tmp_path)  # 音声と動画の結合

# 一時保存ファイルの削除
os.remove(cutvideo_tmp_path) 
os.remove(cutsound_tmp_path)

print("---end---")






