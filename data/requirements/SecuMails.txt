## **1. Produktübersicht**

### **1.1 Produktbeschreibung**

- **Name**: FTAPI SecuMails
- **Zweck**: Sichere Verschlüsselung und Übertragung von E-Mails und Dateien direkt im E-Mail-Postfach
- **Vision**: "Securing Digital Freedom"
- **Zielgruppe**: Unternehmen, Behörden, Gesundheitswesen, HR-Abteilungen

### **1.2 Kernfunktionalität**

- Sicherer Ad-hoc-Versand und -Empfang von Nachrichten und Dateien
- Dateien jeder Größe (bis 100 GB) sicher per Mail versenden
- Ende-zu-Ende-Verschlüsselung nach dem Zero-Knowledge-Prinzip
- Integration in bestehende E-Mail-Systeme

## **2. Systemzugriff und Nutzungsmöglichkeiten**

### **2.1 Zugriffswege**

1. **Web-Interface**
    - Zugriff über alle gängigen Internet-Browser (aktuelle Versionen)
    - Unterstützte Browser: Google Chrome, Microsoft Edge, Safari, Firefox
    - Optimiert für alle Endgeräte: Desktop, Tablet, Smartphone (\geq 360 x 640 px)
    - Keine lokale Installation erforderlich
2. **Microsoft Outlook Add-In** (kostenpflichtige Erweiterung)
    - Systemanforderung: Microsoft Outlook 2016 oder neuer
    - Nahtlose Integration in die gewohnte Outlook-Umgebung
    - Kein Medienbruch beim Versand
3. **SubmitBox** (digitaler Briefkasten) - kostenpflichtige Erweiterung
    - Sicherer Kanal für externe Einreichungen
    - Keine Registrierung für externe Sender erforderlich

## **3. Sicherheitsarchitektur**

### **3.1 Verschlüsselungstechnologie**

### **3.1.1 SecuPass-Technologie**

- Hybride Verschlüsselung mit AES-256-Bit GCM Mode
- Datenverschlüsselung: Symmetrisches AES-Verfahren
- Schlüsselaustausch: Asymmetrisches RSA OAEP - Schlüsselpaar
- RSA-Schlüssel mit OAEP (Optimal Asymmetric Encryption Padding)
- Schlüssellänge: 4096 Bit
- Automatischer Schlüsselaustausch ohne manuelle Zertifikatseinspielung

### **3.1.2 Zero-Knowledge-Prinzip**

- Ende-zu-Ende-Verschlüsselung
- RSA-Schlüsselpaar wird am Client generiert
- Privater RSA-Schlüssel wird mit SecuPass-Passwort verschlüsselt
- Nur verschlüsselte Form wird auf Server gespeichert
- FTAPI hat zu keinem Zeitpunkt Zugriff auf Daten

### **3.1.3 Transportverschlüsselung**

- TLS 1.3 für sichere Übertragung ("Encryption-in-Transit")
- SSL Labs Rating: A+
- Verhindert unbefugten Zugriff während Datenübertragung

### **3.1.4 Krypto-Agilität**

- Flexibles kryptografisches System
- Anpassungsfähig an neue Bedrohungen
- Vorbereitung auf Post-Quantum-Kryptografie
- Speicherung von Verschlüsselungsinformationen für verschiedene Algorithmen

### **3.2 Sicherheitsstufen**

### **Sicherheitsstufe 1 - Sicherer Link**

- **Verschlüsselung**: Transportverschlüsselung (TLS)
- **Zugriff**: Jeder mit Link kann Dateien herunterladen
- **Account erforderlich**: Nein
- **Anwendungsfall**: Unkritische Daten, Ausschreibungsunterlagen, Software-Updates
- **Empfänger-Authentifizierung**: Keine

### **Sicherheitsstufe 2 - Sicherer Link + Login**

- **Verschlüsselung**: Transportverschlüsselung (TLS)
- **Zugriff**: Nur mit FTAPI-Account
- **Account erforderlich**: Ja (automatische Gast-Account-Erstellung möglich)
- **Anwendungsfall**: Daten für bestimmte Empfänger
- **Optional**: Doppelt-Authentifizierte-Registrierung (SMS-Code)

