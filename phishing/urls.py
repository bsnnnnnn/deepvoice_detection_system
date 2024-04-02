from django.urls import path
from . import views

app_name = 'phishing'

urlpatterns = [
    path('', views.home, name='home'),
    path('notify/', views.notify, name='notify'), #신고 페이지
    path('result_high/', views.result_high, name='result_high'), #모델 결과 페이지 : 위험도 높음
    path('result_low/', views.result_low, name='result_low'), #모델 결과 페이지 : 위험도 낮음
    path('rel_org/', views.rel_org, name='rel_org'), #관련 기관 리스트
    path('financial/', views.financial, name='financial'), #금융기관 리스트
    path('investigative/', views.investigative, name='investigative'), #수사 및 신고기관 리스트
    path('victim_guide/', views.victim_guide, name='victim_guide'), #대응방법 가이드
    path('agreement/', views.agreement),
    path('deepvoice_detection/', views.deepvoice_detection, name='deepvoice_detection' ), # 딥보이스 탐지 페이지
    path('detection_history/', views.detection_history, name='detection_history' ),
]
