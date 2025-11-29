from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import ProgramOutcome
from .management.commands.import_outcomes import OutcomeImporter


class DocumentUploadForm(forms.Form):
    program_type = forms.ChoiceField(
        choices=[('auto', 'Otomatik Algıla'), ('biomedical', 'Biyomedikal'), ('computer', 'Bilgisayar')],
        label='Program Tipi'
    )
    docx_file = forms.FileField(label='DOCX Dosyası Yükle')


@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "description", "department")
    list_filter = ("department",)
    search_fields = ("code", "description")



    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-docx/', self.admin_site.admin_view(self.upload_docx), name='outcomes_upload_docx'),
        ]
        return custom_urls + urls

    def upload_docx(self, request):
        if request.method == 'POST':
            form = DocumentUploadForm(request.POST, request.FILES)
            if form.is_valid():
                docx_file = request.FILES['docx_file']
                program_type = form.cleaned_data['program_type']

                # Geçici dosyaya kaydet
                import tempfile
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
                import os
                os.unlink(tmp_path)

                return HttpResponseRedirect('../')
        else:
            form = DocumentUploadForm()

        context = {
            'form': form,
            'title': 'DOCX Dosyası Yükle',
        }
        return render(request, 'templates/dean/upload_form.html', context)

    def program_display(self, obj):
        """Program adını daha güzel göster"""
        return obj.get_program_display()

    program_display.short_description = 'Program'

    def description_short(self, obj):
        """Liste görünümünde kısa açıklama"""
        return obj.description[:80] + '...' if len(obj.description) > 80 else obj.description

    description_short.short_description='Açıklama'