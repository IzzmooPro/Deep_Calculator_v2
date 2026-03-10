# Kurulum Rehberi

## Gereksinimler

- Windows 10 / 11
- Python 3.10 veya üzeri
- PyQt6 6.4.0 veya üzeri

## Kaynak Koddan Çalıştırma

```bash
pip install -r requirements.txt
python main.py
```

## EXE Olarak Derleme

```bash
pip install pyinstaller
pyinstaller main.spec
```

Derleme tamamlandığında `dist/DeepCalculator.exe` dosyası oluşur.

## Klavye Kısayolları

| Tuş | İşlev |
|---|---|
| `0–9` | Rakam girişi |
| `+ - * /` | Dört işlem |
| `Enter` / `=` | Hesapla |
| `Backspace` | Son karakteri sil |
| `Esc` | Temizle |
| `Delete` | Son operandı sil (CE) |
| `Ctrl+C` | Sonucu kopyala |
| `Ctrl+V` | Panodan yapıştır |
| `F9` | İşaret değiştir (+/-) |
| `H` | Kullanım kılavuzu |

## İletişim

Geliştirici: Izzmoo
E-posta: IzzmooPro@gmail.com
GitHub: https://github.com/IzzmooPro/Deep_Calculator_v2
