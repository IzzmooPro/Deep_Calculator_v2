# 🧮 Deep Calculator

**Sürüm:** 2.0.0  
**Geliştirici:** Izzmoo  
**İletişim:** IzzmooPro@gmail.com  
**Lisans:** Ücretsiz — kişisel ve ticari kullanım  

Windows 11 tasarım diline uygun, PyQt6 tabanlı masaüstü hesap makinesi.  
Türkçe sayı formatı (binlik nokta, ondalık virgül), bellek işlemleri,  
hesap geçmişi ve sistem teması algılama içerir.

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Gereksinimler](#-gereksinimler)
- [Kurulum](#-kurulum)
- [Çalıştırma](#-çalıştırma)
- [Proje Yapısı](#-proje-yapısı)
- [Mimari & İşleyiş](#-mimari--i̇şleyiş)
- [Modül Referansı](#-modül-referansı)
- [Klavye Kısayolları](#-klavye-kısayolları)
- [Tema Sistemi](#-tema-sistemi)
- [Bellek İşlemleri](#-bellek-i̇şlemleri)
- [Hesap Geçmişi](#-hesap-geçmişi)
- [Derleme (EXE)](#-derleme-exe)
- [Bilinen Sınırlar](#-bilinen-sınırlar)
- [Değişiklik Geçmişi](#-değişiklik-geçmişi)

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| **Dört işlem** | Toplama, çıkarma, çarpma, bölme |
| **Fonksiyonlar** | `1/x`, `x²`, `√x`, `%`, `+/-` |
| **Bellek** | MC, MR, M+, M−, MS (5'li bellek satırı) |
| **Hesap geçmişi** | Tüm işlemler listelenir, tıklanarak yüklenir |
| **Türkçe format** | `1.234.567,89` — binlik nokta, ondalık virgül |
| **Sistem teması** | Windows kayıt defterinden açık/koyu tema algılanır |
| **Tek instance** | Program zaten açıksa ikinci kopya açılmaz |
| **Klavye desteği** | Tüm işlemler klavyeyle yapılabilir |
| **Kopyala/Yapıştır** | Display sağ tık menüsü + Ctrl+C/V |
| **Şeffaflık** | 3 kademeli pencere saydamlığı |
| **AST güvenliği** | `eval()` yerine güvenli AST değerlendirmesi |

---

## 🔧 Gereksinimler

- **Python:** 3.10 veya üzeri
- **PyQt6:** 6.4.0 veya üzeri
- **İşletim Sistemi:** Windows 10/11 (tema algılama), macOS, Linux

```
PyQt6>=6.4.0
```

---

## 🚀 Kurulum

```bash
# 1. Depoyu klonla veya ZIP'i çıkar
cd Deep_Calculator_v2

# 2. Sanal ortam oluştur (önerilen)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## ▶️ Çalıştırma

```bash
python main.py
```

---

## 📁 Proje Yapısı

```
Deep_Calculator_v2/
│
├── main.py                  # Giriş noktası — tek instance + uygulama başlatma
├── main.spec                # PyInstaller derleme konfigürasyonu
├── requirements.txt         # Bağımlılık listesi
├── README.md                # Bu dosya
├── LICENSE                  # Lisans sözleşmesi
├── INSTALL.md               # Kurulum ve derleme rehberi
├── .gitignore               # Git tarafından takip edilmeyecek dosyalar
│
├── core/                    # İş mantığı katmanı (UI bağımlılığı YOK)
│   ├── __init__.py          # Katman public API'si
│   ├── constants.py         # Sabitler, OPS, FUNCTIONS, KEY_MAP, ALLOWED_NODES
│   ├── engine.py            # CalculatorEngine + CalculatorState
│   └── formatter.py         # Türkçe sayı formatlama fonksiyonları
│
├── ui/                      # Arayüz katmanı
│   ├── __init__.py          # Katman public API'si
│   ├── window.py            # CalculatorWindow — ana pencere
│   ├── grid_layout.py       # Buton ızgara tanımı (GRID listesi)
│   ├── theme.py             # ThemePalette, LIGHT, DARK, btn_style()
│   ├── widgets.py           # AnimatedButton (QPushButton subclass)
│   └── help_dialog.py       # Kullanım kılavuzu diyalogu
│
├── assets/                  # Uygulama kaynakları
│   ├── __init__.py          # Paket tanımı
│   ├── icon_data.py         # Base64 kodlu uygulama ikonları (açık/koyu)
│   └── README.md            # Assets klasörü notu
│
└── assets/                  # Uygulama kaynakları (yukarıda)
    ├── Kurulum_Öncesi.txt
    ├── Kurulum_Sonrası.txt
    └── Lisans_Dosyası.txt
```

---

## 🏗️ Mimari & İşleyiş

### Genel Akış

```
Kullanıcı (tuş/tıklama)
        │
        ▼
  CalculatorWindow._dispatch(token)
        │
        ▼
  CalculatorEngine.press(token)      ← saf iş mantığı, UI yok
        │
        ▼
  CalculatorState (dataclass)        ← anlık durum snapshotu
        │
        ▼
  CalculatorWindow._render(state)    ← state'e göre UI güncellenir
```

### Katman Ayrımı

Proje iki net katmandan oluşur:

- **`core/`** — UI'ya hiç bağımlı değil. Sadece Python standart kütüphanesi ve kendi modüllerini kullanır. Birim testi yazılabilir, UI değişse de core değişmez.
- **`ui/`** — PyQt6'ya bağımlı. `core`'dan `CalculatorEngine` ve `CalculatorState`'i alır, bunları ekranda gösterir.

### Durum Yönetimi

`CalculatorState` her buton basışında yeniden üretilir ve `_render()` metoduna iletilir. UI hiçbir zaman kendi içinde durum tutmaz — tüm gerçek durum engine'dedir.

```python
@dataclass
class CalculatorState:
    expression:       str        # Ekranda gösterilen ifade
    history:          str        # Üst satır (5 + 3 =)
    error:            str        # Hata mesajı (boşsa hata yok)
    just_evaluated:   bool       # = sonrası mı?
    full_expression:  str        # Zincir işlemler için tam ifade
    last_op:          str        # = tekrarı için son operatör
    last_operand:     str        # = tekrarı için son operand
    buttons_disabled: bool       # Hata sonrası operatör butonları kilitli
    memory:           float      # Bellek değeri
    memory_active:    bool       # M göstergesi görünür mü?
    history_log:      list[str]  # Tüm işlem geçmişi
```

### Güvenli Hesaplama (AST)

`eval()` kullanılmaz. Bunun yerine ifade Python AST'ye dönüştürülür ve sadece izin verilen node tipleri değerlendirilir:

```python
ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
)
```

Başka herhangi bir node (fonksiyon çağrısı, attribute erişimi, import vb.) `CalculationError` fırlatır.

### Türkçe Format Dönüşümü

İki yönlü dönüşüm vardır:

```
Görüntü (Türkçe)   →   Python ifadesi
────────────────────────────────────────
1.234,56           →   1234.56
1.234×5.678        →   1234*5678
5−3                →   5-3
10÷2               →   10/2
```

Bu dönüşüm `engine._to_py()` içinde yapılır; binlik noktalar her iki yanında rakam olan noktalar olarak tespit edilip kaldırılır.

### Tek Instance Kontrolü

| Platform | Yöntem |
|---|---|
| **Windows** | `CreateMutexW("Global\DeepCalculator_SingleInstance_Mutex")` |
| **macOS/Linux** | `/tmp/deep_calculator.lock` dosya kilidi (`fcntl`) |

Program zaten açıksa Windows'ta mevcut pencere öne getirilir (`FindWindowW` ile `WINDOW_TITLE` sabiti kullanılır).

---

## 📖 Modül Referansı

### `core/constants.py`

| Sabit | Tip | Açıklama |
|---|---|---|
| `ORG` | `str` | Organizasyon adı (`"DeepCalc"`) |
| `APP` | `str` | Uygulama adı (`"Calculator"`) |
| `VERSION` | `str` | Sürüm (`"2.0.0"`) |
| `WINDOW_TITLE` | `str` | Pencere başlığı — tek yerde tanımlı |
| `DEFAULT_W/H` | `int` | Varsayılan pencere boyutu (320×500) |
| `CORNER_HIT` | `int` | Köşe çift-tık hassasiyeti (px) |
| `OPS` | `frozenset` | Operatör karakterleri: `+  −  ×  ÷` |
| `FUNCTIONS` | `frozenset` | Fonksiyon butonları: `1/x x² 2√x % ⌫ CE C +/-` |
| `KEY_MAP` | `dict` | Qt tuş kodu → token eşlemesi |
| `ALLOWED_NODES` | `tuple` | AST değerlendirmede izin verilen node tipleri |

### `core/engine.py`

**`CalculatorEngine.press(token) → CalculatorState`**

Her buton basışının giriş noktası. Token'a göre uygun handler çağrılır ve güncel state döndürülür.

| Token grubu | Handler |
|---|---|
| `"="` | `_handle_equals` — hesapla, = tekrarını destekle |
| `"C"` | `_handle_clear` — bellek ve geçmişi koruyarak sıfırla |
| `"CE"` | `_handle_clear_entry` — son operandı sil |
| `"⌫"` | `_handle_backspace` — son karakteri sil |
| `"%"` | `_handle_percent` — operandı 100'e böl |
| `"+/-"` | `_handle_negate` — işaret değiştir |
| `"1/x"` | `_handle_reciprocal` — tersini al |
| `"x²"` | `_handle_square` — karesini al |
| `"2√x"` | `_handle_sqrt` — karekök al |
| `"MC/MR/M+/M−/MS"` | Bellek handler'ları |
| `OPS` içindeki | `_handle_operator` — operatör ekle/değiştir |
| Rakam / `,` | `_handle_digit` — operanda karakter ekle |

### `core/formatter.py`

| Fonksiyon | Açıklama |
|---|---|
| `format_number(value)` | `float/int → "1.234.567,89"` |
| `format_display_expr(expr)` | İfade içindeki tüm sayılara binlik nokta uygular |

### `ui/window.py`

**`CalculatorWindow`** — `QMainWindow` subclass'ı.

| Metod | Açıklama |
|---|---|
| `_build_ui()` | Tüm widget'ları oluşturur |
| `_dispatch(token)` | Engine'e gönderir, `_render()` çağırır |
| `_render(state)` | State'e göre display, butonlar, bellek göstergesini günceller |
| `_apply_theme()` | Tüm widget'lara tema renkleri uygulanır |
| `_toggle_history()` | Geçmiş flyout'u açar/kapar |
| `_detect_system_theme()` | Windows registry'den açık/koyu tema okur |

### `ui/theme.py`

`ThemePalette` dataclass'ı 16 renk alanı içerir. `LIGHT` ve `DARK` hazır palettir. `btn_style()` fonksiyonu QSS string üretir.

### `ui/grid_layout.py`

`GRID` listesi `(etiket, satır, sütun, rowspan, colspan)` tuple'larından oluşur. 6 satır × 4 sütun düzen:

```
%    CE   C    ⌫
1/x  x²   2√x  ÷
7    8    9    ×
4    5    6    −
1    2    3    +
+/-  0    ,    =
```

---

## ⌨️ Klavye Kısayolları

| Tuş | İşlem |
|---|---|
| `0` – `9` | Rakam girişi |
| `+` `-` `*` `/` | Dört işlem |
| `Enter` veya `=` | Hesapla |
| `Backspace` | Son karakteri sil |
| `Esc` | Her şeyi temizle (C) |
| `Delete` | Son operandı sil (CE) |
| `,` veya `.` | Ondalık virgül |
| `%` | Yüzde |
| `F9` | İşaret değiştir (+/-) |
| `Ctrl + C` | Sonucu panoya kopyala |
| `Ctrl + V` | Panodan sayı yapıştır |
| `H` | Kullanım kılavuzunu aç |
| `Esc` (geçmiş açıkken) | Geçmiş panelini kapat |

---

## 🎨 Tema Sistemi

Program başlarken şu öncelik sırasıyla tema belirlenir:

```
1. Kullanıcı daha önce Ayarlar menüsünden manuel tema seçti mi?
      → Evet: QSettings'ten kayıtlı tema yüklenir.
      → Hayır: Windows registry okunur.

2. Windows registry: AppsUseLightTheme
      → 1 (açık): "light" tema
      → 0 (koyu): "dark" tema
      → Hata / Windows değil: "light" (varsayılan)
```

> ⚠️ **Not:** Program çalışırken Windows teması değiştirilirse otomatik güncelleme olmaz.
> Programı yeniden başlatmak gerekir (Manuel seçim yapılmamışsa).

### Renk Paleti

| Alan | Açık | Koyu |
|---|---|---|
| Arka plan | `#F2F2F7` | `#1C1C1E` |
| Yüzey | `#FFFFFF` | `#2C2C2E` |
| Metin | `#1A1A2E` | `#F2F2F7` |
| Operatör butonu | `#FF9500` | `#FF9F0A` |
| Sayısal buton | `#FFFFFF` | `#3A3A3C` |
| Fonksiyon butonu | `#E5E5EA` | `#2C2C2E` |
| Vurgu rengi | `#FF9500` | `#FF9F0A` |

---

## 💾 Bellek İşlemleri

| Buton | İşlev |
|---|---|
| **MS** | Ekrandaki sayıyı belleğe kaydet (Memory Store) |
| **MR** | Bellekteki sayıyı ekrana yükle (Memory Recall) |
| **M+** | Ekrandaki sayıyı belleğe ekle |
| **M−** | Ekrandaki sayıyı bellekten çıkar |
| **MC** | Belleği sıfırla (Memory Clear) |

- Bellekte değer varken display üzerinde küçük **M** göstergesi görünür.
- MC ve MR butonları bellek boşken devre dışı (gri) kalır.
- Bellek değeri C (temizle) tuşunda korunur — sadece MC sıfırlar.

---

## 📜 Hesap Geçmişi

- **⏱ butonu** ile geçmiş paneli aşağıdan kayarak açılır/kapanır.
- Her `=` basışında işlem `"ifade = sonuç"` formatında geçmişe eklenir.
- Geçmişteki bir satıra tıklamak o sonucu ekrana yükler.
- **Temizle** butonu geçmişi siler.
- `Esc` tuşu açık geçmiş panelini kapatır.

---

## 📦 Derleme (EXE)

PyInstaller ile tek dosya EXE oluşturmak için:

```bash
pip install pyinstaller
pyinstaller main.spec
```

Derlenmiş dosya `dist/` klasöründe oluşur.

> `main.spec` içinde icon ve diğer kaynak dosyaları zaten tanımlıdır.

---

## ⚠️ Bilinen Sınırlar

| Sınır | Açıklama |
|---|---|
| **Tema otomatik güncelleme yok** | Windows teması değişince program yeniden başlatılmalı |
| **Bilimsel mod yok** | Yalnızca standart hesap makinesi işlemleri |
| **Sayı büyüklüğü** | `≥ 1e15` değerler bilimsel gösterime geçer (`1.23e+15`) |
| **Ondalık hassasiyet** | 12 anlamlı basamak (`:.12g` formatı) |
| **Negatif karekök** | Hata verir — karmaşık sayı desteği yok |

---

## 📝 Değişiklik Geçmişi

### v2.0.0 — 2026
- Dört işlem, bilimsel fonksiyonlar, bellek, geçmiş, tema, klavye desteği
- Modüler mimari: `core/`, `ui/`, `assets/` ayrı paketler
- Tek instance koruması (Windows Mutex / Unix fcntl)
- AST tabanlı güvenli hesaplama motoru (`eval()` yok)
- Türkçe sayı formatı (1.234.567,89)
- Hakkında diyaloğunda tıklanabilir GitHub linki
- Bellek butonları (MC/MR) yalnızca bellek doluyken aktif
- GitHub standartları: `LICENSE`, `INSTALL.md`, `.gitignore` eklendi

---

## 📄 Lisans

Kaynak kodu değiştirilemez ve satılamaz.  
Kişisel ve ticari kullanım ücretsizdir.  
Detaylar için `LICENSE` dosyasına bakınız.

**© 2026 Izzmoo. Tüm hakları saklıdır.**
