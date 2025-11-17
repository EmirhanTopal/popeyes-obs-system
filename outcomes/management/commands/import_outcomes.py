import os
import docx
import re
from django.core.management.base import BaseCommand
from outcomes.models import ProgramOutcome

class OutcomeImporter:
    @staticmethod
    def extract_number_from_text(text):
        """Metinden outcome numarasını çıkar"""
        match = re.match(r'^(\d+)[\s\-\.]', text.strip())
        if match:
            return int(match.group(1))
        return None
    
    @staticmethod
    def clean_description(text):
        """Açıklamayı temizle"""
        cleaned = re.sub(r'^\d+[\s\-\.]*', '', text.strip())
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    @staticmethod
    def detect_program_type(file_path):
        """Dosya içeriğine göre program tipini otomatik algıla"""
        try:
            doc = docx.Document(file_path)
            content = " ".join([p.text for p in doc.paragraphs[:5]])  # İlk 5 paragraf
            
            if 'biyomedikal' in content.lower() or 'biomedical' in content.lower():
                return 'biomedical'
            elif 'bilgisayar' in content.lower() or 'computer' in content.lower():
                return 'computer'
            else:
                # İçerik analizi ile otomatik tespit
                biomedical_keywords = ['tıp', 'medikal', 'sağlık', 'cihaz', 'sistem']
                computer_keywords = ['yazılım', 'donanım', 'programlama', 'bilişim', 'yazılım']
                
                biomedical_score = sum(1 for keyword in biomedical_keywords if keyword in content.lower())
                computer_score = sum(1 for keyword in computer_keywords if keyword in content.lower())
                
                if biomedical_score > computer_score:
                    return 'biomedical'
                else:
                    return 'computer'
                    
        except Exception as e:
            print(f"Program tipi algılanırken hata: {e}")
            return None
    
    @staticmethod
    def parse_docx_file(file_path, program_type=None):
        """Docx dosyasını parse et - program tipi otomatik veya manuel"""
        if not program_type:
            program_type = OutcomeImporter.detect_program_type(file_path)
        
        outcomes = []
        try:
            doc = docx.Document(file_path)
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text and any(char.isdigit() for char in text[:10]):
                    outcome_num = OutcomeImporter.extract_number_from_text(text)
                    if outcome_num:
                        description = OutcomeImporter.clean_description(text)
                        outcomes.append({
                            'number': outcome_num,
                            'description': description
                        })
            
            return outcomes, program_type
        except Exception as e:
            print(f"Dosya okunurken hata: {e}")
            return [], None

class Command(BaseCommand):
    help = 'YÖK Program Outcomes larını otomatik içe aktar'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--files',
            nargs='+',
            type=str,
            help='Docx dosya yolları (örn: --files "file1.docx" "file2.docx")'
        )
        parser.add_argument(
            '--biomedical',
            type=str,
            help='Biyomedikal docx dosya yolu'
        )
        parser.add_argument(
            '--computer',
            type=str, 
            help='Bilgisayar Mühendisliği docx dosya yolu'
        )
        parser.add_argument(
            '--auto-detect',
            action='store_true',
            help='Dosya içeriğinden program tipini otomatik algıla'
        )
    
    def handle(self, *args, **options):
        importer = OutcomeImporter()
        processed_files = 0
        
        # 1. Eski yöntem (geriye dönük uyumluluk)
        if options['biomedical'] and os.path.exists(options['biomedical']):
            self.import_single_file(importer, options['biomedical'], 'biomedical')
            processed_files += 1
            
        if options['computer'] and os.path.exists(options['computer']):
            self.import_single_file(importer, options['computer'], 'computer')
            processed_files += 1
        
        # 2. Yeni yöntem - çoklu dosya ve otomatik algılama
        if options['files']:
            for file_path in options['files']:
                if os.path.exists(file_path):
                    program_type = None
                    if options['auto_detect']:
                        program_type = importer.detect_program_type(file_path)
                        self.stdout.write(f"{file_path} → {program_type} olarak algılandı")
                    
                    self.import_single_file(importer, file_path, program_type)
                    processed_files += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Dosya bulunamadı: {file_path}")
                    )
        
        if processed_files == 0:
            self.stdout.write(
                self.style.WARNING('Hiç dosya işlenmedi. Kullanım:')
            )
            self.stdout.write('python manage.py import_outcomes --files "dosya1.docx" "dosya2.docx" --auto-detect')
            self.stdout.write('VEYA')
            self.stdout.write('python manage.py import_outcomes --biomedical "bio.docx" --computer "comp.docx"')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'{processed_files} dosya başarıyla işlendi!')
            )
    
    def import_single_file(self, importer, file_path, program_type=None):
        """Tek bir dosyayı import et"""
        try:
            outcomes, detected_program = importer.parse_docx_file(file_path, program_type)
            
            if not detected_program:
                self.stdout.write(
                    self.style.ERROR(f'Program tipi algılanamadı: {file_path}')
                )
                return
            
            self.stdout.write(f'{file_path} → {detected_program} outcomes import ediliyor...')
            
            for outcome in outcomes:
                ProgramOutcome.objects.update_or_create(
                    program=detected_program,
                    outcome_number=outcome['number'],
                    defaults={'description': outcome['description']}
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{detected_program} Outcome {outcome['number']} eklendi/güncellendi"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'{file_path} işlenirken hata: {e}')
            )