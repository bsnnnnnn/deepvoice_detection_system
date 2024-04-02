from django.db import models

# Create your models here.

# 유관기관 정보
class Organizations(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    image = models.CharField(max_length=255)
    call = models.CharField(max_length=50)
    work = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    category = models.CharField(max_length=20)

######딥보이스 탐지
class CallHistory(models.Model):
    id = models.AutoField(primary_key=True)
    called_at = models.DateTimeField(auto_now_add=True)
    numbers = models.CharField(max_length=50, null=True) #전화번호
    contents = models.TextField(null=True) #통화 내용
    audio_file = models.FileField(upload_to='audio/', null=True)
    results = models.BooleanField(null=True) #딥보이스 의심 여부
    # category = models.BooleanField(null=True) #기존 데이터 분류 카테고리

    # CallHistory 모델에 MFCC와 MelSpectrograms 모델과의 관계 추가
    mel_spectrogram = models.OneToOneField('MelSpectrograms', on_delete=models.CASCADE, null=True, related_name='call_history_mel_spectrogram')
    mfcc = models.OneToOneField('MFCC', on_delete=models.CASCADE, null=True, related_name='call_history_mfcc')

    def __str__(self):
        return f"CallHistory {self.id}"
    # def __str__(self): #객체를 문자열로 변환할 때 어떤 문자열을 반환할지
    #     return self.title

# 멜 스펙트로그램
class MelSpectrograms(models.Model):
    id = models.AutoField(primary_key=True)
    call_history = models.ForeignKey(CallHistory, on_delete=models.CASCADE, related_name='mel_spectrograms_data', null=True)
    mel_img = models.ImageField(upload_to='mel_spectrograms_img/', null=True)
    mel_np = models.FileField(upload_to='mel_spectrogram_np/', null=True)
    category = models.CharField(max_length=10, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"MelSpectrograms {self.id}"
    # def __str__(self): #객체를 문자열로 변환할 때 어떤 문자열을 반환할지
    #     return self.title

# mfcc
class MFCC(models.Model):
    id = models.AutoField(primary_key=True)
    call_history = models.ForeignKey(CallHistory, on_delete=models.CASCADE, related_name='mfcc_data', null=True)
    mfcc = models.FileField(upload_to='mfcc/', null=True)
    category = models.CharField(max_length=10, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"MFCC {self.id}"

# 텍스트 테이블 1. 메일, 문자
class Text_mail(models.Model):
    id = models.AutoField(primary_key=True)
    # filename = models.CharField(max_length=50, null=True)
    message = models.TextField()
    label = models.BooleanField(null=True) #default 설정 가능
    phone_number = models.CharField(max_length=50, null=True)
    message_embedding = models.TextField(null=True)

# 텍스트 테이블 2. KorCCVi
class Text_KorCCVi(models.Model):
    id = models.AutoField(primary_key=True)
    transcript = models.TextField()
    label = models.BooleanField(null=True)