### **Sicherheitsstufe 3 - Sicherer Link + Login + verschlüsselte Dateien**

- **Verschlüsselung**: Ende-zu-Ende-Verschlüsselung für Dateien
- **Zugriff**: FTAPI-Account + SecuPass-Key erforderlich
- **Account erforderlich**: Ja
- **Anwendungsfall**: Sensible/unternehmenskritische Daten, Arbeitsverträge, Gehaltsabrechnungen
- **Besonderheit**: Nachricht bleibt unverschlüsselt sichtbar

### **Sicherheitsstufe 4 - Sicherer Link + Login + verschlüsselte Dateien + verschlüsselte Nachricht**

- **Verschlüsselung**: Vollständige Ende-zu-Ende-Verschlüsselung (Dateien + Nachricht)
- **Zugriff**: FTAPI-Account + SecuPass-Key erforderlich
- **Account erforderlich**: Ja
- **Anwendungsfall**: Höchst sensible Kommunikation, strategische Dokumente
- **Besonderheit**: Gesamter E-Mail-Text ist verschlüsselt

## **4. Funktionale Requirements**

### **4.1 Versand-Funktionen**

### **4.1.1 Outlook Add-In Versand**

1. **E-Mail-Erstellung**
    - Standard E-Mail-Erstellung mit Empfänger, Betreff, Nachricht
    - Anhänge per Drag & Drop oder Büroklammer-Symbol
2. **FTAPI-Versand**
    - Button "Mit FTAPI versenden" in Menüleiste
    - Automatische sichere Übertragung der Anhänge
3. **Download-Button Integration**
    - Optional: Download-Button direkt in E-Mail einfügen
    - Alternative: Automatische Platzierung über Signatur
4. **Einstellungen**
    - Auswahl der Sicherheitsstufe (1-4)
    - Festlegung der Gültigkeitsdauer für Downloads
    - Admin kann Vorgaben definieren ("Security-by-Default")

### **4.1.2 Web-Interface Versand**

1. **Neue Zustellung erstellen**
    - Eingabe von Empfänger, Betreff, Nachricht
2. **Datei-Upload**
    - Drag & Drop Funktionalität
    - "Dateien anhängen" Button
    - Maximale Dateigröße: 100 GB
3. **Sicherheitseinstellungen**
    - Wahl der Sicherheitsstufe
    - Gültigkeitsdauer festlegen
4. **Versand**
    - "Mit FTAPI versenden" Button

### **4.2 Empfangs-Funktionen**

### **4.2.1 Outlook Add-In Empfang**

1. **E-Mail-Empfang**
    - Zustellung im normalen E-Mail-Postfach
    - Sichtbar: Absender, Betreff, Dateinamen, Nachrichtentext
2. **Entschlüsselung bei Stufe 4**
    - Button "Mail entschlüsseln" in Menüleiste
    - Entschlüsselung des Nachrichtentexts
3. **Download-Optionen**
    - "Herunterladen" Button in Menüleiste → Download in Outlook
    - Download-Link in E-Mail → Weiterleitung zum Browser
    - "Speichern unter" Option für alternativen Speicherort

### **4.2.2 Browser-basierter Empfang**

- Sicherer Download-Link in E-Mail
- Je nach Sicherheitsstufe weitere Authentifizierung nötig
- Download über Web-Interface

### **4.3 SubmitBox-Funktionalität**

### **4.3.1 Grundfunktionen**

- Digitaler Briefkasten für sichere Dateneinreichung
- Keine Registrierung für externe Sender erforderlich
- Einreichung nur mit SubmitBox-Link möglich
- Verschlüsselte Übertragung in allen Sicherheitsstufen

### **4.3.2 Integration**

- **E-Mail-Signatur**: Link zur persönlichen SubmitBox
- **Webseite**: Einbindung des Links
- **Outlook Integration**:
    - Option 1: Einmal gültiges Upload-Ticket versenden
    - Option 2: Permanenter SubmitBox-Link

