import librosa
import random
import matplotlib.pyplot as plt
import numpy as np
import time
import tensorflow as tf
import os
from PIL import Image
import cv2
from sklearn.preprocessing import StandardScaler

# 오디오 파일 멜 스펙트로그램, MFCC로 변환
def convert_audio_to_mel_spectrogram(audio_file_path):
    y, sr = librosa.load(audio_file_path, sr=16000)
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr) #sr 수치가 높을수록 자세히 봄
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)  # dB 스케일로 변환

    # 현재 시간 기반으로 한 이름 생성
    timestamp = int(time.time())
    mel_spectrogram_img_path = f'media\mel_spectrograms_img\mel_spectrogram_img_{timestamp}.png'
    mel_spectrogram_np_path = f'media\mel_spectrograms_np\mel_spectrogram_np_{timestamp}.npy'
    mfcc_path = f'media\mfcc\mfcc_{timestamp}.npy'

    #### Resnet50 데이터 전처리
    # 이미지로 저장
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mel_spectrogram_db, sr=sr, x_axis='time', y_axis='mel', fmax=8000) #fmax : 주파수의 최대값
    plt.colorbar(format='%+2.0f dB') # 모델이 학습하면 오버피팅 발생할 수 있어서 지우기
    # plt.title('Mel-Spectrogram')
    plt.savefig(mel_spectrogram_img_path)

    # 이미지 전처리
    img = cv2.imread(mel_spectrogram_img_path) 
    normalized_image = img.astype('float32') / 255.0  # 이미지 정규화
    resized_img = cv2.resize(img, (224, 224)) # 이미지 크기 조정 -> 모델이 사전 학습한 사진 크기에 맞추기 위해서
    resized_mel_batched = np.expand_dims(resized_img, axis=0)

    #### GRU 데이터 전처리
    max_len = 400 # 패딩할 최대 길이

    # MFCC 배열을 지정된 길이로 패딩하거나 잘라냄
    if mfcc.shape[1] < max_len:
        # pad_width(0,0) => 첫 번째 차원(행)에 대한 패딩이 없음
        # (0, max_len - mfcc.shape[1]) => 은 두 번째 차원(열)에 대한 패딩이 max_len-mfcc.shape[1]만큼 적용됨
        # MFCC 배열을 두 번째 차원(열)의 크기가 max_len이 되도록 패딩합니다.
        # 모든 MFCC 배열 동일한 길이 갖게 하도록
        # mode='constant' => 상수 값으로 채워지게 됨 => 상수 값을 사용하여 패딩되지 않은 영역을 특정 값으로 채우도록 설정
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, max_len - mfcc.shape[1])), mode='constant')
    else:
        mfcc = mfcc[:, :max_len] # 두 번째 차원에서 처음부터 max_len - 1 열까지의 모든 값을 포함합니다.
    
    ###### 전처리 과정 수정
    # resize보다 scale이 먼저여야 함
    scaler = StandardScaler()
    scaled_mfcc = scaler.fit_transform(mfcc)
    resized_mfcc = np.expand_dims(scaled_mfcc, axis=0)

    # 넘파이로 저장
    np.save(mel_spectrogram_np_path, mel_spectrogram_db)
    np.save(mfcc_path, resized_mfcc)

    return resized_mel_batched, mel_spectrogram_img_path, mel_spectrogram_np_path, mfcc_path, resized_mfcc

# resnet 모델 
def load_resnet_model():
    resnet_path = "phishing\model"
    model = tf.keras.models.load_model(resnet_path)
    return model

# GRU 모델
def load_gru_model():
    gru_path = "phishing\gru_model.h5"
    model = tf.keras.models.load_model(gru_path)
    return model

# 전화번호 랜덤 생성
def get_rand_numbers():
    numbers = '0123456789'
    num1 = "".join(random.sample(numbers, 4))
    num2 = "".join(random.sample(numbers, 4))

    phone_num = f"010-{num1}-{num2}"

    return phone_num