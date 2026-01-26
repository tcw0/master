## 1. Produktübersicht

### 1.1 Produktbeschreibung

- **Name**: FTAPI SecuRooms
- **Zweck**: Virtuelle Datenräume für sicheres und einfaches Filesharing
- **Vision**: Sensible Daten sicher online verwalten und gemeinsam daran arbeiten
- **Zielgruppe**: Unternehmen, Projektteams, Gesundheitswesen, Behörden

### 1.2 Kernfunktionalität

- Browserbasierte virtuelle Datenräume
- Sicheres Speichern, Teilen und gemeinsames Bearbeiten von Dateien
- Granulare Rollen- und Rechtevergabe
- Vollständige Transparenz und Nachvollziehbarkeit durch Audit Trail

## 2. Systemzugriff und Architektur

### 2.1 Zugriffsmöglichkeiten

- **Browserbasierter Zugriff**: Keine lokale Installation erforderlich
- **Unterstützte Browser**:
    - Google Chrome (aktuelle Version)
    - Safari (aktuelle Version)
    - Microsoft Edge (aktuelle Version)
    - Mozilla Firefox (aktuelle Version)
- **Gerätekompatibilität**:
    - Desktop/Laptop
    - Tablet
    - Smartphone
    - Optimiert für alle mobilen Endgeräte

### 2.2 Account-Typen

1. **Reguläre Benutzer-Accounts**
    - Vollwertiger Account mit allen Funktionen
    - Eigene Datenräume erstellen und verwalten
2. **Gast-Accounts**
    - Kostenloser Account für externe Nutzer
    - Zugriff nur auf freigegebene Datenräume
    - Automatische Erstellung bei Einladung

### 2.3 Registrierungsprozess

1. **Gast-Account Registrierung**
    - E-Mail mit Datenraum-Einladung erhalten
    - Button "Registrierung abschließen" klicken
    - Benutzername = E-Mail-Adresse (vorgegeben)
    - Passwort frei wählbar
    - Bestätigung per E-Mail

## 3. Sicherheitsarchitektur

### 3.1 Verschlüsselungsmethoden

### 3.1.1 Transportverschlüsselung

- **Standard**: TLS 1.3 für alle Datenübertragungen
- **Schutz**: Während der Übertragung ("Encryption-in-Transit")
- **Anwendung**: Automatisch für alle Datenräume

### 3.1.2 Serverseitige Verschlüsselung

- **Standard**: AES-256 GCM Mode Verschlüsselung
- **Speicherung**: Verschlüsselt auf Server ("Encryption-at-Rest")
- **Anwendung**: Für alle Datenräume

### 3.1.3 Ende-zu-Ende-Verschlüsselung (Optional)

- **Aktivierung**: Manuell pro Datenraum
- **Verschlüsselung**: Direkt im Browser mit SecuPass
- **Zero-Knowledge-Prinzip**: FTAPI hat keinen Zugriff auf Inhalte
- **Voraussetzung**: SecuPass-Key erforderlich

### 3.2 SecuPass-Verwaltung

### 3.2.1 SecuPass-Einrichtung

1. Benutzerverwaltung öffnen (rechts oben)
2. "SecuPass einrichten" klicken
3. SecuPass festlegen und bestätigen

### 3.2.2 SecuPass-Eigenschaften

- Sicherheitspasswort für Ver-/Entschlüsselung
- Einmalige Festlegung
- **WICHTIG**: Kann nicht zurückgesetzt werden
- Bei Verlust kein Zugriff auf E2E-verschlüsselte Datenräume

### 3.3 Compliance und Datenschutz

- **DSGVO-konform**: Vollständige Compliance
- **BSI-Standards**: Verschlüsselung nach BSI-Vorgaben
- **Datenhaltung**: 100% in Deutschland
- **Rechenzentrum**: Deutscher Betreiber

## 4. Funktionale Requirements

### 4.1 Datenraum-Management

### 4.1.1 Datenraum-Erstellung

- Neue Datenräume anlegen
- Namen und Beschreibung vergeben
- Verschlüsselungsoptionen wählen
- Initiale Zugriffsrechte festlegen

### 4.1.2 Datenraum-Struktur

