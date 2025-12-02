from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from grades.models import Grade
import json

# NOT: 'statistics_dashboard' view'ınızı bu dosyanın başka bir yerinde
# rol yönlendirmesi için tuttuğunuzu varsayıyorum.

# @login_required

def dean_stats(request):
    # =======================================================
    # 1. DÖNEMLİK GNO EĞİLİMİ (Mevcut Çalışan Kod)
    # =======================================================
    donem_ortalama_egilimi = Grade.objects.filter(
        gpa_value__isnull=False
    ).values(
        'offering__year',
        'offering__semester'
    ).annotate(
        ortalama_gpa=Avg('gpa_value'),
        toplam_ders=Count('id')
    ).order_by('offering__year', 'offering__semester')

    labels = []
    data = []
    for item in donem_ortalama_egilimi:
        label = f"{item['offering__year']}-{item['offering__semester']}"
        labels.append(label)
        data.append(round(item['ortalama_gpa'], 2))

    # =======================================================
    # 2. BÖLÜM KIYASLAMA İSTATİSTİKLERİ (MOCK DATA KULLANILARAK)
    # Grafikleri doldurmak için Mock verileri kullanmaya devam ediyoruz.
    # =======================================================

    # A. Bölümler Arası Ortalama GPA
    bolum_labels = ['Bilgisayar Müh.', 'Biyomedikal Müh.', 'Elektrik-Elektronik', 'Makine Müh.']
    bolum_gpa_data = [2.95, 3.12, 2.78, 3.05]

    # B. Bölümler Arası Devamsızlık Oranları
    devamsizlik_labels = ['Bilgisayar', 'Biyomedikal', 'Diğerleri']
    devamsizlik_data = [350, 420, 1200]

    # =======================================================
    # 3. CONTEXT GÜNCELLEMESİ (TÜM VERİLER JSON'A ÇEVRİLİYOR)
    # =======================================================
    context = {
        'page_title': 'Fakülte Genel İstatistik Paneli',

        # Dönem Eğilimi Verileri
        'donem_labels': json.dumps(labels),
        'donem_gpa_data': json.dumps(data),
        'egilim_tablosu': donem_ortalama_egilimi,

        # Bölüm Kıyaslama Verileri
        'bolum_labels': json.dumps(bolum_labels),
        'bolum_gpa_data': json.dumps(bolum_gpa_data),

        # Devamsızlık Verileri
        'devamsizlik_labels': json.dumps(devamsizlik_labels),
        'devamsizlik_data': json.dumps(devamsizlik_data),
    }

    return render(request, 'statistic/dean_statistic.html', context)