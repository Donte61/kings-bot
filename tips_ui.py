import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class TipsUI:
    def __init__(self, parent, license_active, base_font_size, colors):
        self.parent = parent
        self.license_active = license_active
        self.base_font_size = base_font_size
        self.colors = colors
        self.tips_window = None
        self.setup_ui()

    def setup_ui(self):
        if not self.license_active:
            return
        # Toplevel penceresi oluştur
        self.tips_window = tk.Toplevel(self.parent)
        self.tips_window.title("Kingshot Etkinlik ve Strateji İpuçları")
        self.tips_window.geometry("800x600")  # Daha büyük pencere boyutu
        self.tips_window.configure(bg=self.colors['background'])
        self.tips_window.resizable(True, True)
        # Pencereyi ekranın ortasına yerleştir
        self.tips_window.update_idletasks()
        x = self.tips_window.winfo_screenwidth() // 2 - self.tips_window.winfo_width() // 2
        y = self.tips_window.winfo_screenheight() // 2 - self.tips_window.winfo_height() // 2
        self.tips_window.geometry(f"+{x}+{y}")
        self.tips_window.withdraw()  # Başlangıçta pencereyi gizle

        # Başlık
        ttk.Label(self.tips_window, text="Kingshot Etkinlik ve Strateji İpuçları", font=("Helvetica", self.base_font_size + 4, "bold"), background=self.colors['background'], foreground=self.colors['accent']).pack(pady=10, anchor="w")

        # ScrolledText widget'ı
        tips_text = ScrolledText(self.tips_window, height=30, state="normal", bg=self.colors['background'], fg=self.colors['text'], font=("Consolas", self.base_font_size - 1), relief="solid", bd=1)
        tips_text.pack(pady=5, fill="both", expand=True)

        # Renkli başlıklar için etiketler tanımla
        tips_text.tag_configure("main_heading", font=("Helvetica", self.base_font_size + 2, "bold"), foreground=self.colors['accent'])
        tips_text.tag_configure("sub_heading", font=("Helvetica", self.base_font_size, "bold"), foreground=self.colors['text'])
        tips_text.tag_configure("sub_sub_heading", font=("Helvetica", self.base_font_size - 1, "bold"), foreground=self.colors['text'])

        # Belge içeriği
        tips_content = """
Stratejik Etkinlik Katılımı: Fırsatları Yakalamak

Kutsal Alan Savaşları: İttifak Savaşında Üstünlük
Kutsal Alan Savaşları, krallık büyümesi için önemli ödüller sunan haftalık bir ittifak savaşı etkinliğidir. Uzun vadeli başarı için bu savaşlar çok önemlidir, çünkü tutarlı katılım kaynak ve güç sıralamasında avantajlara yol açar.

Mekanikler ve Haftalık Program:
- İttifak Kayıt Aşaması: Bir ittifakın R4 veya R5 üyeleri, belirlenen bir pencere sırasında kayıt olmalıdır.
- Zaman Dilimi Oylaması: Üyeler, katılımı en üst düzeye çıkarmak için tercih edilen savaş zamanlarına oy verir.
- Savaş Yürütme: İttifaklar ya saldırgan ralliler düzenler ya da savunma stratejilerini koordine eder.
- Kontrol Süresi Takibi: Puanlar, ittifakın Kutsal Alan'ın kontrolünü ne kadar süreyle sürdürdüğüne göre birikir.
- Ödül Dağıtımı: Hem katılım hem de zafer ödülleri, savaş tamamlandıktan sonra dağıtılır.

Bu savaşlar her hafta düzenli olarak gerçekleşir, ancak belirli zamanlamalar oyun güncellemeleriyle değişebilir, bu da oyun içi duyuruların dikkatle takip edilmesini gerektirir. 2025 sezon yapısı 8 aşamalı bir döngüdür; tek bir haftayı kaçırmak, bir ittifakı tüm sezon boyunca dezavantajlı duruma düşürebilir.

Kayıt ve İttifak Koordinasyon Stratejileri:
Sadece R4 ve R5 görevlileri bir ittifakı Kutsal Alan Savaşları için kaydedebilir, ancak otomatik kayıt da etkinleştirilebilir. Bu sorumluluk, üye uygunluğunu, rakip ittifakların tipik aktivite modellerini ve farklı zaman dilimlerindeki ittifak gücünü dikkate almayı gerektirir. İttifaklar, zaman dilimi seçimi için geçmiş verileri analiz etmeli ve direnç seviyelerini takip etmelidir. Hafta ortası savaşları daha düşük katılım oranları göstererek potansiyel olarak daha kolay zaferler sunabilir.

Etkili koordinasyon, net iletişim kanalları gerektirir: anlık taktiksel ayarlamalar için oyun içi ittifak sohbeti, savaş öncesi strateji oturumları için Discord/Line ve rol atamaları ile toplanma noktaları için paylaşılan belgeler. Kritik anlarda tereddütü önlemek için önceden net karar verme kriterleri (ne zaman kaynak ayırılacağı veya stratejik olarak geri çekileceği) belirlenmelidir.

Savaş Taktikleri: Hareket (Yürüyüşe Geçme vs. Işınlanma), Ralli Koordinasyonu, Kaynak Planlaması:
- Hareket Stratejisi: Yürüyüşe geçme ve ışınlanma arasındaki seçim, savaş sonuçlarını önemli ölçüde etkiler.
  - Yürüyüşe Geçme: Kaynak açısından verimli, rota ortasında yönlendirmeye izin verir, gerçek sayıları maskeleyebilir. Dezavantajları: Daha yavaş varış, engellemeye karşı savunmasız, niyetleri belli eder.
  - Işınlanma: Anında konumlanma, sürpriz faktörü, azaltılmış savunmasızlık. Dezavantajları: Işınlanma eşyaları tüketir, konuma bağlılık, kullanımdan sonra sınırlı esneklik.
  - Genellikle en etkili yaklaşım, ana kuvvet liderlerini ışınlarken, destekleyici birlikleri katmanlı varış süreleri oluşturarak savunucuları alt etmek için yürüyüşe geçirmektir.
- Ralli Koordinasyonu: Başarılı ralliler hassas zamanlama ve net liderlik gerektirir. Birincil ve ikincil ralli liderleri güç ve ekipmanlarına göre belirlenmeli, kesin fırlatma zamanları geri sayım koordinasyonu ile ayarlanmalı, genel gücü tamamlamak için belirli birlik kompozisyonları atanmalı ve savaş ortası ayarlamalar için iletişim protokolleri oluşturulmalıdır. Senkronize üçlü ralliler, iyi savunulan Kutsal Alanlara karşı en yüksek başarı oranını göstermiştir, ancak bu önemli ittifak koordinasyonu gerektirir.
- Kaynak Planlaması: Doğru hazırlık, kötü performansı önler. Beklenen savaşlardan birkaç gün önce birlikler eğitilmeli, iyileştirme kuyrukları ve revir kapasitesi sürekli savaş için korunmalı ve hızlandırma eşyaları acil takviyeler için stoklanmalıdır. Zaman kısıtlı olduğunda, Kingshot cevherleri hızlı eğitim veya iyileşme için kritik bir avantaj sağlayabilir.

Ödül Optimizasyonu ve Sezon Puanları Psikolojisi:
Kutsal Alan Savaşları ikili ödül yapıları sunar:
- Anında Ödüller: Sonuçtan bağımsız olarak katılım için kaynak paketleri, Kutsal Alan'ı kontrol etme karşılığında hızlandırmalar ve materyaller, performans metriklerine dayalı ittifak hediyeleri.
- Uzun Vadeli Faydalar: Sezon sonu sıralamaları için biriken sezon puanları, en iyi performans gösterenler için prestijli ekipman ve özel kozmetikler, diplomatik ilişkileri etkileyen ittifak itibarı.

Bu sistem, anında ödüllerle kısa vadeli tatmin ihtiyaçlarını karşılayarak sürekli katılımı teşvik ederken, sezon puanları daha büyük gelecekteki ödüller için beklenti oluşturur. Ödülleri en üst düzeye çıkarmak için, zaferin olası görünmediği durumlarda bile tutarlı katılım çok önemlidir, çünkü katılım ödüllerinin kümülatif değeri genellikle ara sıra kazanılan zaferlerin artan faydasını aşar. Rekabetçi ittifaklar için, Kingshot cevherlerinin stratejik yatırımı belirleyici avantajlar yaratabilir, çünkü zafer ödüllerinden elde edilen yatırım getirisi genellikle akıllıca kaynak harcamasını haklı çıkarır.

Bu haftalık ritim, Kutsal Alan Savaşlarını izole olaylardan sürekli, sezon boyu süren bir stratejik kampanyaya dönüştürür. İttifakları sadece tek bir savaş için değil, devam eden rekabet için sürdürülebilir planlama ve koordinasyon mekanizmaları geliştirmeye zorlar. Anında ve uzun vadeli ödül yapısı bu durumu psikolojik olarak pekiştirir, oyuncuların bireysel zaferler elde edilemese bile tutarlı bir şekilde katılmaya motive olmalarını sağlar. Hazırlanma, koordine olma ve hafta be hafta performans gösterme konusundaki bu sürekli baskı, ittifak dinamiklerinin, kaynak yönetiminin ve oyunculuk devamlılığının temel itici gücüdür.

Çukur (Ayı Avı): Hasarı ve Ödülleri En Üst Düzeye Çıkarma
Ayı Avı, ittifakların "asla ölmeyen bir Ayı'ya" saldırdığı bir etkinliktir. Verilen hasar ne kadar yüksek olursa, kişisel ve ittifak ödülleri de o kadar yüksek olur. Ödüller arasında dövme çekiçleri, ittifak puanları ve kaynaklar bulunur. Bu etkinlikte her şey, mümkün olan en fazla hasarı vermeye odaklıdır.

Optimal Ralli Kompozisyonu ve Kahraman Seçimi:
- Ralli Liderleri: En yüksek Şehir Merkezi seviyesine sahip oyuncular, ralli kapasitesini en üst düzeye çıkarmak için rallileri başlatmalıdır. Genellikle en iyi kahramanlara sahiptirler; ralli liderinden gelen 6-9 sefer becerisinin tamamı uygulanır.
- Ralli Katılımcıları: Chenko veya Amadeus'u ilk kahraman yuvasına yerleştirerek %25 hasar bonuslarının (Chenko'dan gelen ölümcüllük takviyesi) uygulanmasını sağlamak önemlidir. Ralliye katılan kahramanlardan yalnızca en yüksek seviyeli 4 kahramanın ilk becerileri ralli gücüne eklenir. Chenko/Amadeus mevcut değilse, diğer oyunculardan gelen değerli becerileri engellememek için hiçbir kahraman gönderilmemelidir.
- Birlik Kompozisyonu: Okçular en fazla hasarı verir ve Ayı Çukuru'nda hasar alınmadığı için sağlık önemli değildir. Bu nedenle Okçular en üst düzeye çıkarılmalıdır. Kalan boşluk Süvarilerle, eğer hala boşluk varsa Piyadelerle doldurulmalıdır.

Zamanlama ve Koordinasyon İpuçları:
- Etkinliğin son 25 dakikasında tam bir rallinin canavara hasar verdiğinden emin olunmalıdır.
- "Hız her şey değildir — Ralli stratejisinde hassasiyet önemlidir." Doğru kahramanları ve birlikleri göndermek için yavaşlamak, acele etmekten daha etkilidir.
- Düşük seviyeli piyadeler göndermekten kaçınılmalıdır, çünkü bunlar daha güçlü birimlerle doldurulabilecek yuvaları işgal eder.
- Ayı tuzakları kullanılmalıdır.

Ayı Avı etkinliği, basit bir "ayıya saldırma" gibi görünse de, kahraman beceri uygulaması (yalnızca ilk 4 katılımcı becerisi, Chenko/Amadeus gibi belirli kahraman önceliği) ve birlik kompozisyonu (sağlık önemsiz olduğu için maksimum okçular) için özel mekaniklere sahiptir. Ayrıca, "hız" yerine "hassasiyet" ve "kişisel ödül" ile "toplam ittifak ödülü" için hasarı en üst düzeye çıkarma vurgulanır. Bu etkinlik, bir ittifakın üyelerinin katkılarını koordine etme ve optimize etme yeteneği için mükemmel bir eğitim alanı ve test görevi görür. Kahraman sinerjisinin (ölümcüllük takviyelerini yığma), akıllı birlik konuşlandırmasının (dayanıklılık yerine hasar) ve disiplinli ralli katılımının önemini vurgular. Ayı Avı'ndaki başarı, sadece bireysel güçle ilgili değil, belirli, yüksek etkili stratejilerin kolektif olarak anlaşılması ve uygulanmasıyla ilgilidir, bu da bir ittifakın genel stratejik olgunluğunun ve iletişim etkinliğinin önemli bir göstergesidir.

Diğer Önemli Etkinlikler ve Görevler

Mistik Kehanet: Jeton Ekonomisi ve Stratejisi:
Oyuncular, dört mevcut seçenekten (genellikle Dövme Çekiçleri, Vali Tılsım Malzemeleri, Cevherler, Hızlandırmalar veya Kahraman XP'si) "Dilek Ödülü"nü seçerler. Gizli ödülü bulmak için "Şans Jetonları" kullanarak kartları çevirirler. Jetonlar Günlük Görevler (günde yaklaşık 22 jeton), Ücretsiz Günlük Jeton veya Şans Jetonu Paketleri aracılığıyla elde edilebilir. Kart çevirme maliyetleri artar (1, 2, 3, 4, 6, 8, 12, 15, 20, 25 jeton, tüm 10 çevirme için toplam 96 jeton). Kilometre taşı ödülleri (örneğin, 100, 250, 750 çevirmede) Dövme Çekiçleri ve Genel Hızlandırmalar gibi ek değer sunar.

Strateji:
- Ücretsiz oynayan oyuncular, jetonları etkinlikler arasında biriktirebilir, yüksek değerli ödüllere (Dövme Çekiçleri, Tılsım Malzemeleri) odaklanabilir ve yüksek maliyetlerden kaçınmak için 6-8 çevirmeden sonra sıfırlayabilirler.
- Orta düzey harcama yapanlar, tam temizlemeleri ve kilometre taşı ödüllerini hedeflemelidir. 3-4 çevirmeden sonra sıfırlamaktan kaçınılmalıdır.
- Şans Jetonları, etkinlik bittikten sonra sırt çantasında kalır ve biriktirilmesine olanak tanır.

Büyüme Görevleri: Hızlandırılmış İlerleme ve Ödüller:
Bunlar, her gün yeni görevlerin kilidini açan 5 günlük belirli görev setleridir. Kahramanları işe alma, binaları yükseltme/inşa etme, Bastır aşamalarına ulaşma gibi basit görevler için zengin kaynaklar ve premium para birimi sağlarlar. Tüm 5 günlük görevleri tamamlamak, SR nadirliğinde bir kahraman olan Chenko'yu ödüllendirir.

Günlük Görevler ve İstihbarat Görevleri: Tutarlı Kazançlar:
Günlük görevler, sürekli bir kaynak ve XP akışı sağlar. İstihbarat Görevleri (Gözetleme Kulesi görevleri olarak da adlandırılır) kaynaklarda ve kahraman parçalarında iyi ödüller verir. PvP savaşları da önemli kaynak kazançları sağlayabilir.

Kingshot'taki etkinlikler, sadece isteğe bağlı yan içerikler değil, temel ilerleme sistemine derinlemesine entegre edilmişlerdir. Oyuncuların uzun vadeli büyüme ve rekabetçilik için kritik olan temel kaynakları, kahramanları ve hızlandırmaları edinmeleri için yapılandırılmış yollar sağlarlar. Bu etkinlikleri ihmal etmek, önemli ölçüde daha yavaş ilerleme anlamına gelir ve zamanla önemli bir güç farkı yaratır. Bu durum, harcama alışkanlıklarından bağımsız olarak tüm oyuncular için tutarlı katılımı stratejik bir zorunluluk haline getirir. Tasarım, günlük girişleri ve çeşitli oyun yönlerinde katılımı teşvik eder.

Birlik Yönetimi ve Savaş Ustalığı: Ordunuzu Oluşturma

Birlik Türlerini ve Rollerini Anlama
Kingshot'taki savaş sistemi, her birinin kendine özgü bir rolü, konumu ve etkileşimi olan üç ana birlik türüne dayanır. Bu birliklerin özelliklerini ve birbirleriyle olan ilişkilerini anlamak, etkili savaş stratejileri oluşturmanın temelini oluşturur.

Birlik Türleri ve Diziliş:
- Piyade: Birincil hasar emiciler olarak ön saflarda konumlandırılırlar. Mızraklılara %10 ek hasar verir ve Mızraklılara karşı savunmayı %10 artırırlar. En yüksek zayiat oranına sahiptirler.
- Süvari (Mızraklılar): Mobil birimler olarak orta safta konumlandırılırlar. Güvenli bir şekilde hasar verirler, öncelikli olarak düşman Piyadelerini ve Okçularını hedeflerler. En düşük zayiat oranına ve en yüksek öldürme sayısına sahiptirler. Koruma için Piyadelere güvenirler ve bazen düşman Okçularına doğrudan saldırmak için becerilerini etkinleştirebilirler.
- Okçu (Nişancılar): En yüksek tek hedef hasarını sağlarlar ve arka saflarda konumlandırılırlar. Düşman Piyadelerine saldırırlar, ancak çıktıları Piyadelerin engellemesiyle sınırlıdır. Yüksek hasara sahip olsalar da, düşük öldürme sayılarına sahiptirler ve düşman Mızraklıları tarafından hızla ortadan kaldırılabilir. Koruma için Piyadelere güvenirler.

Birlik Türleri Özeti:
- Piyade: Hasar Emici, Ön Sıra, Güçlü Yönler: Yüksek Savunma, Mızraklılara Karşı Etkili, Zayıf Yönler: Düşük Hasar Çıkışı, Yüksek Zayiat Oranı, Ana Etkileşim: Mızraklıları Yener
- Süvari: Mobil Hasar, Orta Sıra, Güçlü Yönler: Düşük Zayiat, Yüksek Öldürme Sayısı, Okçuları Hedefleyebilir, Zayıf Yönler: Piyade Korumasına Bağımlı, Ana Etkileşim: Nişancıları Yener
- Okçu: Menzilli Hasar, Arka Sıra, Güçlü Yönler: Yüksek Tek Hedef Hasarı, Zayıf Yönler: Düşük Sağlık, Mızraklılara Karşı Savunmasız, Ana Etkileşim: Piyadeleri Yener

Saldırı, Savunma ve Denge İçin Optimal Dizilişler ve Oranlar:
- Saldıran Dizilişi (%45 Piyade, %35 Süvari, %25 Okçu):
  - Artıları: Özellikle Süvari güçlendirici kahramanlarla düşman Piyadelerini kesmede üstündür. Okçular, arka safları hedefleyerek Süvarileri tamamlar.
  - Eksileri: Sınırlı tanklama kapasitesi, Piyadeler çökerse uzun süreli savaşlarda zorlanır.
- Savunan Dizilişi (%70 Piyade, %10 Süvari, %20 Okçu):
  - Artıları: Hasarı emmek için tasarlanmış büyük bir sağlık ve savunma duvarı oluşturur. Rakiplerden daha uzun süre dayanır.
  - Eksileri: Düşmanları hızlıca öldürme potansiyeli düşüktür, sürekli hasar veren yapılar veya ağır Okçu/kritik vuruş kahramanlarına karşı savunmasızdır.
- Dengeli Diziliş (%50 Piyade, %30 Süvari, %20 Okçu):
  - Artıları: Hasarı emmek için sağlam bir kalkan sağlar, Piyade ağırlıklı oluşumlara karşı önemli patlama hasarı, istikrarlı menzilli baskı. Çok yönlüdür.
  - Eksileri: Uzmanlaşmış oluşumların aşırı dayanıklılığına veya ham hasarına sahip değildir; ideal senaryolarda uzmanlaşmış yapılara karşı geride kalabilir.

Optimal Birlik Oluşumları Özeti:
- Saldıran: %45 Piyade, %35 Süvari, %25 Okçu, Ana Artıları: Hızlı Hasar, Piyade Kesme, Ana Eksileri: Düşük Dayanıklılık, Uzun Savaşlarda Zayıf, Önerilen Kullanım: Agresif Saldırılar, Hızlı Zaferler
- Savunan: %70 Piyade, %10 Süvari, %20 Okçu, Ana Artıları: Yüksek Dayanıklılık, Hasar Emme, Ana Eksileri: Düşük Hasar Çıkışı, Yavaş Öldürme, Önerilen Kullanım: Savunma, Kuşatma Savunması
- Dengeli: %50 Piyade, %30 Süvari, %20 Okçu, Ana Artıları: Çok Yönlü, Orta Hasar ve Savunma, Ana Eksileri: Uzmanlaşmış Oluşumların Aşırı Gücünden Yoksun, Önerilen Kullanım: Genel Amaçlı Savaşlar, Bilinmeyen Rakip

Savaş Öncesi Strateji:
Yeterli Piyade'nin hasarı emmesini sağlamak için farklı birim türü oranları seçilmelidir, bu da arka sıra birimlerinin hasar verme alanını artırır ve zafer şansını yükseltir. Birlik türlerinin rolleri (Piyade tank olarak, Süvari mobil hasar olarak, Okçu menzilli DPS olarak) ve konumları (ön, orta, arka) arasındaki net ayrımlar, Kingshot'un savaş sisteminde temel bir taş-kağıt-makas dinamiği oluşturur. Özellikle, hasar veren birimlerin "koruma için Piyadelere güvendiği" ve "sınıf karşıtlıkları"nın (Piyade Mızraklıyı yener, Mızraklı Nişancıyı yener, Nişancı Piyadeyi yener) varlığı, hiçbir birlik türünün evrensel olarak üstün olmadığını gösterir. Etkinlikleri, düşman kompozisyonuna ve kendi koruyucu katmanlarına (Piyade) büyük ölçüde bağlıdır. Bu, başarılı savaşın sadece yüksek güce sahip olmakla değil, aynı zamanda akıllı birlik kompozisyonu, düşman oluşumlarını anlama ve bu karşıt ilişkileri kullanma ile ilgili olduğu anlamına gelir. Bu aynı zamanda, optimal oluşumların statik olmadığını, belirli savaş senaryosuna (PvP'ye karşı PvE, saldırma veya savunma) göre uyarlanması gerektiğini de gösterir.

Kahraman Sinerjisi ve Konuşlandırma
Kahramanlar, Kingshot'taki ordunuzun bel kemiğidir ve savaş performansınızı önemli ölçüde etkileyen benzersiz becerilere ve rollere sahiptir.

Savaş Kahramanları ve Büyüme Kahramanları:
- Savaş Kahramanları: Savaş durumlarında üstündürler (örneğin, alan hasarı için Jeronimo, delici saldırılar için Molly).
- Büyüme Kahramanları: Verimliliğinizi artırırlar, genellikle kaynak toplama veya üretimle ilgilidirler (örneğin, odun/taş/demir toplama hızını veya kale çıktısını artıran kahramanlar).

Savaş ve Ralliler için Anahtar Kahramanlar:
- Chenko (Süvari): Saldıran rallilere katılmak için en önemli kahramandır. Sağ üst becerisi Ölümcüllüğü %25'e kadar artırır ve diğer Chenko'larla birleşerek etkiyi artırır.
- Gordon (Piyade): Savunma garnizonlarına katılmak için en önemli kahramandır. Becerileri bir ralli/garnizondaki herkese uygulanır.
- Diana (Okçu): Canavarlara ve Terörlere saldırmak için stamina tasarrufu sağlamada faydalıdır. Parçaları daha kolay elde edilebilir.
- Amadeus: Ralli katılımcıları için Chenko'ya benzer şekilde %25 hasar bonusu sağlar. Tüm birlikler için becerilere sahiptir, %50 bonus hasar tetikleme şansı da dahil.
- Hilda: Savunma kahramanıdır. Tüm birlikler için gelen hasarı %50 azaltma şansı %40'tır. Ayrıca tüm birliklerin saldırısını ve ölümcüllüğünü artırır.
- Marlin: Sefer modunda güçlüdür, özellikle ölümcüllük bonusuyla.
- Jabel: En iyi ücretsiz oynanabilen kahramandır.
- Howard (Piyade): Oynaması ücretsiz 1. nesil Piyade kahramanıdır.
- Quin (Okçu): Oynaması ücretsiz 1. nesil Nişancı kahramanıdır.

Kilit Kahramanlar Özeti:
- Chenko: Süvari, Ralli Hasar Takviyesi, Ölümcüllük Artışı (%25'e kadar), Saldıran rallilere katılırken ilk slotta kritik.
- Gordon: Piyade, Garnizon Savunması, Savunma Takviyesi (Tüm ralli/garnizon için), Savunma garnizonlarına katılırken önemli.
- Amadeus: Belirtilmemiş, Ralli Hasar Takviyesi, %50 Bonus Hasar Tetikleme Şansı, Chenko gibi ralli katılımcısı, PvE baskınlarında güçlü.
- Hilda: Belirtilmemiş, Savunma Kahramanı, Gelen Hasarı Azaltma (%50 şans %40), PvP savunması için iyi, tüm birliklere saldırı/ölümcüllük verir.
- Diana: Okçu, Stamina Tasarrufu, Stamina Maliyetini Azaltma, Canavar ve Terör avı için ideal, F2P dostu.
- Marlin: Belirtilmemiş, Sefer Modu Hasarı, Ölümcüllük Bonusu, Uzun vadeli PvE ve Arena için değerli.
- Jabel: Belirtilmemiş, Genel Kullanım, -, En iyi ücretsiz oynanabilen kahraman.
- Howard: Piyade, F2P Tank, Savunma Odaklı, Oynaması ücretsiz başlangıç Piyade tankı.
- Quin: Okçu, F2P Nişancı, Tek Hedef Hasarı, Oynaması ücretsiz başlangıç Okçu.

Kahraman Beceri Etkileşimi ve Maksimum Etki için Önceliklendirme:
Bir birlik bir kahraman içeriyorsa, sefer becerileri (bazıları olasılık tabanlıdır) eşleşen birlik türü olup olmadığına bakılmaksızın etkinleştirilir. Beceriler, savaş raporunda listelenen istatistiklerden bağımsız olarak işlev görür. Ralliler oluşturulurken, üç kahramanınızın da üç sağ becerisi kullanılır. Rallilere katılırken ise, yalnızca ilk kahramanınızın sağ üst becerisi uygulanır. Ralli, katılan kahramanlar arasında en yüksek seviyeli 4 kahramanın sağ üst becerisini kullanır. Uzun vadeli büyüme stratejisinde Piyade sağlığına ve Okçu ölümcüllüğüne öncelik verilmelidir. Kaynak toplayan kahramanlara, kaynak toplama yeteneklerini artıran ekipmanlar giydirilmelidir.

Kahramanların seviyelerini yükseltmek temel istatistiklerini (Saldırı, Savunma, Sağlık) doğrudan artırır; onları yükseltmek becerilerini geliştirir ve bazen yeni becerilerin kilidini açar; becerilerini yükseltmek ise faydalarını (hasar çarpanları, bekleme süreleri) artırır. Daha iyi sinerji için, becerileri birbirini tamamlayan kahramanlar eşleştirilmelidir. Seferde, takviyeleri en üst düzeye çıkarmak için kahramanların ilgili birlik türlerine (örneğin, Jeronimo Piyade ile) liderlik etmesi sağlanmalıdır.

Ralli ve Garnizon Kahraman Katkıları: İttifak Gücünü En Üst Düzeye Çıkarma:
- Ralli Savaşları: Ralli başlatıcısının 9 kahraman becerisine ek olarak, ralli üyelerinin 4 birincil kahraman becerisi (her kahramanın ilk becerisi) dahil edilir.
- Garnizon Savaşları: En yüksek istatistik bonuslarına sahip oyuncu, savunma bonuslarının kaynağı olarak seçilir. Ayrıca, diğer garnizon üyelerinden 4 birincil kahraman becerisi savaş için etkinleştirilir.
- Hasar odaklı rallilere katılırken, Chenko veya Amadeus olmayan kahramanlarla birlik göndermektense, kahramansız birlik göndermek daha iyidir.

Kahraman becerilerinin (örneğin, Chenko'nun ölümcüllük takviyesi, Amadeus'un hasarı, Gordon'ın savunması) ve rallilerdeki belirli uygulama kurallarının (katılımcılar için yalnızca ilk kahramanın sağ üst becerisi, en iyi 4 becerinin uygulanması) ayrıntılı dökümü, kahramanların sadece istatistik yığınları olmadığını vurgular. Benzersiz becerileri ve ralli mekaniğiyle nasıl etkileşime girdikleri çok önemlidir. Bu, etkili kahraman konuşlandırmasının sofistike bir güç çarpanı olduğu anlamına gelir. Sadece güçlü kahramanlara sahip olmak yeterli değildir; oyuncuların belirli etkinlik veya savaş senaryosuna (örneğin, Ayı Avı'na karşı PvP savunması) göre hangi kahramanları kullanacaklarını, nereye yerleştireceklerini (lider mi katılımcı mı, ilk slot) ve ne zaman konuşlandıracaklarını anlamaları gerekir. İttifak üyeleri arasında koordineli kahraman seçimi yoluyla belirli takviyelerin (Chenko'nun ölümcüllüğü gibi) biriktirilmesi yeteneği, önemli ölçüde daha yüksek kolektif hasar veya savunmaya doğrudan bir yoldur ve ham güç sayılarının ötesinde stratejik derinliği vurgular.

Gelişmiş Savaş Taktikleri
Kingshot'ta savaş, sadece düşmanları yenmekle kalmayıp, aynı zamanda kaynaklarınızı verimli bir şekilde yönetmek ve kayıpları en aza indirmekle ilgilidir.

Savaş Öncesi Strateji ve Hedef Seçimi:
- Birimler normalde önce düşmanın ön sırasına saldırır. Ön sıra ortadan kaldırıldıktan sonra bir sonraki sırayı hedeflerler.
- Süvariler bazen düşman Okçularına doğrudan arka sıradan saldırmak için becerilerini etkinleştirebilirler.
- Bazı kahraman becerileri tüm birimleri veya belirli birim türlerini hedefleyebilir.

Zayiatları En Aza İndirme ve Revir Yönetimi:
- Farklı savaş türleri değişen zayiat oranlarına sahiptir (ölü, ağır yaralı, hafif yaralı ve hayatta kalanlar).
- Diğer oyuncuların Şehir Merkezi'ne karşı yapılan savaşlarda, saldıranın zayiatlarının %35'i ölür.
- Kral Kalesi savaşlarında, tüm zayiatlar revir dolana kadar revire gider ve daha sonraki zayiatlar ölür.
- Kalıcı birlik kayıplarını önlemek için revir her zaman boş tutulmalıdır.
- Dünya Haritası'nda yaralı askerleri iyileştirmek artık tam ekran arayüz yerine bir açılır pencere açar.

PvP ve PvE'ye Özgü Yaklaşımlar (Arena, Bastır, Canavar Avı):
- Arena: Her gün oynanmalıdır, ancak sıralamada düşme şansını azaltmak için sıfırlamadan (00:00 UTC) önceki son 1-10 dakikada 10 saldırı yapılmalıdır. Tanklar ve destekçilerle birlikte ani hasar veren birimleri birleştirin. Jessie'nin sersemletmesi düşman rotasyonlarını kesintiye uğratır. Günlük görevlerle oluşumlar test edilmelidir; cevherler, yalnızca kesin galibiyetler için ek denemeler için ayrılmalıdır. Savaşlardan önce rakip dizilişlere dikkat edilmelidir. Önerilen bir arena oluşumu: Zoey, Amadeus, Hilda, Marlin ve Jabel.
- Bastır (PvE): 4. Bölüm görevlerinden sonra kilidi açılır. Oyuncuların düşman dalgalarına karşı 6 kahramana kadar konuşlandırabildiği sıra tabanlı bir moddur. İmparatorluğu genişletmek ve kaynak toplamak için kullanılır. Daha yüksek aşamalar daha fazla ödül verir. Alan hasarı veren kahramanları (Jeronimo) kitle kontrolü (Jessie) ve şifacılarla (Philly) birleştirin. Keşif becerileri yükseltilmeli ve yüksek ödüllü aşamalar için stamina saklanmalıdır. Kazançlı kaynaklar için Bastır aşamalarında daha ileriye gidilmelidir.
- Canavar Avı (Dünya Yaratıkları/Korkunç Kurtlar): Korkunç Kurtları çağırmak için dünya yaratıkları temizlenerek "başarı" kazanılmalıdır. Kahraman parçaları (Diana, Korkunç Kurt) elde etmek için Korkunç Kurtlara karşı kendi rallilerinizi düzenleyin. Dünya yaratıklarını temizleme ve Korkunç Kurtlara karşı ralli düzenleme arasında stamina kullanımını dengeleyin. Bonuslar için Diana veya başka bir kahraman liderliğinde otomatik ralliyi çevrimdışı ayarlayın. PvP/Canavar Avları: Kahramanları birlik türleriyle hizalayın; Gina'nın stamina azaltması sık rallilere yardımcı olur. Jeronimo harika bir ralli lideridir.

Zayiat oranlarının savaş türüne göre değiştiği, kalıcı kayıpları önlemek için revirin boş tutulması gerektiği ve "kazanamayacağınız savaşlardan kaçınma" tavsiyesi, savaşın sadece kazanmakla ilgili olmadığını, aynı zamanda verimli kazanmak ve kaynakları korumakla ilgili olduğunu gösterir. Bu, her savaşın aynı zamanda bir kaynak yönetimi kararı olduğu anlamına gelir. Oyuncular, potansiyel ödülleri, birlik zayiatı ve iyileşme süresi maliyetleriyle karşılaştırmalıdır. Yüksek zayiat oranları doğrudan kaynak tüketimine (yeni birlikler eğitmek ve iyileştirmek için) yol açar. Bu nedenle, stratejik savaş, sadece optimal oluşumlar ve kahraman seçimleriyle değil, aynı zamanda ne zaman saldırılacağını, ne zaman geri çekileceğini ve özellikle yüksek riskli PvP senaryolarında kayıpları nasıl en aza indireceğini bilmeyi de içerir. Oyun, en değerli varlıkları olan ordularının en az harcamayla hedeflere ulaşabilen oyuncuları açıkça ödüllendirir.

Gelişmiş İpuçları ve Uzun Vadeli Stratejiler: Üstünlük Kurmak

Verimli Kaynak Yönetimi: Temel Toplamanın Ötesinde
Kingshot'ta uzun vadeli başarı için kaynak yönetimi, temel toplamadan çok daha fazlasını içerir. Özellikle çiftlik hesaplarının kullanımı, ciddi oyuncular için oyunun meta-stratejisinin önemli bir parçası haline gelmiştir.

Çiftlik Hesapları: Kurulum, Yönetim ve Güvenli Kaynak Transferi:
- Ciddi oyuncular için en verimli uzun vadeli stratejilerden biridir.
- Kurulum: Farklı bir e-posta veya sosyal medya girişi kullanarak yeni bir Kingshot hesabı oluşturulur. Temel özelliklerin kilidini açmak için eğitim hızlıca tamamlanır. Kaynak üreten binalara ve araştırmalara odaklanılır. Üretim için gerekli olmayan savaş yükseltmeleri atlanır. Ana hesaba bağlanır.
- Genişleme: Bonus kaynaklar için günlük görevler tamamlanır. Kaynak üreten binalar genişletilir. Askerler öncelikli olarak kaynak taşıma kapasitesi için işe alınır. Kaynak odaklı etkinliklere katılım sağlanır. Saldırılardan kaçınmak için düşük profil korunur.
- Kaynak Transferi: Çiftlik hesabı ana hesabın yakınına ışınlanır. Kaynaklar birliklere yüklenir. Birlikler ana hesaba saldırmak için gönderilir. Kaynakların ana hesap tarafından "yağmalanması" için savaş kasten kaybedilir.
- Verimi En Üst Düzeye Çıkarma: Kaynak takviyesi etkinlikleri sırasında transferler zamanlanır. Ana hesabın yeterli depolama kapasitesine sahip olduğundan emin olunur. Kayıpları önlemek için çiftlik hesabında kaynak koruma eşyaları kullanılır. Kaynak üst sınırlarını önlemek için düzenli bir transfer programı sürdürülür.

Oyun, "çiftlik hesapları oluşturma ve yönetme"yi "ciddi oyuncular için en verimli uzun vadeli stratejilerden biri" olarak açıkça vurgular. Kurulum, genişletme ve kaynak transferi için kasıtlı kayıp gibi ayrıntılı adımlar, sofistike, oyuncu odaklı bir meta-oyunu gösterir. Bu, oyunun kaynak ekonomisinin, çoklu hesap yönetimini teşvik eden bir kıtlık derecesiyle tasarlandığı anlamına gelir. Çiftlik hesapları sadece bir "hile" değil, rekabetçi oyuncuların kaynak darboğazlarını aşmak ve hızlandırılmış ilerlemeyi sürdürmek için tanınmış ve neredeyse gerekli bir stratejidir. Bu durum, çiftlik hesaplarını kullanmayan oyuncuların doğal olarak daha yavaş ilerleyeceğini ve zamanla önemli bir güç farkı yaratacağını gösterir. Aynı zamanda, ittifakların üyeleri için çiftlik hesabı operasyonlarını koruyup kolaylaştırabileceği için ittifak koordinasyonunun önemini de vurgular.

Toplama Verimliliği için Araştırma ve Kahraman Önceliklendirme:
- Öncelikle Ekonomi araştırma ağacına odaklanılmalıdır, özellikle toplama hızını artıran düğümlere.
- Toplama odaklı becerilere sahip mavi kahramanlar işe alınmalı ve seviyeleri yükseltilmelidir.
- Toplama kahramanlarına, kaynak toplama yeteneklerini artıran ekipmanlar giydirilmelidir.
- Araştırma ve seviye ilerlemesi yoluyla 4 yürüyüş yuvasının tamamı hızla açılmalıdır. Tüm yürüyüş yuvaları her zaman kaynak toplamakla meşgul tutulmalıdır. Daha yüksek seviyeli kaynak düğümlerine öncelik verilmelidir. Sürekli toplama için yürüyüş zamanlamaları ayarlanmalıdır. Yürüyüş hızı takviyeleri kullanılmalıdır.

Akıllı Yatırım: Cevherler, VIP Seviyeleri ve Büyüme için Eşya Önceliklendirme
Kingshot'ta ilerlemeyi hızlandırmak ve rekabet avantajı elde etmek için premium para birimleri ve eşyaların akıllıca kullanılması çok önemlidir.

Cevherler: Premium Para Birimi Hileleri ve Stratejik Kullanım:
- Özel eşyalar ve daha hızlı ilerleme için premium para birimidir.
- Bina inşa etme, eğitim, araştırma hızlandırması, VIP seviyelerinin kilidini açma/yükseltme, nadir eşyalar satın alma ve ek etkinlik şansları elde etme için kullanılabilir.
- Haftalık Görev Kartı (haftalık 150 cevher), üst düzey loncalar (haftalık 50 cevher) ve sosyal medyayı bağlama (günlük 20 cevher) yoluyla kazanılır.
- Cevherler VIP seviyeleri ve önemli etkinlikler için saklanmalıdır.
- Stratejik satın almalar (İnşaat Paketi, Yürüyüş Kuyrukları, Haftalık/Aylık Paket) değerli olabilir.

VIP Seviyeleri: Faydaları ve Anahtar Kilometre Taşları:
- Kingshot cevherleri harcamak VIP seviyesini artırır.
- VIP Seviye 8, önemli faydalar sunar: daha hızlı yükseltmeler, ek bina kuyruğu, efsanevi parçalar. Seviye 8'den sonra yükseltme çok maliyetli hale gelir.
- Pasif takviyeler için VIP kilometre taşlarına ulaşmaya öncelik verilmelidir.

Tüm Aşamalar için Eşya Önceliklendirme:
- Başlangıç Odak Noktası: İkinci İnşaat Kuyruğu (aynı anda iki bina inşa etme), Temel Kahraman Ekipmanı, Kaynak Paketleri, Şehir Merkezi Yükseltmeleri, İttifak Eşyaları (ittifak paralarıyla ışınlayıcılar, hızlandırmalar).
- Orta Oyun Odak Noktası: Kahraman Parçaları (kahramanları yükseltmek için), Etkinlik Eşyaları (ekipman materyalleri, nadir kahramanlar için etkinlik para birimi kullanma), VIP Seviyeleri (seviye 8'e kadar).
- İleri Oyun Odak Noktası: Yüksek Seviyeli Ekipman (Efsanevi, Efsanevi), Dövme Çekiçleri, Tasarım Planları (ekipman üretimi/yükseltmesi için), Özel Takviyeler (önemli savaşlar için saklama), Nadir Kahraman Anahtarları (özel etkinlikler için), Kahraman Beceri Kitapları (kahraman becerilerini yükseltmek için).
- Kahraman ve üs yükseltmeleri arasında denge sağlanmalıdır. Sabırlı olunmalı ve etkinlikler/fırsatlar beklenmelidir.
- Yaygın materyaller: Dövme Çekiçleri (üretim), Kahraman Parçaları (kahramanların kilidini açma/yükseltme), Parşömenler (ekipman yükseltme/araştırma), Tasarım Planları (güçlü ekipmanların kilidini açma/yükseltme).

Cevherlerin "oyundaki en kullanışlı ve güçlü para birimi" olarak tanımlanması ve "daha hızlı ilerleme" ile ilişkilendirilmesi, kaynak tahsisinin kritik bir stratejik karar olduğunu gösterir. Ayrıca, eşya önceliklendirmesinin oyun aşamalarına göre (başlangıç, orta, ileri) ayrıntılı dökümü ve VIP seviyelerinin belirli faydaları, akıllı harcamanın sadece kaynak biriktirmekle ilgili olmadığını, aynı zamanda temel ilerleme darboğazlarını aşmak için bunları akıllıca dağıtmakla ilgili olduğunu gösterir. Örneğin, ikinci inşaat kuyruğuna erken öncelik vermek veya VIP 8'e ulaşmak, sonraki tüm büyümeyi hızlandıran bileşik faydalar sağlar. Sınırlı premium kaynakların (cevherler) ve yüksek değerli eşyaların bu stratejik tahsisi, verimli oyuncuları ayıran şeydir ve onlara dürtüsel veya net bir uzun vadeli plan olmadan harcama yapanlara karşı önemli bir avantaj sağlar.

Sürekli Gelişim: Savaş Raporlarından Öğrenme ve Stratejileri Uyarlama
Kingshot'ta üstünlük kurmak, sürekli bir öğrenme ve adaptasyon döngüsü gerektirir. Oyun dinamik bir ortamdır ve statik stratejiler eninde sonunda yetersiz kalacaktır.

"Yansıtma, Uyarlama ve Yeniden Giriş" iyi oyuncuların harika oyunculara dönüştüğü noktadır. Maç verileri analiz edilmeli, yanlış hamleler üzerinde düşünülmeli ve daha iyi bir strateji için yüklemeler veya şampiyonlar değiştirilmelidir. Savaş raporlarından öğrenmek, savaşta avantaj elde etmek için kritik öneme sahiptir. Birliklerin veya kaynakların kötü kararlar yüzünden boşa harcanmasından kaçınılmalıdır. Oluşumlar her zaman benzersiz durumlara uygun ideal kompozisyonlarla güncel tutulmalıdır. Oyun, her oynadığınızda ve düşmanlarınızı gözlemlediğinizde gelişir, bu da gözlem becerilerini ve refleksleri artırır.

"Yansıtma, uyarlama ve yeniden giriş" ve "savaş raporlarından öğrenme" gibi ifadeler, sürekli bir geri bildirim döngüsünü vurgular. Oyun statik değildir; yeni kahramanlar, etkinlikler ve oyuncu stratejileri ortaya çıkar. Bu durum, Kingshot'un dinamik bir stratejik ortam olduğunu gösterir. Statik stratejiler sonunda başarısız olacaktır. Gerçek ustalık, sürekli bir analiz (savaş raporları), eleştirel öz değerlendirme (yanlış hamleler) ve proaktif adaptasyon (oluşumları, kahramanları, yüklemeleri değiştirme) sürecinden gelir. Bu yinelemeli öğrenme ve iyileştirme döngüsü, uzun vadeli üstünlük için esastır, çünkü oyuncuların meta'nın önünde kalmalarını ve gelişen tehditlere karşı koymalarını sağlar. Bu, bu analitik sürece katılan oyuncuların, sabit yaklaşımlara güvenenlerden sürekli olarak daha iyi performans göstereceği anlamına gelir.

Sonuç: Kingshot'ta Hükmetme Yolunuz
Kingshot, strateji, yönetim ve bağlılık gerektiren eğlenceli ve heyecan verici bir oyundur. Başarı, verimlilik ve tutarlılığa bağlıdır – kaynaklar boşa harcanmamalıdır. Kingshot'ta ustalaşmak, üs geliştirme, kaynak edinimi, stratejik etkinlik katılımı ve akıllı savaşı dengelemek anlamına gelir. Oyun, analitik oyunu, sürekli öğrenmeyi ve uyarlanabilir stratejileri ödüllendirir. Bu detaylı bilgiler ve ipuçları uygulanarak, valiler ilerlemelerini önemli ölçüde hızlandırabilir, etkinliklerde üstünlük kurabilir ve Kingshot'un çalkantılı dünyasında hüküm sürebilirler.
"""

        # İçeriği ekle ve başlıkları biçimlendir
        lines = tips_content.split("\n")
        for line in lines:
            line = line.rstrip()
            if not line:
                tips_text.insert(tk.END, "\n")
                continue
            if line.startswith("Stratejik Etkinlik Katılımı") or line.startswith("Birlik Yönetimi ve Savaş Ustalığı") or line.startswith("Gelişmiş İpuçları ve Uzun Vadeli Stratejiler") or line.startswith("Sonuç:"):
                tips_text.insert(tk.END, line + "\n", "main_heading")
            elif line.startswith("Kutsal Alan Savaşları") or line.startswith("Çukur (Ayı Avı)") or line.startswith("Diğer Önemli Etkinlikler ve Görevler") or line.startswith("Birlik Türlerini ve Rollerini Anlama") or line.startswith("Kahraman Sinerjisi ve Konuşlandırma") or line.startswith("Gelişmiş Savaş Taktikleri") or line.startswith("Verimli Kaynak Yönetimi") or line.startswith("Toplama Verimliliği için Araştırma ve Kahraman Önceliklendirme") or line.startswith("Akıllı Yatırım") or line.startswith("Sürekli Gelişim"):
                tips_text.insert(tk.END, line + "\n", "sub_heading")
            elif line.startswith("Mekanikler ve Haftalık Program") or line.startswith("Kayıt ve İttifak Koordinasyon Stratejileri") or line.startswith("Savaş Taktikleri") or line.startswith("Ödül Optimizasyonu ve Sezon Puanları Psikolojisi") or line.startswith("Optimal Ralli Kompozisyonu ve Kahraman Seçimi") or line.startswith("Zamanlama ve Koordinasyon İpuçları") or line.startswith("Mistik Kehanet") or line.startswith("Büyüme Görevleri") or line.startswith("Günlük Görevler ve İstihbarat Görevleri") or line.startswith("Birlik Türleri ve Diziliş") or line.startswith("Saldırı, Savunma ve Denge İçin Optimal Dizilişler ve Oranlar") or line.startswith("Savaş Öncesi Strateji") or line.startswith("Savaş Kahramanları ve Büyüme Kahramanları") or line.startswith("Savaş ve Ralliler için Anahtar Kahramanlar") or line.startswith("Kahraman Beceri Etkileşimi ve Maksimum Etki için Önceliklendirme") or line.startswith("Ralli ve Garnizon Kahraman Katkıları") or line.startswith("Savaş Öncesi Strateji ve Hedef Seçimi") or line.startswith("Zayiatları En Aza İndirme ve Revir Yönetimi") or line.startswith("PvP ve PvE'ye Özgü Yaklaşımlar") or line.startswith("Çiftlik Hesapları") or line.startswith("Cevherler") or line.startswith("VIP Seviyeleri") or line.startswith("Tüm Aşamalar için Eşya Önceliklendirme"):
                tips_text.insert(tk.END, line + "\n", "sub_sub_heading")
            else:
                tips_text.insert(tk.END, line + "\n")
        
        tips_text.config(state="disabled")

    def show(self):
        if self.tips_window:
            self.tips_window.deiconify()
            self.tips_window.lift()

    def hide(self):
        if self.tips_window:
            self.tips_window.withdraw()