- **Hierarchische Organisation**:
    - Datenräume (oberste Ebene)
    - Unterordner (ein-/ausklappbar)
    - Dateien
- **Sortieroptionen**:
    - Name (alphabetisch)
    - Dateigröße
    - Änderungsdatum

### 4.1.3 Datenraum-Verwaltung

- Datenräume umbenennen
- Beschreibungen ändern
- Löschfristen festlegen
- Datenräume löschen (nur Besitzer)

### 4.2 Datei-Management

### 4.2.1 Upload-Funktionen

- **Methoden**:
    - Drag & Drop
    - Upload-Button
    - Mehrfachauswahl möglich
- **Dateigröße**: Bis 100 GB pro Datei
- **Dateitypen**: Keine Einschränkungen (konfigurierbar)

### 4.2.2 Download-Funktionen

- Einzeldateien herunterladen
- Mehrfachauswahl für Download
- Ordner als ZIP herunterladen

### 4.2.3 Datei-Operationen

- Dateien verschieben
- Dateien löschen
- Dateien umbenennen
- Dateiversionierung

### 4.2.4 PDF-Kollaboration

- **PDF-Viewer im Browser**
- **Anmerkungen**: Direkt im Dokument
- **Kommentare**: Für andere Mitarbeiter sichtbar
- **Speicherung**: Automatisch mit Dokument

### 4.3 Zugriffsrollen und Berechtigungen

### 4.3.1 Rollendefinitionen

**Betrachter (ohne Herunterladen)**

- Datei ansehen
- Keine Download-Berechtigung
- Keine Bearbeitungsrechte

**Betrachter**

- Datei ansehen
- Datei herunterladen
- Keine Bearbeitungsrechte

**Bearbeiter**

- Datei ansehen
- Datei herunterladen
- Datei hochladen
- Datei verschieben
- Datei löschen
- Ordner erstellen
- Ordner löschen

**Besitzer**

- Alle Bearbeiter-Rechte
- Datenraum löschen
- Zugriffe verwalten
- Neue Nutzer einladen
- Rollen ändern
- Übersicht über Datei-Upload-Events und -zugriffe

### 4.3.2 Rechtevergabe

- E-Mail-basierte Einladung
- Rollenzuweisung bei Einladung
- Nachträgliche Rollenänderung möglich
- Mehrfachzuweisung von Rollen

### 4.4 Transparenz und Nachvollziehbarkeit

### 4.4.1 Audit Trail

- **Protokollierte Aktivitäten**:
    - Datei-Upload
    - Datei-Download
    - Datei-Ansicht
    - Änderungen
    - Löschungen
    - Zugriffsverwaltung
- **Informationen**:
    - Benutzer
    - Zeitstempel
    - Aktion
    - Betroffene Dateien/Ordner
- **Zugriff**: Nur für Besitzer sichtbar

### 4.4.2 Dateiversionierung

- Automatische Versionierung bei Änderungen
- Versionsverlauf einsehbar
- Alte Versionen wiederherstellen
- Versionsnummern und Zeitstempel

### 4.4.3 Aktivitätsbenachrichtigungen

- E-Mail-Benachrichtigungen bei:
    - Neuen Uploads
    - Änderungen
    - Freigaben
    - Downloads (optional)
- Konfigurierbare Benachrichtigungseinstellungen

### 4.5 Automatisierung und Regelwerk

### 4.5.1 Löschfristen

- **Automatische Löschung**: Nach festgelegtem Zeitraum
- **Konfiguration**: Pro Datenraum oder global
- **Compliance**: Unterstützung von DSGVO-Aufbewahrungsfristen
- **Benachrichtigung**: Vor Löschung (optional)

### 4.5.2 Zugriffsbeschränkungen

- Zeitbasierte Zugriffe (Ablaufdatum)
- IP-Beschränkungen (Admin-Funktion)
- Download-Limits (optional)

## 5. Administrative Requirements

### 5.1 Admin-Konsole

### 5.1.1 Zentrale Verwaltung

- Übersicht aller Datenräume
- Keine direkten Zugriffe auf Inhalte erforderlich
- Globale Einstellungen

### 5.1.2 Verfügbare Informationen