### **4.3.3 Workflow für Externe**

1. **Ticket-Anforderung**
    - SubmitBox-Link aufrufen
    - E-Mail-Adresse eingeben
    - "Ticket erstellen" klicken
2. **Upload-Link erhalten**
    - E-Mail mit persönlichem Upload-Link
    - Betreff: "SubmitBox Ticket erstellt"
3. **Datei-Upload**
    - Upload-Link öffnen
    - Dateien per Drag & Drop oder Büroklammer hinzufügen
    - Nachricht eingeben
    - "Abschicken" klicken
4. **Bestätigungen**
    - Einreichungsbestätigung per E-Mail
    - Download-Bestätigung wenn Empfänger Dateien herunterlädt

### **4.3.4 Kontrollfunktionen**

- Optionales White- und Blacklisting
- Volle Kontrolle über erlaubte Einreichungen

### **4.4 Benachrichtigungen und Tracking**

### **4.4.1 Download-Bestätigungen**

- Automatische Benachrichtigung nach erfolgreichem Download
- Revisionssichere Dokumentation
- Transparenz über Empfangsstatus

### **4.4.2 Status-Tracking**

- Überblick über versendete Dateien
- Empfangsstatus in Echtzeit
- Reporting-Funktionen für Administratoren

### **4.5 Datenmanagement**

### **4.5.1 Löschfristen**

- Individuell festlegbare Aufbewahrungsfristen
- Automatische Löschung nach Ablauf
- Kein Zugriff nach Löschung möglich

### **4.5.2 Dateigröße**

- Maximale Dateigröße: 100 GB
- Keine Einschränkung bei Anzahl der Dateien
- Optimiert für große Datenmengen

## **5. Administrative Requirements**

### **5.1 Benutzerverwaltung**

- Zentrale Verwaltung über Admin-Oberfläche
- Lizenzverwaltung für Nutzer
- Rechtevergabe und Rollenverwaltung

### **5.2 Security-by-Default**

- Organisationsweite Vorgabe von Sicherheitsstufen
- Erzwingung bestimmter Verschlüsselungsstandards
- Automatische Regeln für Verschlüsselung

### **5.3 Compliance-Features**

- DSGVO-konforme Datenverarbeitung
- BSI-konforme Verschlüsselungsstandards
- Revisionssichere Protokollierung

### **5.4 Reporting**

- Detailliertes Reporting über Admin-Oberfläche
- Analyse des Anwenderverhaltens
- Ereignisprotokolle (Login-Zeiten, Aktivitäten)
- Export als HTML, PDF oder XLS

### **5.5 Integration**

- REST API für Systemintegration
- SMTP/IMAP Unterstützung
- Active Directory/LDAP Anbindung
- Single Sign-On (SSO) Unterstützung

## **6. Technische Requirements**

### **6.1 Client-Anforderungen**

- **Browser**: Aktuelle Versionen von Chrome, Edge, Safari, Firefox
- **Outlook**: Version 2016 oder höher
- **Bildschirmauflösung**: Minimum 360 x 640 px
- **Internetverbindung**: Stabile Verbindung erforderlich

### **6.2 Server-Infrastruktur**

- Cloud-basierte Lösung
- Hosting in deutschem Rechenzentrum (SysEleven)
- Kubernetes-Container-Architektur
- 99% Verfügbarkeit
- Geo-redundante Datenspeicherung

### **6.3 Sicherheitsstandards**

- ISO 27001 Zertifizierung
- BSI C5 Auditierung
- Regelmäßige Penetrationstests
- Secure Development Lifecycle

## **7. Benutzerfreundlichkeit**

### **7.1 User Experience**

- Intuitive Benutzeroberfläche
- Keine technischen Vorkenntnisse erforderlich
- Gewohnte E-Mail-Umgebung beibehalten
- Responsive Design für alle Geräte

### **7.2 Anwenderunterstützung**

- Interaktive Produkt-Touren
- Kurzanleitungen und Dokumentation
- Help Center mit FAQ
- Deutscher Admin-Support

