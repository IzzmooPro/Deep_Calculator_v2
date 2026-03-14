"""
Çoklu dil desteği (i18n).

Desteklenen diller:
  tr — Türkçe (varsayılan)
  en — İngilizce
  de — Almanca
  fr — Fransızca
  es — İspanyolca

Kullanım:
  from core.i18n import t, set_language
  set_language("en")
  t("settings.theme")  →  "Theme"
"""

from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── Türkçe ────────────────────────────────────────────────────────────────
    "tr": {
        "lang.name": "Türkçe",

        # Tooltip
        "tooltip.settings": "Ayarlar",
        "tooltip.history":  "Geçmiş",

        # Bağlam menüsü (display sağ tık)
        "menu.copy":        "  Kopyala",
        "menu.paste":       "  Yapıştır",
        "menu.selectall":   "  Tümünü Seç",

        # Ayarlar menüsü
        "settings.theme":       "Tema",
        "settings.theme.light": "Açık",
        "settings.theme.dark":  "Koyu",
        "settings.opacity":              "Şeffaflık",
        "settings.opacity.full":         "Tam opak",
        "settings.opacity.slight":       "Hafif şeffaf",
        "settings.opacity.half":         "Yarı şeffaf",
        "settings.help":        "Kullanım Kılavuzu",
        "settings.feedback":    "Geri Bildirim Gönder",
        "settings.about":       "Hakkında",
        "settings.language":    "Dil",

        # Geçmiş paneli
        "history.title":        "Geçmiş",
        "history.clear":        "Temizle",
        "history.empty":        "Henüz hesaplama yapılmadı",

        # Hakkında diyaloğu
        "about.title":          "Hakkında",
        "about.version":        "Sürüm {version}  •  2026",
        "about.developer":      "Geliştirici",
        "about.contact":        "İletişim",
        "about.license":        "Lisans",
        "about.license.value":  "Ücretsiz — kişisel ve ticari",
        "about.note":           "Kaynak kodu değiştirilemez ve satılamaz.",
        "about.update.idle":    "Güncelleme durumu kontrol edilmedi.",
        "about.update.checking":"GitHub kontrol ediliyor...",
        "about.update.btn":     "Güncelleme Denetle",
        "about.update.checking.btn": "Kontrol ediliyor...",
        "about.update.available": "🔄  Yeni sürüm mevcut: {tag}",
        "about.update.uptodate":  "✓  En güncel sürümdesiniz.",
        "about.update.failed":    "⚠  Bağlantı hatası. İnternet bağlantınızı kontrol edin.",
        "about.update.retry":   "Tekrar Dene",
        "about.update.do":      "Güncelle",
        "about.ok":             "Tamam",

        # Güncelleme bildirimi
        "update.title":         "Yeni Sürüm Mevcut",
        "update.info":          "Mevcut: v{current}  →  Yeni: {new}\n\nGüncelleme otomatik indirilecek ve kurulacak.",
        "update.later":         "Daha Sonra",
        "update.do":            "Güncelle",
        "update.downloading":   "Güncelleniyor",
        "update.progress":      "Sürüm {version} indiriliyor...",

        # Geri bildirim
        "feedback.title":       "Geri Bildirim",
        "feedback.heading":     "💬  Geri Bildirim Gönder",
        "feedback.subtitle":    "GitHub'da bir konu açılacak. GitHub hesabı gerekmez.",
        "feedback.cat.suggest": "💡 Öneri",
        "feedback.cat.bug":     "🐛 Hata Bildirimi",
        "feedback.cat.general": "💬 Genel",
        "feedback.placeholder": "Düşüncelerinizi buraya yazın...",
        "feedback.send":        "Gönder →",
        "feedback.cancel":      "İptal",

        # Kılavuz
        "help.title":           "Kullanım Kılavuzu",
        "help.header":          "  🧮  Kullanım Kılavuzu",
        "help.kbd.title":       "Klavye Kısayolları",
        "help.kbd.digits":      "Rakam girişi",
        "help.kbd.ops":         "Dört işlem operatörleri",
        "help.kbd.enter":       "Hesapla",
        "help.kbd.backspace":   "Son karakteri sil",
        "help.kbd.esc":         "Her şeyi temizle (C)",
        "help.kbd.delete":      "Son operandı sil (CE)",
        "help.kbd.decimal":     "Ondalık virgül gir",
        "help.kbd.percent":     "Yüzde",
        "help.kbd.sign":        "İşaret değiştir (+/-)",
        "help.kbd.copy":        "Sonucu panoya kopyala",
        "help.kbd.paste":       "Panodan sayı yapıştır",
        "help.kbd.help":        "Bu kılavuzu aç",
        "help.btn.title":       "Buton Referansı",
        "help.btn.ce":          "Son operandı sil, operatörü koru",
        "help.btn.c":           "Her şeyi sıfırla",
        "help.btn.back":        "Son karakteri sil",
        "help.btn.sign":        "İşaret değiştir (±)",
        "help.btn.percent":     "Yüzdeye çevir (÷ 100)",
        "help.btn.inv":         "Tersini al (1 ÷ x)",
        "help.btn.sq":          "Karesini al",
        "help.btn.sqrt":        "Karekök al",
        "help.chain.title":     "Zincir İşlemler",
        "help.chain.1":         "Ara sonuç gösterir → 10 → 13",
        "help.chain.2":         "Son işlemi tekrarlar: 8+3=11 → =→14",
        "help.chain.3":         "Tam ifadeyi gösterir: 5+2+3 =",
        "help.clip.title":      "Kopyala & Yapıştır",
        "help.clip.1":          "Kopyala / Yapıştır / Tümünü Seç",
        "help.clip.2":          "Sonucu panoya kopyala",
        "help.clip.3":          "Panodan sayı yapıştır",
        "help.view.title":      "Görünüm & Pencere",
        "help.view.1":          "Açık / Koyu tema (kaydedilir)",
        "help.view.2":          "Pencere opaklığı — 3 seviye",
        "help.view.3":          "Varsayılan boyuta sıfırla",
        "help.close":           "Tamam",
    },

    # ── İngilizce ─────────────────────────────────────────────────────────────
    "en": {
        "lang.name": "English",

        "tooltip.settings": "Settings",
        "tooltip.history":  "History",

        "menu.copy":        "  Copy",
        "menu.paste":       "  Paste",
        "menu.selectall":   "  Select All",

        "settings.theme":       "Theme",
        "settings.theme.light": "Light",
        "settings.theme.dark":  "Dark",
        "settings.opacity":              "Opacity",
        "settings.opacity.full":         "Fully opaque",
        "settings.opacity.slight":       "Slightly transparent",
        "settings.opacity.half":         "Semi-transparent",
        "settings.help":        "User Guide",
        "settings.feedback":    "Send Feedback",
        "settings.about":       "About",
        "settings.language":    "Language",

        "history.title":        "History",
        "history.clear":        "Clear",
        "history.empty":        "No calculations yet",

        "about.title":          "About",
        "about.version":        "Version {version}  •  2026",
        "about.developer":      "Developer",
        "about.contact":        "Contact",
        "about.license":        "License",
        "about.license.value":  "Free — personal and commercial",
        "about.note":           "Source code may not be modified or sold.",
        "about.update.idle":    "Update status not checked.",
        "about.update.checking":"Checking GitHub...",
        "about.update.btn":     "Check for Updates",
        "about.update.checking.btn": "Checking...",
        "about.update.available": "🔄  New version available: {tag}",
        "about.update.uptodate":  "✓  You are up to date.",
        "about.update.failed":    "⚠  Connection error. Check your internet connection.",
        "about.update.retry":   "Retry",
        "about.update.do":      "Update",
        "about.ok":             "OK",

        "update.title":         "New Version Available",
        "update.info":          "Current: v{current}  →  New: {new}\n\nThe update will be downloaded and installed automatically.",
        "update.later":         "Later",
        "update.do":            "Update",
        "update.downloading":   "Updating",
        "update.progress":      "Downloading version {version}...",

        "feedback.title":       "Feedback",
        "feedback.heading":     "💬  Send Feedback",
        "feedback.subtitle":    "A GitHub issue will be opened. No account required.",
        "feedback.cat.suggest": "💡 Suggestion",
        "feedback.cat.bug":     "🐛 Bug Report",
        "feedback.cat.general": "💬 General",
        "feedback.placeholder": "Write your thoughts here...",
        "feedback.send":        "Send →",
        "feedback.cancel":      "Cancel",

        "help.title":           "User Guide",
        "help.header":          "  🧮  User Guide",
        "help.kbd.title":       "Keyboard Shortcuts",
        "help.kbd.digits":      "Digit input",
        "help.kbd.ops":         "Four arithmetic operators",
        "help.kbd.enter":       "Calculate",
        "help.kbd.backspace":   "Delete last character",
        "help.kbd.esc":         "Clear all (C)",
        "help.kbd.delete":      "Clear entry (CE)",
        "help.kbd.decimal":     "Enter decimal point",
        "help.kbd.percent":     "Percent",
        "help.kbd.sign":        "Toggle sign (+/-)",
        "help.kbd.copy":        "Copy result to clipboard",
        "help.kbd.paste":       "Paste number from clipboard",
        "help.kbd.help":        "Open this guide",
        "help.btn.title":       "Button Reference",
        "help.btn.ce":          "Clear entry, keep operator",
        "help.btn.c":           "Clear all",
        "help.btn.back":        "Delete last character",
        "help.btn.sign":        "Toggle sign (±)",
        "help.btn.percent":     "Convert to percent (÷ 100)",
        "help.btn.inv":         "Reciprocal (1 ÷ x)",
        "help.btn.sq":          "Square",
        "help.btn.sqrt":        "Square root",
        "help.chain.title":     "Chained Operations",
        "help.chain.1":         "Shows intermediate result → 10 → 13",
        "help.chain.2":         "Repeats last operation: 8+3=11 → =→14",
        "help.chain.3":         "Shows full expression: 5+2+3 =",
        "help.clip.title":      "Copy & Paste",
        "help.clip.1":          "Copy / Paste / Select All",
        "help.clip.2":          "Copy result to clipboard",
        "help.clip.3":          "Paste number from clipboard",
        "help.view.title":      "Appearance & Window",
        "help.view.1":          "Light / Dark theme (saved)",
        "help.view.2":          "Window opacity — 3 levels",
        "help.view.3":          "Reset to default size",
        "help.close":           "OK",
    },

    # ── Almanca ───────────────────────────────────────────────────────────────
    "de": {
        "lang.name": "Deutsch",

        "tooltip.settings": "Einstellungen",
        "tooltip.history":  "Verlauf",

        "menu.copy":        "  Kopieren",
        "menu.paste":       "  Einfügen",
        "menu.selectall":   "  Alles auswählen",

        "settings.theme":       "Design",
        "settings.theme.light": "Hell",
        "settings.theme.dark":  "Dunkel",
        "settings.opacity":              "Transparenz",
        "settings.opacity.full":         "Vollständig opak",
        "settings.opacity.slight":       "Leicht transparent",
        "settings.opacity.half":         "Halbtransparent",
        "settings.help":        "Benutzerhandbuch",
        "settings.feedback":    "Feedback senden",
        "settings.about":       "Über",
        "settings.language":    "Sprache",

        "history.title":        "Verlauf",
        "history.clear":        "Löschen",
        "history.empty":        "Noch keine Berechnungen",

        "about.title":          "Über",
        "about.version":        "Version {version}  •  2026",
        "about.developer":      "Entwickler",
        "about.contact":        "Kontakt",
        "about.license":        "Lizenz",
        "about.license.value":  "Kostenlos — privat und kommerziell",
        "about.note":           "Quellcode darf nicht verändert oder verkauft werden.",
        "about.update.idle":    "Updatestatus nicht überprüft.",
        "about.update.checking":"GitHub wird überprüft...",
        "about.update.btn":     "Nach Updates suchen",
        "about.update.checking.btn": "Wird geprüft...",
        "about.update.available": "🔄  Neue Version verfügbar: {tag}",
        "about.update.uptodate":  "✓  Sie verwenden die neueste Version.",
        "about.update.failed":    "⚠  Verbindungsfehler. Internetverbindung prüfen.",
        "about.update.retry":   "Erneut versuchen",
        "about.update.do":      "Aktualisieren",
        "about.ok":             "OK",

        "update.title":         "Neue Version verfügbar",
        "update.info":          "Aktuell: v{current}  →  Neu: {new}\n\nDas Update wird automatisch heruntergeladen und installiert.",
        "update.later":         "Später",
        "update.do":            "Aktualisieren",
        "update.downloading":   "Wird aktualisiert",
        "update.progress":      "Version {version} wird heruntergeladen...",

        "feedback.title":       "Feedback",
        "feedback.heading":     "💬  Feedback senden",
        "feedback.subtitle":    "Ein GitHub-Issue wird geöffnet. Kein Konto erforderlich.",
        "feedback.cat.suggest": "💡 Vorschlag",
        "feedback.cat.bug":     "🐛 Fehlermeldung",
        "feedback.cat.general": "💬 Allgemein",
        "feedback.placeholder": "Schreiben Sie Ihre Gedanken hier...",
        "feedback.send":        "Senden →",
        "feedback.cancel":      "Abbrechen",

        "help.title":           "Benutzerhandbuch",
        "help.header":          "  🧮  Benutzerhandbuch",
        "help.kbd.title":       "Tastaturkürzel",
        "help.kbd.digits":      "Zifferneingabe",
        "help.kbd.ops":         "Vier Grundrechenarten",
        "help.kbd.enter":       "Berechnen",
        "help.kbd.backspace":   "Letztes Zeichen löschen",
        "help.kbd.esc":         "Alles löschen (C)",
        "help.kbd.delete":      "Eingabe löschen (CE)",
        "help.kbd.decimal":     "Dezimalkomma eingeben",
        "help.kbd.percent":     "Prozent",
        "help.kbd.sign":        "Vorzeichen wechseln (+/-)",
        "help.kbd.copy":        "Ergebnis kopieren",
        "help.kbd.paste":       "Zahl einfügen",
        "help.kbd.help":        "Dieses Handbuch öffnen",
        "help.btn.title":       "Schaltflächenreferenz",
        "help.btn.ce":          "Eingabe löschen, Operator behalten",
        "help.btn.c":           "Alles zurücksetzen",
        "help.btn.back":        "Letztes Zeichen löschen",
        "help.btn.sign":        "Vorzeichen wechseln (±)",
        "help.btn.percent":     "In Prozent umwandeln (÷ 100)",
        "help.btn.inv":         "Kehrwert (1 ÷ x)",
        "help.btn.sq":          "Quadrieren",
        "help.btn.sqrt":        "Quadratwurzel",
        "help.chain.title":     "Verkettete Operationen",
        "help.chain.1":         "Zeigt Zwischenergebnis → 10 → 13",
        "help.chain.2":         "Wiederholt letzte Operation: 8+3=11 → =→14",
        "help.chain.3":         "Zeigt vollständigen Ausdruck: 5+2+3 =",
        "help.clip.title":      "Kopieren & Einfügen",
        "help.clip.1":          "Kopieren / Einfügen / Alles auswählen",
        "help.clip.2":          "Ergebnis kopieren",
        "help.clip.3":          "Zahl einfügen",
        "help.view.title":      "Darstellung & Fenster",
        "help.view.1":          "Hell / Dunkel Design (gespeichert)",
        "help.view.2":          "Fenstertransparenz — 3 Stufen",
        "help.view.3":          "Standardgröße wiederherstellen",
        "help.close":           "OK",
    },

    # ── Fransızca ─────────────────────────────────────────────────────────────
    "fr": {
        "lang.name": "Français",

        "tooltip.settings": "Paramètres",
        "tooltip.history":  "Historique",

        "menu.copy":        "  Copier",
        "menu.paste":       "  Coller",
        "menu.selectall":   "  Tout sélectionner",

        "settings.theme":       "Thème",
        "settings.theme.light": "Clair",
        "settings.theme.dark":  "Sombre",
        "settings.opacity":              "Opacité",
        "settings.opacity.full":         "Totalement opaque",
        "settings.opacity.slight":       "Légèrement transparent",
        "settings.opacity.half":         "Semi-transparent",
        "settings.help":        "Guide d'utilisation",
        "settings.feedback":    "Envoyer un avis",
        "settings.about":       "À propos",
        "settings.language":    "Langue",

        "history.title":        "Historique",
        "history.clear":        "Effacer",
        "history.empty":        "Aucun calcul effectué",

        "about.title":          "À propos",
        "about.version":        "Version {version}  •  2026",
        "about.developer":      "Développeur",
        "about.contact":        "Contact",
        "about.license":        "Licence",
        "about.license.value":  "Gratuit — personnel et commercial",
        "about.note":           "Le code source ne peut pas être modifié ou vendu.",
        "about.update.idle":    "Statut de mise à jour non vérifié.",
        "about.update.checking":"Vérification de GitHub...",
        "about.update.btn":     "Vérifier les mises à jour",
        "about.update.checking.btn": "Vérification...",
        "about.update.available": "🔄  Nouvelle version disponible : {tag}",
        "about.update.uptodate":  "✓  Vous êtes à jour.",
        "about.update.failed":    "⚠  Erreur de connexion. Vérifiez votre connexion.",
        "about.update.retry":   "Réessayer",
        "about.update.do":      "Mettre à jour",
        "about.ok":             "OK",

        "update.title":         "Nouvelle version disponible",
        "update.info":          "Actuel : v{current}  →  Nouveau : {new}\n\nLa mise à jour sera téléchargée et installée automatiquement.",
        "update.later":         "Plus tard",
        "update.do":            "Mettre à jour",
        "update.downloading":   "Mise à jour en cours",
        "update.progress":      "Téléchargement de la version {version}...",

        "feedback.title":       "Avis",
        "feedback.heading":     "💬  Envoyer un avis",
        "feedback.subtitle":    "Un ticket GitHub sera ouvert. Aucun compte requis.",
        "feedback.cat.suggest": "💡 Suggestion",
        "feedback.cat.bug":     "🐛 Signaler un bug",
        "feedback.cat.general": "💬 Général",
        "feedback.placeholder": "Écrivez vos commentaires ici...",
        "feedback.send":        "Envoyer →",
        "feedback.cancel":      "Annuler",

        "help.title":           "Guide d'utilisation",
        "help.header":          "  🧮  Guide d'utilisation",
        "help.kbd.title":       "Raccourcis clavier",
        "help.kbd.digits":      "Saisie de chiffres",
        "help.kbd.ops":         "Quatre opérations arithmétiques",
        "help.kbd.enter":       "Calculer",
        "help.kbd.backspace":   "Supprimer le dernier caractère",
        "help.kbd.esc":         "Tout effacer (C)",
        "help.kbd.delete":      "Effacer la saisie (CE)",
        "help.kbd.decimal":     "Entrer la virgule décimale",
        "help.kbd.percent":     "Pourcentage",
        "help.kbd.sign":        "Changer le signe (+/-)",
        "help.kbd.copy":        "Copier le résultat",
        "help.kbd.paste":       "Coller un nombre",
        "help.kbd.help":        "Ouvrir ce guide",
        "help.btn.title":       "Référence des boutons",
        "help.btn.ce":          "Effacer la saisie, conserver l'opérateur",
        "help.btn.c":           "Tout réinitialiser",
        "help.btn.back":        "Supprimer le dernier caractère",
        "help.btn.sign":        "Changer le signe (±)",
        "help.btn.percent":     "Convertir en pourcentage (÷ 100)",
        "help.btn.inv":         "Inverse (1 ÷ x)",
        "help.btn.sq":          "Carré",
        "help.btn.sqrt":        "Racine carrée",
        "help.chain.title":     "Opérations en chaîne",
        "help.chain.1":         "Affiche le résultat intermédiaire → 10 → 13",
        "help.chain.2":         "Répète la dernière opération : 8+3=11 → =→14",
        "help.chain.3":         "Affiche l'expression complète : 5+2+3 =",
        "help.clip.title":      "Copier & Coller",
        "help.clip.1":          "Copier / Coller / Tout sélectionner",
        "help.clip.2":          "Copier le résultat",
        "help.clip.3":          "Coller un nombre",
        "help.view.title":      "Apparence & Fenêtre",
        "help.view.1":          "Thème clair / sombre (sauvegardé)",
        "help.view.2":          "Opacité de la fenêtre — 3 niveaux",
        "help.view.3":          "Réinitialiser la taille par défaut",
        "help.close":           "OK",
    },

    # ── İspanyolca ────────────────────────────────────────────────────────────
    "es": {
        "lang.name": "Español",

        "tooltip.settings": "Configuración",
        "tooltip.history":  "Historial",

        "menu.copy":        "  Copiar",
        "menu.paste":       "  Pegar",
        "menu.selectall":   "  Seleccionar todo",

        "settings.theme":       "Tema",
        "settings.theme.light": "Claro",
        "settings.theme.dark":  "Oscuro",
        "settings.opacity":              "Opacidad",
        "settings.opacity.full":         "Totalmente opaco",
        "settings.opacity.slight":       "Ligeramente transparente",
        "settings.opacity.half":         "Semitransparente",
        "settings.help":        "Guía de uso",
        "settings.feedback":    "Enviar comentarios",
        "settings.about":       "Acerca de",
        "settings.language":    "Idioma",

        "history.title":        "Historial",
        "history.clear":        "Limpiar",
        "history.empty":        "Aún no hay cálculos",

        "about.title":          "Acerca de",
        "about.version":        "Versión {version}  •  2026",
        "about.developer":      "Desarrollador",
        "about.contact":        "Contacto",
        "about.license":        "Licencia",
        "about.license.value":  "Gratuito — personal y comercial",
        "about.note":           "El código fuente no puede modificarse ni venderse.",
        "about.update.idle":    "Estado de actualización no verificado.",
        "about.update.checking":"Verificando GitHub...",
        "about.update.btn":     "Buscar actualizaciones",
        "about.update.checking.btn": "Verificando...",
        "about.update.available": "🔄  Nueva versión disponible: {tag}",
        "about.update.uptodate":  "✓  Estás al día.",
        "about.update.failed":    "⚠  Error de conexión. Verifica tu conexión a internet.",
        "about.update.retry":   "Reintentar",
        "about.update.do":      "Actualizar",
        "about.ok":             "Aceptar",

        "update.title":         "Nueva versión disponible",
        "update.info":          "Actual: v{current}  →  Nueva: {new}\n\nLa actualización se descargará e instalará automáticamente.",
        "update.later":         "Más tarde",
        "update.do":            "Actualizar",
        "update.downloading":   "Actualizando",
        "update.progress":      "Descargando versión {version}...",

        "feedback.title":       "Comentarios",
        "feedback.heading":     "💬  Enviar comentarios",
        "feedback.subtitle":    "Se abrirá un issue en GitHub. No se requiere cuenta.",
        "feedback.cat.suggest": "💡 Sugerencia",
        "feedback.cat.bug":     "🐛 Informe de error",
        "feedback.cat.general": "💬 General",
        "feedback.placeholder": "Escribe tus comentarios aquí...",
        "feedback.send":        "Enviar →",
        "feedback.cancel":      "Cancelar",

        "help.title":           "Guía de uso",
        "help.header":          "  🧮  Guía de uso",
        "help.kbd.title":       "Atajos de teclado",
        "help.kbd.digits":      "Entrada de dígitos",
        "help.kbd.ops":         "Cuatro operaciones aritméticas",
        "help.kbd.enter":       "Calcular",
        "help.kbd.backspace":   "Eliminar último carácter",
        "help.kbd.esc":         "Borrar todo (C)",
        "help.kbd.delete":      "Borrar entrada (CE)",
        "help.kbd.decimal":     "Introducir punto decimal",
        "help.kbd.percent":     "Porcentaje",
        "help.kbd.sign":        "Cambiar signo (+/-)",
        "help.kbd.copy":        "Copiar resultado",
        "help.kbd.paste":       "Pegar número",
        "help.kbd.help":        "Abrir esta guía",
        "help.btn.title":       "Referencia de botones",
        "help.btn.ce":          "Borrar entrada, mantener operador",
        "help.btn.c":           "Reiniciar todo",
        "help.btn.back":        "Eliminar último carácter",
        "help.btn.sign":        "Cambiar signo (±)",
        "help.btn.percent":     "Convertir a porcentaje (÷ 100)",
        "help.btn.inv":         "Recíproco (1 ÷ x)",
        "help.btn.sq":          "Elevar al cuadrado",
        "help.btn.sqrt":        "Raíz cuadrada",
        "help.chain.title":     "Operaciones encadenadas",
        "help.chain.1":         "Muestra resultado intermedio → 10 → 13",
        "help.chain.2":         "Repite última operación: 8+3=11 → =→14",
        "help.chain.3":         "Muestra expresión completa: 5+2+3 =",
        "help.clip.title":      "Copiar & Pegar",
        "help.clip.1":          "Copiar / Pegar / Seleccionar todo",
        "help.clip.2":          "Copiar resultado",
        "help.clip.3":          "Pegar número",
        "help.view.title":      "Apariencia & Ventana",
        "help.view.1":          "Tema claro / oscuro (guardado)",
        "help.view.2":          "Opacidad de ventana — 3 niveles",
        "help.view.3":          "Restablecer tamaño predeterminado",
        "help.close":           "Aceptar",
    },
}

# Aktif dil
_current_lang: str = "tr"

SUPPORTED_LANGUAGES = [
    ("tr", "Türkçe"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("es", "Español"),
]


def set_language(lang: str) -> None:
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    """Verilen anahtar için aktif dilde çeviri döner."""
    text = TRANSLATIONS.get(_current_lang, TRANSLATIONS["tr"]).get(key)
    if text is None:
        # Eksik çeviri varsa Türkçe'ye geri dön
        text = TRANSLATIONS["tr"].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