- **Datenraum-Details**:
    - Name des Datenraums
    - Besitzer (Liste)
    - Ende-zu-Ende-Verschlüsselung (Ja/Nein)
    - Anzahl Mitglieder
    - Anzahl Dateien
    - Gesamtdateigröße

### 5.1.3 Admin-Aktionen

- Besitzer-Rechte vergeben
- Datenräume löschen
- Berichte generieren
- Speicherplatz verwalten

### 5.2 Benutzerverwaltung

### 5.2.1 Gruppenverwaltung

- Benutzergruppen erstellen
- Rechte pro Gruppe definieren
- Benutzer zu Gruppen hinzufügen
- Mehrfachgruppenzugehörigkeit

### 5.2.2 Berechtigungsprinzipien

- **Segregation of Duties**: Aufgabentrennung
- **Principle of Least Privilege**: Minimale Berechtigung
- **Principle of Need to Know**: Notwendiges Wissen

### 5.2.3 Berechtigungsvererbung

- **Kumulative Berechtigungen**:
    - Whitelist/Blacklist für Dateitypen
    - IP-Adressen-Beschränkungen
    - Sicherheitsstufen
- **Prioritäre Berechtigungen**:
    - Nach Gruppenrang
    - Höhere Gruppe überschreibt niedrigere

### 5.3 Reporting und Monitoring

### 5.3.1 Reports

- Nutzungsstatistiken
- Speicherverbrauch
- Aktivitätsprotokolle
- Compliance-Reports

### 5.3.2 Monitoring

- Echtzeit-Überwachung
- Kapazitätsplanung
- Performance-Metriken
- Sicherheitsereignisse

### 5.4 Integration und APIs

### 5.4.1 REST API

- Vollständige API-Dokumentation
- Authentifizierung via Token
- CRUD-Operationen für Datenräume
- Benutzerverwaltung via API

### 5.4.2 Systemintegrationen

- **SecuFlows-Schnittstelle**
- **SSO (Single Sign-On)**
- **Zwei-Faktor-Authentifizierung (2FA)**

## 6. Technische Requirements

### 6.1 Performance

- **Dateigröße**: Bis 100 GB pro Datei
- **Speicher**: 300 GB inklusive (erweiterbar)
- **Unlimitierter Speicher**: Auf Wunsch verfügbar
- **Gleichzeitige Nutzer**: Skalierbar

### 6.2 Verfügbarkeit

- **Uptime**: 99% Verfügbarkeit
- **Wartungsfenster**: Angekündigt
- **Backup**: Automatische Sicherungen
- **Disaster Recovery**: Implementiert

### 6.3 Browser-Kompatibilität

- Keine Plugins erforderlich
- HTML5-Standard
- Responsive Design
- Progressive Web App fähig

## 7. Benutzerfreundlichkeit

### 7.1 User Interface

- **Intuitive Oberfläche**: Keine Schulung erforderlich
- **Übersichtliche Dateiverwaltung**: Direkt im Browser
- **Drag & Drop**: Für alle Dateioperationen
- **Kontextmenüs**: Rechtsklick-Funktionen

### 7.2 Onboarding

- **Schnelles Onboarding**: Keine Installation
- **Guided Tours**: Interaktive Einführung
- **Help Center**: Integrierte Hilfe
- **Video-Tutorials**: Verfügbar

### 7.3 Anpassung

- **Corporate Design**: CI-konforme Oberfläche
- **Mehrsprachigkeit**: Deutsch, Englisch, Französisch
- **Benutzerdefinierte Felder**: Erweiterbar
- **White-Label**: Option verfügbar

## 8. Support und Wartung

### 8.1 Support-Optionen

- **Deutscher Support**: Verfügbar
- **Support-Kanäle**: E-Mail, Telefon
- **SLA**: Definierte Reaktionszeiten
- **Dokumentation**: Umfassend

### 8.2 Wartung

- **Updates**: Automatisch
- **Keine Downtime**: Bei Updates
- **Feature-Releases**: Regelmäßig
- **Security-Patches**: Sofort

## 9. Implementierung

### 9.1 Rollout

- **Implementierungszeit**: Innerhalb von 24h
- **Keine IT-Ressourcen**: Erforderlich
- **Cloud-basiert**: Sofort verfügbar
- **Skalierbar**: Nach Bedarf