### **7.3 Mehrsprachigkeit**

- Deutsche und englische Oberfläche
- Weitere Sprachen konfigurierbar
- Automatische Spracherkennung

## **8. Performance-Requirements**

### **8.1 Übertragungsgeschwindigkeit**

- Optimiert für große Dateien
- Parallele Upload-Streams
- Resumable Uploads bei Verbindungsabbruch

### **8.2 Skalierbarkeit**

- Unbegrenzte Anzahl externer Nutzer
- Elastische Cloud-Infrastruktur
- Automatische Lastverteilung

## **9. Lizenzierung und Kosten**

### **9.1 Basis-Lizenz**

- Web-Interface Zugang
- Grundfunktionen SecuMails

### **9.2 Kostenpflichtige Erweiterungen**

- Outlook Add-In
- SubmitBox Funktionalität
- Erweiterte Admin-Features
- API-Zugriff

## **10. Migration und Implementierung**

### **10.1 Implementierung**

- Schnelle und einfache Einrichtung
- Keine aufwendige Infrastruktur-Änderung
- Schrittweise Einführung möglich

### **10.2 Schulung**

- Personalisiertes Onboarding
- Schulungsmaterialien
- Customer Success Team Begleitung

### **10.3 Support**

- Deutschsprachiger Support
- SLA-basierte Reaktionszeiten
- Technische Dokumentation

# Use Cases:

# FTAPI SecuMails - Detaillierte Requirements und Use Cases

## 1. Produktübersicht

FTAPI SecuMails ist eine Lösung für den sicheren Versand und Empfang von Nachrichten und Dateien via E-Mail. Die Lösung ermöglicht die verschlüsselte Übertragung von Dateien bis zu 100 GB und bietet verschiedene Sicherheitsstufen für unterschiedliche Schutzbedürfnisse.

## 2. Systemanforderungen

### 2.1 Technische Requirements

### Unterstützte Umgebungen

- **Web-Browser** (jeweils aktuelle Version):
    - Google Chrome
    - Microsoft Edge
    - Safari
    - Mozilla Firefox
- **Microsoft Outlook Add-in**:
    - Microsoft Outlook 2016 oder neuer
- **Mobile Endgeräte**:
    - Optimiert für Desktop, Tablet und Smartphone
    - Mindestauflösung: 360 x 640 px

### Verschlüsselung

- AES GCM Mode 256-Bit-Verschlüsselung
- Transport-Verschlüsselung via TLS 1.3
- Ende-zu-Ende-Verschlüsselung nach Zero-Knowledge-Prinzip
- Verschlüsselung nach BSI-Standards

## 3. Funktionale Requirements

### 3.1 Versand-Funktionen

### FR-001: Dateigrößen-Handling

- System MUSS Dateien bis zu 100 GB verarbeiten können
- System MUSS maximale Anhangsgröße für WebUpload konfigurierbar machen
- System MUSS maximale Segmentgröße für Upload konfigurierbar machen

### FR-002: Sicherheitsstufen

System MUSS vier verschiedene Sicherheitsstufen anbieten:

**Sicherheitsstufe 1 - Sicherer Link**

- Zustellung wird hinter sicherem Link abgelegt
- Kein FTAPI-Account für Download erforderlich
- Anonymer Download möglich (konfigurierbar)

**Sicherheitsstufe 2 - Sicherer Link + Login**

- Empfänger benötigt FTAPI-Account
- Automatische Gast-Account-Erstellung für externe Empfänger
- Empfänger-Authentifizierung erforderlich

**Sicherheitsstufe 3 - Sicherer Link + Login + verschlüsselte Dateien**

- Ende-zu-Ende-Verschlüsselung der Dateien
- SecuPass-Key für Ver-/Entschlüsselung erforderlich
- Zero-Knowledge-Prinzip

**Sicherheitsstufe 4 - Sicherer Link + Login + verschlüsselte Dateien + verschlüsselte Nachricht**

