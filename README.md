# Multi-Threaded TCP Port Scanner

Standart Python kütüphaneleri kullanılarak geliştirilmiş, yüksek performanslı ve eşzamanlı (multi-threaded) TCP port tarama aracı. Güvenlik testleri, ağ envanter tespiti ve açık servis analizi süreçlerinde hızlı sonuç üretmek amacıyla tasarlanmıştır.

---

## 📐 Proje Mimarisi ve Özellikler

Bu araç, ek bir 3. taraf kütüphane bağımlılığı (PyPI packages) olmadan **tamamen Python 3 standart kütüphaneleri** üzerine inşa edilmiştir.

### Core Özellikler
* **Yüksek Başarım (Concurrency):** `concurrent.futures.ThreadPoolExecutor` havuzu ile ayarlanabilir sayıda iş parçacığı (`max_workers`) üzerinden eşzamanlı soket bağlantıları kurulur.
* **TCP Bağlantı Kontrolü:** `socket.socket(socket.AF_INET, socket.SOCK_STREAM)` ve `sock.connect_ex()` metodolojisi ile hedef port üzerinde TCP 3'lü el sıkışma (3-way handshake) durumu sınanır (`0` dönen durumlar `OPEN` kabul edilir).
* **Esnek Port Ayrıştırma (`parse_ports`):** Tekil portlar (`80,443`), port aralıkları (`8000-8010`) veya bunların kombinasyonları dinamik olarak işlenir.
* **Akıllı Varsayılan Port Listesi:** Port seçeneği verilmediğinde en çok kullanılan 22 kritik servis portu (`21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 10000`) otomatik olarak taranır.
* **Thread-Safe Çıktı Yönetimi:** `threading.Lock` nesnesi ile konsol çıktılarının ve açık port verilerinin çakışmasız eşzamanlı güncellenmesi sağlanır.
* **Yumuşak Kapanma (Graceful Shutdown):** Kullanıcı `Ctrl+C` (KeyboardInterrupt) verdiğinde işlem anında kesilir ve tarayıcı güvenli şekilde sonlanır.
* **ANSI Terminal Renklendirmesi:** Görsel takibi kolaylaştırmak için açık (`OPEN` - Yeşil) ve kapalı (`CLOSED` - Kırmızı) portlar renk kodlarıyla ayrıştırılır.
* **Zaman Formatlama (`human_readable_duration`):** Taramaların toplam çalışma süresi hesaplanarak insan tarafından kolay okunabilir biçimde (`Xh Ym Zs` / `Xs`) raporlanır.

---

## ⚙️ Komut Satırı Argümanları (CLI)

`argparse` modülü ile sağlanan parametreler ve varsayılan değerleri aşağıda listelenmiştir:

| Parametre | Kısa Ad | Tip | Varsayılan | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `host` | - | `string` | *(Zorunlu)* | Hedef IP adresi veya hostname (Örn: `127.0.0.1`, `scanme.nmap.org`) |
| `--ports` | `-p` | `string` | *Ortak Portlar* | Virgülle ayrılmış port listesi ve/veya aralığı (Örn: `80,443,8000-8010`) |
| `--timeout` | `-t` | `float` | `0.5` | Bağlantı denemesi için zaman aşımı süresi (saniye cinsinden) |
| `--workers` | `-w` | `int` | `100` | Eşzamanlı çalışacak maksimum thread (iş parçacığı) sayısı |

---

## 🚀 Kullanım Örnekleri

### 1. Yardım Menüsünü Görüntüleme
```bash
python port_scanner.py -h
```

### 2. Varsayılan Port Listesi ile Hızlı Tarama
Hedef IP veya alan adı verilerek varsayılan 22 port üzerinde tarama yapılır:
```bash
python port_scanner.py 127.0.0.1
```

### 3. Belirli Portlar ve Port Aralıkları İle Tarama
Virgül ve tire sembolleri kullanılarak özel port listesi tanımlanabilir:
```bash
python port_scanner.py scanme.nmap.org -p 80,443,8000-8010
```

### 4. Geniş Port Aralığı, Özel Timeout ve Thread Sayısı İle Tarama
Hassas zaman aşımı (0.2sn) ve 200 eşzamanlı thread ile 1-1024 arası port taraması:
```bash
python port_scanner.py 192.168.1.1 -p 1-1024 -t 0.2 -w 200
```

---

## 🖥️ Örnek Ekran Çıktısı

```text
  ____            _   _                 _   
 |  _ \ ___  __ _| |_| |__   ___   ___ | |_ 
 | |_) / _ \/ _` | __| '_ \ / _ \ / _ \| __|
 |  __/  __/ (_| | |_| | | | (_) | (_) | |_ 
 |_|   \___|\__,_|\__|_| |_|\___/ \___/ \__|
                                            

Scanning 127.0.0.1 for 22 ports (timeout=0.5s)…

[CLOSED] Port 21
[CLOSED] Port 22
[OPEN]   Port 80
[CLOSED] Port 443
[OPEN]   Port 8080
...

============================================================
Scan completed in 0.52s
Total ports scanned : 22
Open ports          : 2
Open ports list    : 80, 8080
============================================================
```

---

## 🛠️ Gereksinimler & Derleme

* **Python Sürümü:** Python 3.8+ (herhangi bir standart Python 3 sürümü)
* **Bağımlılıklar:** Herhangi bir dış bağımlılık bulunmamaktadır (Zero External Dependencies).

---

## ⚠️ Yasal ve Etik Uyarı (Legal Disclaimer)

> **ÖNEMLİ UYARI:**  
> Bu yazılım yalnızca **yetkili sistemlerde sızma testi (penetrasyon testi)**, **ağ güvenlik denetimleri** ve **eğitim/araştırma amaçlarıyla** kullanılmak üzere tasarlanmıştır.  
> 
> Yazılı izin alınmaksızın üçüncü taraf sistemlere veya ağlara karşı gerçekleştirilen port taramaları ve güvenlik analizleri yasalara aykırı olabilir ve ciddi hukuki yaptırımlar doğurabilir. Kullanıcı, bu aracı çalıştırdığı hedef sistemler üzerinde gerekli yetkiye sahip olduğunu kabul eder. Geliştirici, aracın kötüye kullanımından doğabilecek zararlardan sorumlu tutulamaz.
