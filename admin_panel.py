import os
import json
import unicodedata
import re
import sys
import subprocess
import readline  # For better input handling

# --- Configuration ---
PORTFOLIO_METADATA_FILE = 'data/portfolioItems.json'
PORTFOLIO_DIR = 'portfolio'
DATA_DIR = 'data'

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- Helpers ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def slugify(text):
    text = text.lower()
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        ' ': '-', '.': '', ',': '', '!': '', '?': '', ':': '', ';': '',
        '\'': '', '"': '', '(': '', ')': '', '[': '', ']': ''
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[-\s]+', '-', text).strip('-_')
    return text

def load_json(filepath):
    try:
        if not os.path.exists(filepath):
            return {} if not filepath.endswith('Items.json') and not filepath.endswith('publications.json') else []
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.FAIL}JSON yükleme hatası ({filepath}): {e}{Colors.ENDC}")
        return {} if not filepath.endswith('Items.json') and not filepath.endswith('publications.json') else []

def save_json(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{Colors.FAIL}JSON kaydetme hatası ({filepath}): {e}{Colors.ENDC}")
        return False

def get_input(prompt_text, default=None):
    """Gets input with an optional default value."""
    if default is not None:
        user_input = input(f"{Colors.BLUE}{prompt_text} [{default}]: {Colors.ENDC}")
        return user_input.strip() if user_input.strip() else default
    else:
        return input(f"{Colors.BLUE}{prompt_text}: {Colors.ENDC}").strip()

def get_multiline_input(prompt_text, default=None):
    print(f"{Colors.BLUE}{prompt_text} (Girişi tamamlamak için üst üste iki kez ENTER'a basın):{Colors.ENDC}")
    if default:
        print(f"{Colors.WARNING}Mevcut Değer: {default}{Colors.ENDC}")
    
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    
    content = "\n".join(lines).strip()
    return content if content else default

def confirm_action(prompt_text):
    response = input(f"{Colors.WARNING}{prompt_text} (e/h): {Colors.ENDC}").lower()
    return response == 'e' or response == 'y'

def select_language():
    print(f"\n{Colors.BOLD}Dil Seçimi / Language Selection:{Colors.ENDC}")
    print("1. İngilizce (English)")
    print("2. Türkçe (Turkish)")
    choice = get_input("Seçiminiz / Choice", default="1")
    return "en" if choice == "1" else "tr"

def get_localized_path(filename, lang):
    if lang == "en":
        return os.path.join(DATA_DIR, filename)
    else:
        return os.path.join(DATA_DIR, "tr", filename)

def trigger_rebuild():
    if confirm_action("Değişikliklerin yansıması için siteyi derlemek (build) ister misiniz?"):
        print(f"\n{Colors.HEADER}--- SİTE DERLENİYOR ---{Colors.ENDC}")
        subprocess.run([sys.executable, "build.py"])

# --- Content Manager Base ---
class BaseContentManager:
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.data = load_json(self.metadata_file)

    def reload(self):
        self.data = load_json(self.metadata_file)

    def save(self):
        return save_json(self.metadata_file, self.data)

# --- Portfolio Manager ---
class PortfolioManager(BaseContentManager):
    def __init__(self):
        super().__init__(PORTFOLIO_METADATA_FILE)

    def menu(self):
        while True:
            print(f"\n{Colors.BOLD}--- Portfolyo Yönetimi ---{Colors.ENDC}")
            print("1. Projeleri Listele")
            print("2. Yeni Proje Ekle")
            print("3. Proje Düzenle (Meta Veri)")
            print("4. Proje Sil")
            print("5. Geri")
            choice = get_input("Seçiminiz").strip()
            if choice == '1':
                self.list_items()
            elif choice == '2':
                self.create()
                trigger_rebuild()
            elif choice == '3':
                self.update()
                trigger_rebuild()
            elif choice == '4':
                self.delete()
                trigger_rebuild()
            elif choice == '5':
                break

    def list_items(self):
        self.reload()
        print(f"\n{Colors.HEADER}--- MEVCUT PROJELER ---{Colors.ENDC}")
        if not self.data:
            print("Kayıtlı proje bulunamadı.")
            return False
        for idx, item in enumerate(self.data):
            print(f"{Colors.BOLD}{idx + 1}.{Colors.ENDC} {item.get('title', 'Başlıksız')} ({item.get('slug', 'slug-yok')})")
        return True

    def create(self):
        print(f"\n{Colors.HEADER}--- YENİ PROJE EKLEME ---{Colors.ENDC}")
        title = get_input("Proje Adı")
        if not title: return

        description = get_input("Kısa Açıklama")
        tech = get_input("Kullanılan Teknolojiler (örn: Python, OpenCV)")
        slug = slugify(title)
        image_url = get_input("Görsel Yolu", default="images/icon.png")
        
        filename = os.path.join(PORTFOLIO_DIR, f"{slug}.md")

        links = []
        while True:
            label = get_input("Link Etiketi (örn: GitHub, Canlı Demo - Bitirmek için boş bırakın)")
            if not label:
                break
            url = get_input(f"{label} URL'si")
            if url:
                links.append({"label": label, "url": url})

        new_entry = {
            "title": title,
            "imageUrl": image_url,
            "description": description,
            "techStack": tech,
            "detailFile": filename,
            "slug": slug,
            "links": links
        }

        self.data.insert(0, new_entry)
        if self.save():
            # Create the detail markdown file
            os.makedirs(PORTFOLIO_DIR, exist_ok=True)
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\nProje detaylarını buraya markdown formatında yazabilirsiniz...")
                print(f"{Colors.GREEN}✓ Proje başarıyla eklendi ve {filename} oluşturuldu.{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}Markdown dosyası oluşturulamadı: {e}{Colors.ENDC}")

    def update(self):
        if not self.list_items(): return
        try:
            choice = int(get_input("Düzenlemek istediğiniz projenin numarası")) - 1
            if 0 <= choice < len(self.data):
                item = self.data[choice]
                print(f"\n{Colors.HEADER}--- PROJE DÜZENLEME: {item['title']} ---{Colors.ENDC}")
                item['title'] = get_input("Proje Adı", item['title'])
                item['description'] = get_input("Kısa Açıklama", item.get('description', ''))
                item['techStack'] = get_input("Kullanılan Teknolojiler", item.get('techStack', ''))
                item['imageUrl'] = get_input("Görsel Yolu", item['imageUrl'])
                
                # Links update
                if confirm_action("Mevcut linkleri yeniden düzenlemek ister misiniz?"):
                    links = []
                    while True:
                        label = get_input("Link Etiketi (örn: GitHub - Bitirmek için boş bırakın)")
                        if not label:
                            break
                        url = get_input(f"{label} URL'si")
                        if url:
                            links.append({"label": label, "url": url})
                    item['links'] = links

                if self.save():
                    print(f"{Colors.GREEN}✓ Proje meta verileri güncellendi.{Colors.ENDC}")
                    print(f"{Colors.BLUE}Markdown içeriğini düzenlemek için şu dosyayı açabilirsiniz: {item['detailFile']}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Geçersiz numara.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")

    def delete(self):
        if not self.list_items(): return
        try:
            choice = int(get_input("Silmek istediğiniz projenin numarası")) - 1
            if 0 <= choice < len(self.data):
                item = self.data[choice]
                if confirm_action(f"'{item['title']}' projesini ve ilgili markdown dosyasını silmek istediğinize emin misiniz?"):
                    file_path = item.get('detailFile')
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"{Colors.GREEN}✓ {file_path} silindi.{Colors.ENDC}")
                        except OSError as e:
                            print(f"{Colors.FAIL}Dosya silinirken hata: {e}{Colors.ENDC}")
                    
                    del self.data[choice]
                    if self.save():
                        print(f"{Colors.GREEN}✓ Proje kaydı portfolyodan silindi.{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Geçersiz numara.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")