- Ende-zu-Ende-Verschlüsselung von Dateien UND Nachrichtentext
- SecuPass-Key für Ver-/Entschlüsselung erforderlich
- Höchste Sicherheitsstufe für kritische Kommunikation

### FR-003: Versand-Optionen

- System MUSS Versand ohne Anhang ermöglichen (konfigurierbar)
- System MUSS Gültigkeitsdauer für Download-Links konfigurierbar machen
- System MUSS automatische Löschfristen für Dateien unterstützen
- System MUSS Download-Button in E-Mail integrierbar machen

### FR-004: Benachrichtigungen

- System MUSS automatische Download-Bestätigungen versenden
- System MUSS Versender über erfolgreichen Download informieren
- System MUSS IP-Adressen-Protokollierung ermöglichen (optional)

### 3.2 Empfangs-Funktionen

### FR-005: Antwort-Funktion

- System MUSS "Antwort senden"-Funktion für externe Empfänger bereitstellen
- Externe Empfänger MÜSSEN auf empfangene Zustellungen antworten können

### FR-006: Entschlüsselung

- System MUSS Mail-Entschlüsselung bei Sicherheitsstufe 4 im Outlook Add-in ermöglichen
- System MUSS SecuPass-Verwaltung bereitstellen

### 3.3 Administrative Funktionen

### FR-007: Organisationsweite Einstellungen

- Administrator MUSS Standard-Sicherheitsstufe vorgeben können
- Administrator MUSS Versandregeln organisationsweit festlegen können
- Administrator MUSS Whitelist für Zustellungsempfänger konfigurieren können

### FR-008: Benutzer- und Gruppenverwaltung

- System MUSS Benutzer Gruppen zuweisen können
- System MUSS Berechtigungen und Lizenzen pro Gruppe verwalten
- System MUSS Sicherheitseinstellungen pro Gruppe konfigurierbar machen

### FR-009: Compliance und Reporting

- System MUSS revisionssichere Download-Bestätigungen bereitstellen
- System MUSS Zustellungs-Download-Report generieren können
- System MUSS DSGVO-konforme Datenverarbeitung gewährleisten

### 3.4 Integration Requirements

### FR-010: Outlook Add-in

- Add-in MUSS nahtlose Integration in Outlook bieten
- Add-in MUSS "Mit FTAPI versenden"-Button bereitstellen
- Add-in MUSS Sicherheitsstufen-Auswahl ermöglichen
- Add-in MUSS Download-Button in E-Mail einfügen können

### FR-011: SubmitBox Integration

- System MUSS SubmitBox für sicheren Datenempfang bereitstellen
- SubmitBox MUSS ohne Registrierung für Externe nutzbar sein
- SubmitBox MUSS als digitaler Briefkasten fungieren

## 4. Detaillierte Use Cases

### 4.1 UC-001: Sicherer Versand via Outlook Add-in

**Akteure:**

- USER A (Versender mit Outlook)
- USER B (Empfänger)

**Vorbedingungen:**

- USER A hat Outlook 2016+ mit installiertem FTAPI Add-in
- USER A ist bei FTAPI registriert und angemeldet

**Hauptszenario:**

1. USER A erstellt neue E-Mail in Outlook
2. USER A fügt Empfänger (USER B), Betreff und Nachrichtentext hinzu
3. USER A fügt Dateien als Anhang hinzu
4. USER A klickt auf "Mit FTAPI versenden" im Add-in
5. System zeigt Sicherheitsstufen-Auswahl
6. USER A wählt Sicherheitsstufe (1-4)
7. USER A definiert Gültigkeitsdauer (optional)
8. USER A klickt auf "Senden"
9. System verschlüsselt Dateien gemäß gewählter Sicherheitsstufe
10. System generiert sicheren Download-Link
11. USER B erhält E-Mail mit Download-Link
12. USER A erhält Versandbestätigung

**Alternative Szenarien:**

- 4a. USER A fügt Download-Button direkt in E-Mail ein
- 6a. Administrator hat Sicherheitsstufe vorgegeben

### 4.2 UC-002: Empfang mit Sicherheitsstufe 1

**Akteure:**

- USER B (Empfänger ohne FTAPI-Account)

