from django.shortcuts import render, redirect
from django.http import HttpResponse
# phishing/views.py
from .model.models import Organizations, CallHistory, Text_mail, MelSpectrograms, MFCC
from django.core.paginator import Paginator

from django.views import View
from django.http import JsonResponse

# from .utils import load_kcbert_model, calculate_embedding
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .forms import AudioDataForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

# 신고하기
def notify(request):
    return render(request, 'notify.html')

# 번호 조회 결과 : 위험도 높음
def result_num_high(request):
    return render(request, 'result_num_high.html')

# 번호 조회 결과 : 위험도 낮음
def result_num_low(request):
    return render(request, 'result_num_low.html')

# 모델 결과 : 위험도 높음
def result_high(request):
    # is_blocking_active = False
    detection_list = CallHistory.objects.all()
    return render(request, 'result_model_high.html', {'detection_list':detection_list})

# 모델 결과 : 위험도 낮음
def result_low(request):
    detection_list = CallHistory.objects.all()
    return render(request, 'result_model_low.html', {'detection_list':detection_list})

# 기관 정보
def rel_org(request): #기관 전체
    # page = request.GET.get('page', '1')
    orgs_list = Organizations.objects.all()
    # paginator = Paginator(orgs_list, 8) #페이지당 8개씩 보여주기
    # page_obj = paginator.get_page(page)
    return render(request, 'rel_organization.html', {"orgs_list":orgs_list})

def financial(request): #금융 기관
    # page = request.GET.get('page', '1')
    orgs_list = Organizations.objects.all()
    # paginator = Paginator(orgs_list, 8) #페이지당 8개씩 보여주기
    # page_obj = paginator.get_page(page)
    # context = {'question_list':page_obj}
    return render(request, 'financial.html', {'orgs_list':orgs_list})

def investigative(request): #수사 및 신고기관
    orgs_list = Organizations.objects.all()
    return render(request, 'investigative.html', {'orgs_list':orgs_list})

# 대응방법 안내
def victim_guide(request):
    return render(request, 'victim_guide.html')

# 실시간 탐지 시 정보 제공 동의 여부 확인
def agreement(request):
    return render(request, 'agreement.html')

# 탐지 내역 조회테스트
def detection_history(request):
    detection_list = CallHistory.objects.all()
    return render(request, 'detection_history.html', {'detection_list':detection_list})

##### RESNET50 + GRU
from .utils import convert_audio_to_mel_spectrogram, load_resnet_model, load_gru_model, get_rand_numbers
import cv2
from django.shortcuts import get_object_or_404

# 오디오 파일 입력 받기
def deepvoice_detection(request):
    if request.method == 'POST':
        form = AudioDataForm(request.POST, request.FILES)
        if form.is_valid():
            audio_data = form.save()
            
            # 디버깅 출력 추가
            # pripythnt('Uploaded file path:', audio_data.audio_file.path)

             # 이미 저장된 오디오 파일이 있는지 확인
            callhistory = CallHistory()

            callhistory, created = CallHistory.objects.get_or_create(
                audio_file=audio_data.audio_file.name,  # 파일 이름 또는 고유 식별자 전달
                defaults={'results': False, 'numbers': get_rand_numbers()}
            )

            call_number = get_rand_numbers()
            callhistory.numbers = call_number

            # 음성 파일을 멜 스펙트로그램으로 변환
            resized_mel_batched, mel_spectrogram_img_path, mel_spectrogram_np_path, mfcc_path, resized_mfcc = convert_audio_to_mel_spectrogram(audio_data.audio_file.path)

            ######## Resnet50
            resnet_model = load_resnet_model()
            resnet_result = resnet_model.predict(resized_mel_batched)
            resnet_result = resnet_result[0][0]

            ####### GRU
            gru_model = load_gru_model()
            gru_result = gru_model.predict(resized_mfcc)
            gru_result = gru_result[0][1] #fake value

            # 최종 결과
            result = (gru_result*0.7) + (resnet_result*0.3)

            threshold = 0.5

            # 모델 인스턴스 생성 및 모델에 멜 스펙트로그램 경로 데이터 저장
            mel_spectrograms = MelSpectrograms()
            mel_spectrograms.mel_img = mel_spectrogram_img_path
            mel_spectrograms.mel_np = mel_spectrogram_np_path
            mel_spectrograms.call_history = callhistory

            mfcc_model = MFCC()
            mfcc_model.mfcc = mfcc_path
            mfcc_model.call_history = callhistory

            # 결과에 따라 다른 페이지 반환
            if result >= threshold: # 복제 음성 의심
                callhistory.results = True # 탐지 결과 저장
                callhistory.save()

                mel_spectrograms.category = 1
                mel_spectrograms.save()

                mfcc_model.category = 1
                mfcc_model.save()

                return render(request, 'result_model_high.html', {'result':result, 'resnet_result':resnet_result, 'gru_result':gru_result, 'call_number':call_number})
            else:
                callhistory.results = False # 탐지 결과 저장
                callhistory.save()

                mel_spectrograms.category = 0
                mel_spectrograms.save()

                mfcc_model.category = 0
                mfcc_model.save()
                return render(request, 'result_model_low.html', {'result':result, 'resnet_result':resnet_result, 'gru_result':gru_result, 'call_number':call_number})
        
    else: # 저장에 실패할 경우
        form = AudioDataForm()
    
    return render(request, 'deepvoice_detection.html', {'form':form})