# --- CV Manager ---
class CVManager:
    def menu(self):
        lang = select_language()
        cv_file = get_localized_path('cvData.json', lang)
        data = load_json(cv_file)
        
        # Ensure schema structure exists
        if "$schema" not in data:
            data["$schema"] = "./schemas/cv-schema.json" if lang == "en" else "../schemas/cv-schema.json"

        while True:
            print(f"\n{Colors.BOLD}--- CV Düzenleme Paneli ({lang.upper()}) ---{Colors.ENDC}")
            print("1. Kişisel Bilgileri Düzenle (İsim, Ünvan, Resim)")
            print("2. Profesyonel Özet (Summary) Düzenle")
            print("3. Yetenekleri (Skills) Yönet")
            print("4. İş Deneyimlerini (Experiences) Yönet")
            print("5. Eğitim Bilgilerini (Education) Yönet")
            print("6. Dilleri (Languages) Yönet")
            print("7. Referansları (References) Yönet")
            print("8. Geri")
            
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                personal = data.get('personalInfo', {})
                personal['firstName'] = get_input("Ad", personal.get('firstName', ''))
                personal['lastName'] = get_input("Soyad", personal.get('lastName', ''))
                personal['title'] = get_input("Ünvan (Title)", personal.get('title', ''))
                personal['profileImage'] = get_input("Profil Resmi Yolu", personal.get('profileImage', 'images/profile.png'))
                data['personalInfo'] = personal
                save_json(cv_file, data)
                print(f"{Colors.GREEN}✓ Kişisel bilgiler güncellendi.{Colors.ENDC}")
                trigger_rebuild()
            
            elif choice == '2':
                data['professionalSummary'] = get_multiline_input("Profesyonel Özet", data.get('professionalSummary', ''))
                save_json(cv_file, data)
                print(f"{Colors.GREEN}✓ Profesyonel özet güncellendi.{Colors.ENDC}")
                trigger_rebuild()
                
            elif choice == '3':
                self.manage_skills(cv_file, data)
                trigger_rebuild()
                
            elif choice == '4':
                self.manage_experiences(cv_file, data)
                trigger_rebuild()
                
            elif choice == '5':
                self.manage_education(cv_file, data)
                trigger_rebuild()
                
            elif choice == '6':
                self.manage_languages(cv_file, data)
                trigger_rebuild()
                
            elif choice == '7':
                self.manage_references(cv_file, data)
                trigger_rebuild()
                
            elif choice == '8':
                break

    def manage_skills(self, file_path, data):
        skills = data.get('skills', [])
        while True:
            print(f"\n{Colors.BOLD}--- Yetenek Kategorileri ---{Colors.ENDC}")
            for idx, cat in enumerate(skills):
                print(f"  {idx+1}. {cat.get('category')}: {', '.join(cat.get('skill_list', []))}")
            
            print("\n1. Yeni Yetenek Kategorisi Ekle")
            print("2. Yetenek Kategorisi Sil")
            print("3. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                cat_name = get_input("Kategori Adı (örn: Programlama Dilleri)")
                if cat_name:
                    skill_list = []
                    while True:
                        skill = get_input("Yetenek (Bitirmek için boş bırakın)")
                        if not skill: break
                        skill_list.append(skill)
                    skills.append({"category": cat_name, "skill_list": skill_list})
                    data['skills'] = skills
                    save_json(file_path, data)
                    print(f"{Colors.GREEN}✓ Kategori eklendi.{Colors.ENDC}")
            elif choice == '2':
                try:
                    num = int(get_input("Silmek istediğiniz kategori numarası")) - 1
                    if 0 <= num < len(skills):
                        if confirm_action(f"'{skills[num]['category']}' kategorisini silmek istediğinize emin misiniz?"):
                            del skills[num]
                            data['skills'] = skills
                            save_json(file_path, data)
                            print(f"{Colors.GREEN}✓ Kategori silindi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '3':
                break

    def manage_experiences(self, file_path, data):
        experiences = data.get('experiences', [])
        while True:
            print(f"\n{Colors.BOLD}--- İş Deneyimleri ---{Colors.ENDC}")
            for idx, exp in enumerate(experiences):
                print(f"  {idx+1}. {exp.get('title')} - {exp.get('company')} ({exp.get('startDate')} - {exp.get('endDate')})")
            
            print("\n1. Yeni Deneyim Ekle")
            print("2. Deneyim Düzenle")
            print("3. Deneyim Sil")
            print("4. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                title = get_input("İş Ünvanı")
                company = get_input("Şirket Adı")
                start = get_input("Başlangıç Tarihi (AA/YYYY)")
                end = get_input("Bitiş Tarihi (AA/YYYY veya Devam)")
                
                desc_list = []
                print("Açıklama maddelerini girin (Bitirmek için boş bırakın):")
                while True:
                    bullet = get_input("Madde")
                    if not bullet: break
                    desc_list.append(bullet)
                    
                experiences.append({
                    "title": title,
                    "company": company,
                    "startDate": start,
                    "endDate": end,
                    "description": desc_list
                })
                data['experiences'] = experiences
                save_json(file_path, data)
                print(f"{Colors.GREEN}✓ Deneyim eklendi.{Colors.ENDC}")
                
            elif choice == '2':
                try:
                    num = int(get_input("Düzenlemek istediğiniz deneyim numarası")) - 1
                    if 0 <= num < len(experiences):
                        exp = experiences[num]
                        exp['title'] = get_input("İş Ünvanı", exp.get('title', ''))
                        exp['company'] = get_input("Şirket Adı", exp.get('company', ''))
                        exp['startDate'] = get_input("Başlangıç Tarihi", exp.get('startDate', ''))
                        exp['endDate'] = get_input("Bitiş Tarihi", exp.get('endDate', ''))
                        
                        # Bullet points
                        desc = exp.get('description', [])
                        if isinstance(desc, str): desc = [desc]
                        
                        print("\nMevcut Açıklama Maddeleri:")
                        for d_idx, d_val in enumerate(desc):
                            print(f"  - {d_val}")
                        if confirm_action("Maddeleri yeniden yazmak ister misiniz?"):
                            desc_list = []
                            while True:
                                bullet = get_input("Madde (Bitirmek için boş bırakın)")
                                if not bullet: break
                                desc_list.append(bullet)
                            exp['description'] = desc_list
                        
                        experiences[num] = exp
                        data['experiences'] = experiences
                        save_json(file_path, data)
                        print(f"{Colors.GREEN}✓ Deneyim güncellendi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
                    
            elif choice == '3':
                try:
                    num = int(get_input("Silmek istediğiniz deneyim numarası")) - 1
                    if 0 <= num < len(experiences):
                        if confirm_action(f"'{experiences[num]['title']}' deneyimini silmek istediğinize emin misiniz?"):
                            del experiences[num]
                            data['experiences'] = experiences
                            save_json(file_path, data)
                            print(f"{Colors.GREEN}✓ Deneyim silindi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '4':
                break

    def manage_education(self, file_path, data):
        education = data.get('education', [])
        while True:
            print(f"\n{Colors.BOLD}--- Eğitim Geçmişi ---{Colors.ENDC}")
            for idx, edu in enumerate(education):
                print(f"  {idx+1}. {edu.get('degree')} in {edu.get('field')} - {edu.get('institution')} ({edu.get('startYear')} - {edu.get('endYear')})")
            
            print("\n1. Yeni Eğitim Ekle")
            print("2. Eğitim Düzenle")
            print("3. Eğitim Sil")
            print("4. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                degree = get_input("Derece (örn: Lisans, Bachelor of Science)")
                field = get_input("Bölüm (örn: Bilişim Sistemleri)")
                inst = get_input("Kurum/Üniversite")
                start = get_input("Başlangıç Yılı (AA/YYYY veya YYYY)")
                end = get_input("Bitiş Yılı (AA/YYYY veya YYYY)")
                gpa = get_input("Not Ortalaması (GNO / GPA - boş bırakabilirsiniz)")
                
                education.append({
                    "degree": degree,
                    "field": field,
                    "institution": inst,
                    "startYear": start,
                    "endYear": end,
                    "gpa": gpa
                })
                data['education'] = education
                save_json(file_path, data)
                print(f"{Colors.GREEN}✓ Eğitim bilgisi eklendi.{Colors.ENDC}")
                
            elif choice == '2':
                try:
                    num = int(get_input("Düzenlemek istediğiniz eğitim numarası")) - 1
                    if 0 <= num < len(education):
                        edu = education[num]
                        edu['degree'] = get_input("Derece", edu.get('degree', ''))
                        edu['field'] = get_input("Bölüm", edu.get('field', ''))
                        edu['institution'] = get_input("Kurum", edu.get('institution', ''))
                        edu['startYear'] = get_input("Başlangıç Tarihi", edu.get('startYear', ''))
                        edu['endYear'] = get_input("Bitiş Tarihi", edu.get('endYear', ''))
                        edu['gpa'] = get_input("Not Ortalaması", edu.get('gpa', ''))
                        
                        education[num] = edu
                        data['education'] = education
                        save_json(file_path, data)
                        print(f"{Colors.GREEN}✓ Eğitim bilgisi güncellendi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
                    
            elif choice == '3':
                try:
                    num = int(get_input("Silmek istediğiniz eğitim numarası")) - 1
                    if 0 <= num < len(education):
                        if confirm_action(f"'{education[num]['institution']}' eğitim kaydını silmek istediğinize emin misiniz?"):
                            del education[num]
                            data['education'] = education
                            save_json(file_path, data)
                            print(f"{Colors.GREEN}✓ Eğitim bilgisi silindi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '4':
                break

    def manage_languages(self, file_path, data):
        langs = data.get('languages', [])
        while True:
            print(f"\n{Colors.BOLD}--- Dil Bilgisi ---{Colors.ENDC}")
            for idx, l in enumerate(langs):
                print(f"  {idx+1}. {l.get('language')}: {l.get('level')}")
            
            print("\n1. Yeni Dil Ekle")
            print("2. Dil Sil")
            print("3. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                name = get_input("Dil Adı (örn: İngilizce)")
                lvl = get_input("Seviye (örn: Orta Seviye, Intermediate, Native)")
                if name and lvl:
                    langs.append({"language": name, "level": lvl})
                    data['languages'] = langs
                    save_json(file_path, data)
                    print(f"{Colors.GREEN}✓ Dil bilgisi eklendi.{Colors.ENDC}")
            elif choice == '2':
                try:
                    num = int(get_input("Silmek istediğiniz dil numarası")) - 1
                    if 0 <= num < len(langs):
                        del langs[num]
                        data['languages'] = langs
                        save_json(file_path, data)
                        print(f"{Colors.GREEN}✓ Dil bilgisi silindi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '3':
                break

    def manage_references(self, file_path, data):
        refs = data.get('references', [])
        while True:
            print(f"\n{Colors.BOLD}--- Referanslar ---{Colors.ENDC}")
            for idx, ref in enumerate(refs):
                print(f"  {idx+1}. {ref.get('name')} - {ref.get('title')} ({ref.get('company')})")
            
            print("\n1. Yeni Referans Ekle")
            print("2. Referans Düzenle")
            print("3. Referans Sil")
            print("4. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                name = get_input("Ad Soyad")
                title = get_input("Ünvan")
                company = get_input("Kurum/Şirket")
                email = get_input("E-posta")
                phone = get_input("Telefon (İsteğe bağlı)")
                
                refs.append({
                    "name": name,
                    "title": title,
                    "company": company,
                    "email": email,
                    "phone": phone
                })
                data['references'] = refs
                save_json(file_path, data)
                print(f"{Colors.GREEN}✓ Referans eklendi.{Colors.ENDC}")
                
            elif choice == '2':
                try:
                    num = int(get_input("Düzenlemek istediğiniz referans numarası")) - 1
                    if 0 <= num < len(refs):
                        ref = refs[num]
                        ref['name'] = get_input("Ad Soyad", ref.get('name', ''))
                        ref['title'] = get_input("Ünvan", ref.get('title', ''))
                        ref['company'] = get_input("Kurum/Şirket", ref.get('company', ''))
                        ref['email'] = get_input("E-posta", ref.get('email', ''))
                        ref['phone'] = get_input("Telefon", ref.get('phone', ''))
                        
                        refs[num] = ref
                        data['references'] = refs
                        save_json(file_path, data)
                        print(f"{Colors.GREEN}✓ Referans güncellendi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
                    
            elif choice == '3':
                try:
                    num = int(get_input("Silmek istediğiniz referans numarası")) - 1
                    if 0 <= num < len(refs):
                        if confirm_action(f"'{refs[num]['name']}' referansını silmek istediğinize emin misiniz?"):
                            del refs[num]
                            data['references'] = refs
                            save_json(file_path, data)
                            print(f"{Colors.GREEN}✓ Referans silindi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '4':
                break

# --- Page Managers ---
class PageManager:
    @staticmethod
    def edit_about():
        lang = select_language()
        about_file = get_localized_path('aboutPageData.json', lang)
        data = load_json(about_file)
        
        print(f"\n{Colors.HEADER}--- HAKKIMDA SAYFASI DÜZENLEME ({lang.upper()}) ---{Colors.ENDC}")
        data['title'] = get_input("Sayfa Başlığı", data.get('title', 'Who Am I?'))
        data['profileImageUrl'] = get_input("Profil Resmi Görsel Yolu", data.get('profileImageUrl', 'images/profile.png'))
        data['content'] = get_multiline_input("Hakkımda Metni", data.get('content', ''))
        
        if save_json(about_file, data):
            print(f"{Colors.GREEN}✓ Hakkımda sayfası içeriği başarıyla güncellendi.{Colors.ENDC}")
            trigger_rebuild()

    @staticmethod
    def edit_contact():
        lang = select_language()
        contact_file = get_localized_path('contactPageData.json', lang)
        data = load_json(contact_file)
        
        print(f"\n{Colors.HEADER}--- İLETİŞİM SAYFASI DÜZENLEME ({lang.upper()}) ---{Colors.ENDC}")
        data['title'] = get_input("Sayfa Başlığı", data.get('title', 'Contact'))
        data['introText'] = get_input("Giriş Metni", data.get('introText', ''))
        data['otherContactMethodsTitle'] = get_input("Diğer İletişim Yolları Başlığı", data.get('otherContactMethodsTitle', 'Contact Me'))
        
        if save_json(contact_file, data):
            print(f"{Colors.GREEN}✓ İletişim sayfası içeriği başarıyla güncellendi.{Colors.ENDC}")
            trigger_rebuild()

# --- Social Manager ---
class SocialManager:
    @staticmethod
    def menu():
        social_file = os.path.join(DATA_DIR, 'socialLinks.json')
        data = load_json(social_file)
        
        # Ensure schema structure exists
        if "$schema" not in data:
            data["$schema"] = "./schemas/social-schema.json"

        while True:
            print(f"\n{Colors.BOLD}--- Sosyal Medya & İletişim Linkleri ---{Colors.ENDC}")
            print(f"E-posta: {data.get('email')}")
            print(f"Kişisel Web Sitesi: {data.get('website', {}).get('url')} ({data.get('website', {}).get('display')})")
            print(f"Kayıtlı Profil Link Sayısı: {len(data.get('links', []))}")
            
            print("\n1. Genel Bilgileri Düzenle (E-posta, Web Sitesi)")
            print("2. Profil Linklerini Yönet (GitHub, LinkedIn vb.)")
            print("3. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                data['email'] = get_input("E-posta Adresi", data.get('email', ''))
                website = data.get('website', {})
                website['url'] = get_input("Kişisel Web Sitesi URL'si", website.get('url', ''))
                website['display'] = get_input("Web Sitesi Görüntüleme Adı", website.get('display', ''))
                data['website'] = website
                save_json(social_file, data)
                print(f"{Colors.GREEN}✓ Genel iletişim bilgileri güncellendi.{Colors.ENDC}")
                trigger_rebuild()
                
            elif choice == '2':
                SocialManager.manage_profile_links(social_file, data)
                trigger_rebuild()
                
            elif choice == '3':
                break

    @staticmethod
    def manage_profile_links(file_path, data):
        links = data.get('links', [])
        while True:
            print(f"\n{Colors.BOLD}--- Profil Bağlantıları ---{Colors.ENDC}")
            for idx, link in enumerate(links):
                print(f"  {idx+1}. {link.get('platform')}: {link.get('url')} ({link.get('display')})")
            
            print("\n1. Yeni Profil Ekle")
            print("2. Profil Sil")
            print("3. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                platform = get_input("Platform İsmi (örn: GitHub, LinkedIn)")
                url = get_input("Profil URL'si")
                display = get_input("Görüntüleme Metni (örn: github.com/kullanici)")
                
                if platform and url and display:
                    # Check if platform is ORCID or DergiPark to use images
                    is_img = confirm_action("Bu platform için SVG yerine ikon görseli kullanılsın mı? (örn: ORCID/DergiPark için)")
                    new_link = {
                        "platform": platform,
                        "url": url,
                        "display": display
                    }
                    if is_img:
                        new_link["isImg"] = True
                        new_link["imgUrl"] = get_input("Görsel URL'si (imgUrl)")
                    else:
                        new_link["svgCircle"] = confirm_action("SVG arkaplan dairesi çizilsin mi (svgCircle)?")
                        new_link["svgPath"] = get_input("SVG Path Verisi (svgPath)")
                    
                    links.append(new_link)
                    data['links'] = links
                    save_json(file_path, data)
                    print(f"{Colors.GREEN}✓ Profil linki eklendi.{Colors.ENDC}")
                    
            elif choice == '2':
                try:
                    num = int(get_input("Silmek istediğiniz profil link numarası")) - 1
                    if 0 <= num < len(links):
                        del links[num]
                        data['links'] = links
                        save_json(file_path, data)
                        print(f"{Colors.GREEN}✓ Profil linki silindi.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '3':
                break

# --- Publications Manager ---
class PublicationsManager:
    @staticmethod
    def menu():
        pub_file = os.path.join(DATA_DIR, 'publications.json')
        data = load_json(pub_file)
        if not isinstance(data, list):
            data = []

        while True:
            print(f"\n{Colors.BOLD}--- Akademik Yayın Linkleri Yönetimi ---{Colors.ENDC}")
            print("Kayıtlı yayın linkleri:")
            for idx, url in enumerate(data):
                print(f"  {idx+1}. {url}")
            
            print("\n1. Yeni Yayın Bağlantısı Ekle (DOI veya arXiv linki)")
            print("2. Yayın Bağlantısı Sil")
            print("3. Geri")
            choice = get_input("Seçiminiz").strip()
            
            if choice == '1':
                url = get_input("Yayın URL'si (örn: https://doi.org/... veya https://arxiv.org/abs/...)")
                if url:
                    if url not in data:
                        data.append(url)
                        if save_json(pub_file, data):
                            print(f"{Colors.GREEN}✓ Yayın linki başarıyla eklendi. Metadata derleme sırasında otomatik çekilecektir.{Colors.ENDC}")
                            trigger_rebuild()
                    else:
                        print(f"{Colors.WARNING}Bu yayın linki zaten kayıtlı.{Colors.ENDC}")
            elif choice == '2':
                try:
                    num = int(get_input("Silmek istediğiniz yayın bağlantısının numarası")) - 1
                    if 0 <= num < len(data):
                        if confirm_action(f"'{data[num]}' bağlantısını silmek istediğinize emin misiniz?"):
                            del data[num]
                            if save_json(pub_file, data):
                                print(f"{Colors.GREEN}✓ Yayın bağlantısı silindi.{Colors.ENDC}")
                                trigger_rebuild()
                except ValueError:
                    print(f"{Colors.FAIL}Geçersiz giriş.{Colors.ENDC}")
            elif choice == '3':
                break

# --- Dev Server Runner ---
def start_dev_server():
    print(f"\n{Colors.HEADER}--- GELİŞTİRİCİ SUNUCUSU (FLASK) BAŞLATILIYOR ---{Colors.ENDC}")
    print("Sunucuyu durdurmak için CTRL+C tuşlarına basın.")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nGeliştirici sunucusu durduruldu.")

# --- Main Application Menu ---
def main_menu():
    portfolio_mgr = PortfolioManager()
    cv_mgr = CVManager()

    while True:
        print(f"\n{Colors.BOLD}{Colors.HEADER}=== N4YuC4 Web Sitesi & CV Yönetim Paneli ==={Colors.ENDC}")
        print("1. Portfolyo Öğelerini Yönet (Projeler)")
        print("2. CV Bilgilerini Düzenle (Kişisel Bilgiler, Yetenekler, İş, Eğitim...)")
        print("3. Hakkımda Sayfasını Güncelle")
        print("4. İletişim Sayfasını Güncelle")
        print("5. Sosyal Medya & İletişim Linklerini Yönet")
        print("6. Akademik Yayın Bağlantılarını (Publications) Yönet")
        print("7. Web Sitesini Derle (Build)")
        print("8. Geliştirici Sunucusunu Çalıştır (Flask)")
        print("9. Çıkış")
        
        choice = get_input("Seçiminiz").strip()
        
        if choice == '1':
            portfolio_mgr.menu()
        elif choice == '2':
            cv_mgr.menu()
        elif choice == '3':
            PageManager.edit_about()
        elif choice == '4':
            PageManager.edit_contact()
        elif choice == '5':
            SocialManager.menu()
        elif choice == '6':
            PublicationsManager.menu()
        elif choice == '7':
            print(f"\n{Colors.HEADER}--- SİTE DERLENİYOR (BUILD) ---{Colors.ENDC}")
            subprocess.run([sys.executable, "build.py"])
        elif choice == '8':
            start_dev_server()
        elif choice == '9':
            print("Yönetim panelinden çıkılıyor. İyi çalışmalar!")
            break
        else:
            print(f"{Colors.FAIL}Geçersiz seçim. Lütfen listedeki numaralardan birini girin.{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor...")