**Hauptszenario:**

1. USER B erhält E-Mail mit sicherem Link
2. USER B klickt auf Download-Link
3. System öffnet Download-Seite im Browser
4. USER B lädt Dateien herunter
5. System sendet Download-Bestätigung an Versender

**Besonderheit:** Kein Login erforderlich, anonymer Download möglich

### 4.3 UC-003: Empfang mit Sicherheitsstufe 2

**Akteure:**

- USER B (Externer Empfänger ohne FTAPI-Account)

**Hauptszenario:**

1. USER B erhält E-Mail mit sicherem Link
2. USER B klickt auf Download-Link
3. System leitet zu Registrierungsseite weiter
4. System erstellt automatisch Gast-Account für USER B
5. USER B gibt E-Mail-Adresse ein
6. USER B erstellt Passwort
7. System sendet Bestätigungs-E-Mail
8. USER B meldet sich mit Gast-Account an
9. USER B lädt Dateien herunter
10. System sendet Download-Bestätigung an Versender

### 4.4 UC-004: Ende-zu-Ende-verschlüsselter Versand (Stufe 3)

**Akteure:**

- USER A (Versender mit SecuPass)
- USER B (Empfänger)

**Vorbedingungen:**

- USER A hat SecuPass eingerichtet
- Sensible Dateien (z.B. Verträge, Finanzdaten)

**Hauptszenario:**

1. USER A wählt Sicherheitsstufe 3 beim Versand
2. System verschlüsselt Dateien mit USER A's SecuPass-Key
3. USER B erhält verschlüsselte Zustellung
4. USER B richtet SecuPass ein (falls noch nicht vorhanden)
5. System informiert USER A über SecuPass-Aktivierung
6. USER A erteilt Freigabe für USER B
7. USER B kann Dateien mit eigenem SecuPass entschlüsseln
8. Dateien bleiben während gesamtem Prozess Ende-zu-Ende verschlüsselt

### 4.5 UC-005: Vollverschlüsselte Kommunikation (Stufe 4)

**Akteure:**

- USER A (Versender mit SecuPass)
- USER B (Empfänger mit SecuPass)

**Hauptszenario:**

1. USER A verfasst vertrauliche Nachricht mit sensiblen Anhängen
2. USER A wählt Sicherheitsstufe 4
3. System verschlüsselt Nachrichtentext UND Dateien
4. USER B erhält vollständig verschlüsselte E-Mail
5. USER B meldet sich an und gibt SecuPass ein
6. USER B klickt "Mail entschlüsseln" im Outlook Add-in
7. System entschlüsselt Nachrichtentext
8. USER B lädt und entschlüsselt Dateien
9. Kommunikation bleibt Zero-Knowledge (FTAPI hat keinen Zugriff)

### 4.6 UC-006: SubmitBox - Passiver Upload

**Akteure:**

- USER A (SubmitBox-Besitzer)
- USER B (Externer Einreicher)

**Hauptszenario:**

1. USER A integriert SubmitBox-Link in E-Mail-Signatur
2. USER B findet SubmitBox-Link
3. USER B klickt auf SubmitBox-Link
4. System öffnet SubmitBox-Interface
5. USER B gibt eigene E-Mail-Adresse ein
6. USER B klickt "Ticket erstellen"
7. System sendet Upload-Link an USER B
8. USER B öffnet E-Mail mit Upload-Link
9. USER B lädt Dateien hoch und fügt Nachricht hinzu
10. USER B klickt "Abschicken"
11. USER A erhält Benachrichtigung über Einreichung
12. USER B erhält Einreichungsbestätigung

### 4.7 UC-007: SubmitBox - Aktiver Upload via Outlook

**Akteure:**

- USER A (Anforderer mit Outlook)
- USER B (Externer Einreicher)

**Hauptszenario:**