### 9.2 Migration

- **Datenimport**: Unterstützt
- **Bulk-Upload**: Verfügbar
- **Metadaten**: Erhaltung möglich
- **Rechte-Migration**: Unterstützt

## 10. Lizenzierung

### 10.1 Lizenzmodell

- **Faire Lizenzierung**: Für interne und externe Nutzer
- **Keine versteckten Kosten**: Transparente Preise
- **Skalierbar**: Nach Nutzerzahl
- **Speicher**: Flexibel erweiterbar

### 10.2 Inkludierte Leistungen

- 300 GB Speicher
- Unbegrenzte Gast-Accounts
- Alle Funktionen
- Support inklusive

## 11. Sicherheitsprinzipien und Best Practices

### 11.1 Datenschutz

- Ende-zu-Ende-Verschlüsselung für kritische Daten
- Regelmäßige Zugriffsprüfungen
- Minimale Berechtigungen vergeben
- Löschfristen implementieren

### 11.2 Compliance

- DSGVO-konforme Prozesse
- Audit-Trail aktivieren
- Regelmäßige Reports
- Dokumentation pflegen

### 11.3 Operationale Sicherheit

- Starke Passwörter erzwingen
- 2FA aktivieren
- IP-Beschränkungen nutzen
- Regelmäßige Schulungen

## 1. Datenraum-Verwaltung

### 1.1 Datenraum erstellen

- Neue virtuelle Datenräume anlegen
- Namen und Beschreibung festlegen
- Verschlüsselungsoptionen wählen (Standard oder Ende-zu-Ende)

### 1.2 Datenraum-Struktur

- Hierarchische Ordnerstruktur innerhalb der Datenräume
- Ordner erstellen, umbenennen und löschen
- Ein- und ausklappbare Unterordner für bessere Übersicht

### 1.3 Datenraum löschen

- Datenräume können nur vom Besitzer gelöscht werden
- Automatische Löschfristen konfigurierbar

## 2. Datei-Management

### 2.1 Datei-Upload

- Drag & Drop Funktion
- Upload-Button für Dateiauswahl
- Mehrfachauswahl von Dateien möglich
- Dateien bis 100 GB unterstützt

### 2.2 Datei-Download

- Einzelne Dateien herunterladen
- Mehrere Dateien auf einmal herunterladen
- Ordner als ZIP-Datei herunterladen

### 2.3 Datei-Operationen

- Dateien verschieben zwischen Ordnern
- Dateien löschen
- Dateien umbenennen
- Versionierung von Dateien

### 2.4 Datei-Ansicht

- Dateien direkt im Browser ansehen (ohne Download)
- PDF-Viewer integriert
- Unterstützung verschiedener Dateiformate

## 3. Benutzerverwaltung und Zugriffe

### 3.1 Benutzer-Accounts

- **Reguläre Accounts**: Vollwertige Benutzer mit eigenen Datenräumen
- **Gast-Accounts**: Kostenlose Accounts für externe Nutzer mit eingeschränkten Rechten

### 3.2 Registrierung

- E-Mail-basierte Registrierung
- Gast-Accounts werden automatisch bei Einladung erstellt
- Passwort selbst festlegen

### 3.3 Benutzer zu Datenräumen einladen

- Einladung per E-Mail versenden
- Rolle bei Einladung festlegen
- Mehrere Benutzer gleichzeitig einladen

## 4. Rollen und Berechtigungen

### 4.1 Rollendefinitionen

**Betrachter (ohne Download)**

- Dateien nur ansehen
- Kein Download möglich

**Betrachter (mit Download)**

- Dateien ansehen
- Dateien herunterladen

**Bearbeiter**

- Dateien ansehen und herunterladen
- Dateien hochladen
- Dateien verschieben und löschen
- Ordner erstellen und löschen

**Besitzer**

- Alle Bearbeiter-Rechte
- Datenraum löschen
- Benutzer einladen und entfernen
- Rollen ändern
- Audit-Trail einsehen

### 4.2 Rechteverwaltung

- Rollen pro Datenraum vergeben
- Nachträgliche Änderung von Rollen
- Benutzer aus Datenraum entfernen

## 5. Sicherheitsfunktionen

