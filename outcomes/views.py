from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import messages
import tempfile
import os
from .models import ProgramOutcome
from .management.commands.import_outcomes import OutcomeImporter

@staff_member_required
def dekan_dashboard(request):
    """Dekan için özel dashboard"""
    if request.method == 'POST' and request.FILES.get('docx_file'):
        docx_file = request.FILES['docx_file']
        program_type = request.POST.get('program_type', 'auto')
        
        # Geçici dosyaya kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            for chunk in docx_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Import işlemi
        importer = OutcomeImporter()
        
        if program_type == 'auto':
            outcomes, detected_program = importer.parse_docx_file(tmp_path)
        else:
            outcomes, detected_program = importer.parse_docx_file(tmp_path, program_type)
        
        if outcomes and detected_program:
            for outcome in outcomes:
                ProgramOutcome.objects.update_or_create(
                    program=detected_program,
                    outcome_number=outcome['number'],
                    defaults={'description': outcome['description']}
                )
            
            messages.success(request, f'✅ {len(outcomes)} outcome başarıyla yüklendi! ({detected_program})')
        else:
            messages.error(request, '❌ Dosyadan outcome çıkarılamadı!')
        
        # Geçici dosyayı sil
        os.unlink(tmp_path)
    
    # İstatistikler
    biomedical_count = ProgramOutcome.objects.filter(program='biomedical').count()
    computer_count = ProgramOutcome.objects.filter(program='computer').count()
    total_count = biomedical_count + computer_count
    
    context = {
        'biomedical_count': biomedical_count,
        'computer_count': computer_count,
        'total_count': total_count,
    }
    return render(request, 'admin/outcomes/dekan_dashboard.html', context)