1. USER A erstellt E-Mail in Outlook
2. USER A klickt auf SubmitBox-Button → "Upload-Button einfügen"
3. System fügt einmalig gültigen Upload-Link in E-Mail ein
4. USER A sendet E-Mail mit FTAPI
5. USER B erhält E-Mail mit persönlichem Upload-Link
6. USER B klickt auf Upload-Link
7. USER B lädt angeforderte Dateien hoch
8. USER A erhält verschlüsselte Dateien in Postfach
9. Beide erhalten Bestätigungen

### 4.8 UC-008: Administratorkonfiguration

**Akteur:**

- ADMIN (Administrator)

**Hauptszenario:**

1. ADMIN navigiert zu Administration → Konfiguration
2. ADMIN konfiguriert Zustellungseinstellungen:
    - Erlaubt/verbietet Zustellungen ohne Anhang
    - Setzt Standard-Sicherheitsstufe
    - Definiert maximale Dateigröße
    - Konfiguriert Löschfristen
3. ADMIN richtet Whitelist für erlaubte Empfänger ein
4. ADMIN aktiviert IP-Adressen-Protokollierung
5. ADMIN konfiguriert CC-Adressen für Compliance
6. Einstellungen gelten organisationsweit

### 4.9 UC-009: Compliance-Reporting

**Akteur:**

- ADMIN/COMPLIANCE-OFFICER

**Hauptszenario:**

1. ADMIN navigiert zu Berichte
2. ADMIN wählt "Zustellungen Download Report"
3. ADMIN definiert Zeitraum
4. System generiert Report mit:
    - Versender/Empfänger-Informationen
    - Download-Zeitpunkte
    - IP-Adressen (falls aktiviert)
    - Sicherheitsstufen
5. ADMIN exportiert Report für Audit/Compliance

### 4.10 UC-010: SecuPass-Einrichtung

**Akteur:**

- USER (Erstmalige SecuPass-Nutzung)

**Hauptszenario:**

1. USER erhält Ende-zu-Ende verschlüsselte Zustellung
2. System zeigt rotes "!" bei Benutzerkonto
3. USER klickt auf Benutzerkonto-Icon
4. USER wählt "SecuPass einrichten"
5. USER erstellt SecuPass (mit Vorgaben: Länge, Sonderzeichen)
6. USER bestätigt SecuPass
7. System aktiviert Ende-zu-Ende-Verschlüsselung
8. USER kann nun verschlüsselte Inhalte senden/empfangen

**Wichtig:** SecuPass kann NICHT zurückgesetzt werden!

## 5. Sicherheitsanforderungen

### 5.1 Verschlüsselung

- MUSS AES GCM Mode 256-Bit-Verschlüsselung verwenden
- MUSS Zero-Knowledge-Prinzip bei Stufe 3+4 einhalten
- MUSS Krypto-Agilität für zukünftige Standards unterstützen

### 5.2 Authentifizierung

- MUSS Zwei-Faktor-Authentifizierung unterstützen (optional)
- MUSS Single-Sign-On via SAML unterstützen
- MUSS Brute-Force-Schutz implementieren

### 5.3 Datenschutz

- MUSS DSGVO-konform sein
- MUSS "Made & Hosted in Germany" erfüllen
- MUSS automatische Datenlöschung nach Ablauf unterstützen

## 6. Performance Requirements

- System MUSS Dateien bis 100 GB in angemessener Zeit verarbeiten
- Upload MUSS in Segmenten erfolgen können
- System MUSS für mobile Endgeräte optimiert sein

## 7. Integrations-Requirements

### 7.1 E-Mail-Integration

- MUSS mit Microsoft Outlook 2016+ kompatibel sein
- MUSS Standard-E-Mail-Protokolle unterstützen
- MUSS Download-Links in E-Mails einbetten können

### 7.2 Browser-Kompatibilität

- MUSS mit aktuellen Versionen aller gängigen Browser funktionieren
- MUSS responsive Design für verschiedene Bildschirmgrößen bieten

## 8. Lizenzierung

- Basis-Funktionen (Web-Interface) in Grundlizenz enthalten
- Outlook Add-in als kostenpflichtige Erweiterung
- SubmitBox als kostenpflichtige Erweiterung
- Lizenzierung pro Benutzer/Gruppe