### 5.1 Verschlüsselung

- **Transportverschlüsselung**: TLS für alle Übertragungen
- **Serverseitige Verschlüsselung**: AES-256 GCM Mode für gespeicherte Daten
- **Ende-zu-Ende-Verschlüsselung**: Optional pro Datenraum aktivierbar

### 5.2 SecuPass

- SecuPass einrichten für Ende-zu-Ende-Verschlüsselung
- SecuPass in Benutzerverwaltung festlegen
- Warnung: SecuPass kann nicht zurückgesetzt werden

### 5.3 Authentifizierung

- Zwei-Faktor-Authentifizierung (2FA) optional
- SMS-TAN Verfahren
- Single Sign-On (SSO) via SAML

## 6. Kollaboration

### 6.1 PDF-Bearbeitung

- PDFs direkt im Browser annotieren
- Kommentare zu PDFs hinzufügen
- Anmerkungen für andere Benutzer sichtbar
- Änderungen automatisch speichern

### 6.2 Benachrichtigungen

- E-Mail-Benachrichtigungen bei neuen Uploads
- Benachrichtigungen bei Änderungen
- Aktivitätsbenachrichtigungen konfigurierbar

## 7. Transparenz und Nachvollziehbarkeit

### 7.1 Audit Trail

- Alle Aktivitäten werden protokolliert:
    - Datei-Uploads
    - Downloads
    - Ansichten
    - Änderungen
    - Löschungen
    - Rechtevergaben
- Zeitstempel und Benutzer werden erfasst
- Nur für Besitzer einsehbar

### 7.2 Aktivitätsübersicht

- Übersicht über alle Datei-Upload-Events
- Zugriffe auf Dateien nachvollziehen
- Chronologische Darstellung

## 8. Administration

### 8.1 Admin-Konsole

- Zentrale Verwaltung aller Datenräume
- Übersicht ohne direkten Zugriff auf Inhalte
- Folgende Informationen einsehbar:
    - Name des Datenraums
    - Liste der Besitzer
    - Ende-zu-Ende-Verschlüsselung (Ja/Nein)
    - Anzahl Mitglieder
    - Anzahl Dateien
    - Gesamtdateigröße

### 8.2 Admin-Funktionen

- Besitzer-Rechte vergeben
- Datenräume löschen
- Globale Einstellungen verwalten

## 9. Gruppenverwaltung

### 9.1 Gruppen anlegen

- Neue Gruppen erstellen
- Gruppenname und Beschreibung festlegen

### 9.2 Benutzer zu Gruppen zuweisen

- Benutzer werden bei Anlage einer Gruppe zugewiesen
- Benutzer per E-Mail oder Benutzername hinzufügen
- Übersicht der Gruppenmitglieder

### 9.3 Gruppenberechtigungen

- Features pro Gruppe aktivieren/deaktivieren
- Lizenzfreie und lizenzpflichtige Features unterscheiden
- Sicherheitseinstellungen pro Gruppe

### 9.4 Einschränkungen pro Gruppe

- Maximale Anhangsgröße für WebUpload festlegen
- Maximale Segmentgröße für Uploads
- Whitelist für Empfänger (Domains wie *@company.com)

## 10. Automatisierung

### 10.1 Löschfristen

- Automatische Löschfristen pro Datenraum
- Automatische Bereinigung konfigurieren
- DSGVO-konforme Aufbewahrungsfristen

### 10.2 Automatische Prozesse

- Virenscans beim Upload (G DATA Scanner)
- Automatische Benachrichtigungen
- Compliance-Prüfungen

## 11. Zugriffsmöglichkeiten

### 11.1 Browserbasiert

- Keine lokale Installation erforderlich
- Zugriff über alle gängigen Browser
- Responsive Design für mobile Geräte

### 11.2 Geräteunterstützung

- Desktop/Laptop
- Tablet
- Smartphone
- Plattformunabhängig

## 12. Integration

### 12.1 Microsoft Teams Integration

- SecuRooms in Teams einbinden

### 12.2 API-Schnittstelle

- REST API für Automatisierung
- Programmatischer Zugriff auf Funktionen

### 12.3 SecuFlows-Schnittstelle

- Integration mit FTAPI SecuFlows