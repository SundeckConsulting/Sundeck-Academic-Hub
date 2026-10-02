(function () {
    const DEFAULT_LANG = 'de';
    const AVAILABLE_LANGS = ['de', 'en'];

    const TRANSLATIONS = {
        de: {
            'Academic Hub': 'Academic Hub',
            'Student Portal': 'Studentenportal',
            'Teacher Portal': 'Lehrerportal',
            'Tenant Admin': 'Mandanten-Admin',
            'System Admin Login': 'System-Admin-Anmeldung',
            'Authorized personnel only': 'Nur autorisiertes Personal',
            'System Admin': 'System-Admin',
            'Sign Out': 'Abmelden',
            'Secure Sign Out': 'Sicher abmelden',
            'Passcode': 'Zugangscode',
            'Verify Identity': 'Identität prüfen',
            'Your session expired. Sign in again to continue.': 'Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an, um fortzufahren.',
            'Your session has expired.': 'Ihre Sitzung ist abgelaufen.',
            'Please sign in again to continue.': 'Bitte melden Sie sich erneut an, um fortzufahren.',
            'Sign in again': 'Erneut anmelden',
            'Welcome to your workspace': 'Willkommen in deinem Workspace',
            'Secure access for academic collaboration.': 'Sicherer Zugang für akademische Zusammenarbeit.',
            'University email': 'Universitäts-E-Mail',
            'Verification code': 'Verifizierungscode',
            'Check your email': 'Prüfen Sie Ihre E-Mail',
            'We sent a secure code to': 'Wir haben einen sicheren Code gesendet an',
            'Send secure code': 'Sicheren Code senden',
            'Authenticate': 'Authentifizieren',
            'Use another email': 'Andere E-Mail verwenden',
            'Code expires in 10 minutes and can only be used once.': 'Der Code läuft in 10 Minuten ab und kann nur einmal verwendet werden.',
            'Before you continue': 'Bevor Sie fortfahren',
            'Privacy and permissions': 'Datenschutz und Berechtigungen',
            'Review the privacy notice and Sundeck may use your project work for marketing.': 'Bitte lesen Sie den Datenschutzhinweis und beachten Sie, dass Sundeck Ihre Projektarbeit für Marketingzwecke nutzen kann.',
            'Required': 'Erforderlich',
            'Course privacy notice': 'Datenschutzhinweis für den Kurs',
            'Read the full privacy notice': 'Vollständigen Datenschutzhinweis lesen',
            'I have read the privacy notice.': 'Ich habe den Datenschutzhinweis gelesen.',
            'Optional': 'Optional',
            'Marketing permission': 'Marketing-Erlaubnis',
            'Covers your original project work only. Identifying details must be removed before use; other people\'s work or contributions are not included.': 'Gilt nur für Ihre originalen Projektarbeiten. Identifizierende Details müssen vor der Nutzung entfernt werden; andere Arbeiten oder Beiträge sind nicht enthalten.',
            'I allow Sundeck to reproduce, adapt, and publish my original project work on its website, social media, and marketing materials after identifying details are removed. This does not allow use of my name, image, voice, or email.': 'Ich erlaube Sundeck, meine originalen Projektarbeiten nach Entfernung identifizierender Details auf der Website, in sozialen Medien und in Marketingmaterialien zu reproduzieren, anzupassen und zu veröffentlichen. Dies erlaubt keine Nutzung meines Namens, meiner Bild-, Sprach- oder E-Mail-Daten.',
            'Select all': 'Alle auswählen',
            'Selects both choices. You can also set them separately.': 'Wählt beide Optionen aus. Sie können sie auch getrennt festlegen.',
            'Marketing permission is optional and can be withdrawn later.': 'Die Marketing-Erlaubnis ist optional und kann später widerrufen werden.',
            'Cancel': 'Abbrechen',
            'Continue to workspace': 'Weiter zum Workspace',
            'Saving...': 'Wird gespeichert...',
            'Secure Academic Workspace': 'Sicherer akademischer Workspace',
            'Enterprise-grade collaboration platform for University project deliverables. Fully GDPR compliant, secure, and isolated from core CRM environments.': 'Unternehmensgerechte Kollaborationsplattform für Universitäts-Projektleistungen. Vollständig DSGVO-konform, sicher und von den Kern-CRM-Umgebungen getrennt.',
            'Access Portal': 'Portal öffnen',
            'Student Portal': 'Studentenportal',
            'Teacher Portal': 'Lehrerportal',
            'Tenant Admin': 'Mandanten-Admin',
            'Access Admin': 'Admin öffnen',
            'GDPR Compliance Notice:': 'DSGVO-Hinweis:',
            'This academic portal uses essential cookies and secure tokens solely for authentication and session management. By continuing to use this service, you consent to our data processing terms.': 'Dieses akademische Portal verwendet ausschließlich essenzielle Cookies und sichere Tokens für Authentifizierung und Sitzungsverwaltung. Durch die weitere Nutzung stimmen Sie unseren Datenschutzbedingungen zu.',
            'Decline': 'Ablehnen',
            'Accept & Continue': 'Akzeptieren & Fortfahren',
            'Privacy Policy': 'Datenschutzerklärung',
            'Terms of Service': 'Nutzungsbedingungen',
            'GDPR Information': 'DSGVO-Informationen',
            'Student sign in': 'Student-Anmeldung',
            'Professor Access': 'Professor-Zugang',
            'Sundeck Organizations': 'Sundeck-Organisationen',
            'Manage provisioned universities and schools.': 'Verwalten Sie bereitgestellte Universitäten und Schulen.',
            'New Organization Name...': 'Neuer Organisationsname...',
            '+ New Organization': '+ Neue Organisation',
            'Switch University': 'Universität wechseln',
            'Project Status & Workflow Oversight': 'Projektstatus und Workflow-Übersicht',
            'Total Teams': 'Teams gesamt',
            'Total Tasks': 'Aufgaben gesamt',
            'Deliverables': 'Ergebnisse',
            'Dependencies': 'Abhängigkeiten',
            'No organizations provisioned. Create one above.': 'Keine Organisationen eingerichtet. Erstellen Sie oben eine.',
            'Project Control Center': 'Projektsteuerungszentrum',
            'Manage &rarr;': 'Verwalten →',
            'Legal & Compliance Hub': 'Rechts- und Compliance-Center',
            'Draft notice: not ready for production.': 'Entwurfshinweis: noch nicht produktionsreif.',
            'The controller identity and contact, the university/Sundeck roles, legal bases, retention periods, and processor details must be confirmed and added by the responsible privacy adviser before this notice is relied on.': 'Identität und Kontaktdaten des Verantwortlichen, die Rollen von Universität/Sundeck, Rechtsgrundlagen, Aufbewahrungsfristen und Details der Auftragsverarbeiter müssen vor der Nutzung dieses Hinweises vom zuständigen Datenschutzberater bestätigt und ergänzt werden.',
            'Student Privacy Information': 'Datenschutzinformationen für Studierende',
            'Course and Optional Marketing Use': 'Kurs- und optionale Marketingnutzung',
            'Return to Hub': 'Zurück zum Hub',
            'Deutsch': 'Deutsch',
            'English': 'English',
            'Student sign in': 'Student-Anmeldung',
            'University email': 'Universitäts-E-Mail',
            'Professor access for reviewing student submissions, auditing files, and overseeing progress.': 'Professoren-Zugang zum Prüfen von Studenteneinsendungen, Auditieren von Dateien und Überwachen des Fortschritts.',
            'Securely authenticate to upload assignments, project files, and review your team\'s deliverables.': 'Authentifizieren Sie sich sicher, um Aufgaben, Projektdateien hochzuladen und die Ergebnisse Ihres Teams zu prüfen.',
            'Internal organization tools to configure students, map teams, and manage tenant compliance data.': 'Interne Organisationswerkzeuge zur Konfiguration von Studierenden, zum Zuordnen von Teams und zum Verwalten von Mandanten-Compliance-Daten.',
            'Authorized personnel only': 'Nur autorisiertes Personal',
            'Your session has expired.': 'Ihre Sitzung ist abgelaufen.',
            'Employee access only': 'Nur Mitarbeiterzugang',
            'Research Portal': 'Forschungsportal',
            'Manage your research and projects': 'Verwalten Sie Ihre Forschung und Projekte',
            'Continue': 'Weiter',
            'Delete Organization': 'Organisation löschen',
            'Projects': 'Projekte',
            'Teachers': 'Lehrkräfte',
            'No organizations provisioned. Create one above.': 'Keine Organisationen eingerichtet. Erstellen Sie oben eine.',
            'Sundeck Consulting': 'Sundeck Consulting',
            'All rights reserved. Academic Hub Project.': 'Alle Rechte vorbehalten. Academic Hub Projekt.',
            'The controller and lawful basis for each purpose must be confirmed with the participating institution before production use.': 'Verantwortlicher und rechtliche Grundlage für jeden Zweck müssen mit der teilnehmenden Institution vor der produktiven Nutzung bestätigt werden.'
        },
        en: {
            'Academic Hub': 'Academic Hub',
            'Studentenportal': 'Student Portal',
            'Lehrerportal': 'Teacher Portal',
            'Mandanten-Admin': 'Tenant Admin',
            'System-Admin-Anmeldung': 'System Admin Login',
            'Nur autorisiertes Personal': 'Authorized personnel only',
            'System-Admin': 'System Admin',
            'Abmelden': 'Sign Out',
            'Sicher abmelden': 'Secure Sign Out',
            'Zugangscode': 'Passcode',
            'Identität prüfen': 'Verify Identity',
            'Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an, um fortzufahren.': 'Your session expired. Sign in again to continue.',
            'Ihre Sitzung ist abgelaufen.': 'Your session has expired.',
            'Bitte melden Sie sich erneut an, um fortzufahren.': 'Please sign in again to continue.',
            'Erneut anmelden': 'Sign in again',
            'Willkommen in deinem Workspace': 'Welcome to your workspace',
            'Sicherer Zugang für akademische Zusammenarbeit.': 'Secure access for academic collaboration.',
            'Universitäts-E-Mail': 'University email',
            'Verifizierungscode': 'Verification code',
            'Prüfen Sie Ihre E-Mail': 'Check your email',
            'Wir haben einen sicheren Code gesendet an': 'We sent a secure code to',
            'Sicheren Code senden': 'Send secure code',
            'Authentifizieren': 'Authenticate',
            'Andere E-Mail verwenden': 'Use another email',
            'Der Code läuft in 10 Minuten ab und kann nur einmal verwendet werden.': 'Code expires in 10 minutes and can only be used once.',
            'Bevor Sie fortfahren': 'Before you continue',
            'Datenschutz und Berechtigungen': 'Privacy and permissions',
            'Bitte lesen Sie den Datenschutzhinweis und beachten Sie, dass Sundeck Ihre Projektarbeit für Marketingzwecke nutzen kann.': 'Review the privacy notice and Sundeck may use your project work for marketing.',
            'Erforderlich': 'Required',
            'Datenschutzhinweis für den Kurs': 'Course privacy notice',
            'Vollständigen Datenschutzhinweis lesen': 'Read the full privacy notice',
            'Ich habe den Datenschutzhinweis gelesen.': 'I have read the privacy notice.',
            'Optional': 'Optional',
            'Marketing-Erlaubnis': 'Marketing permission',
            'Gilt nur für Ihre originalen Projektarbeiten. Identifizierende Details müssen vor der Nutzung entfernt werden; andere Arbeiten oder Beiträge sind nicht enthalten.': 'Covers your original project work only. Identifying details must be removed before use; other people\'s work or contributions are not included.',
            'Ich erlaube Sundeck, meine originalen Projektarbeiten nach Entfernung identifizierender Details auf der Website, in sozialen Medien und in Marketingmaterialien zu reproduzieren, anzupassen und zu veröffentlichen. Dies erlaubt keine Nutzung meines Namens, meiner Bild-, Sprach- oder E-Mail-Daten.': 'I allow Sundeck to reproduce, adapt, and publish my original project work on its website, social media, and marketing materials after identifying details are removed. This does not allow use of my name, image, voice, or email.',
            'Alle auswählen': 'Select all',
            'Wählt beide Optionen aus. Sie können sie auch getrennt festlegen.': 'Selects both choices. You can also set them separately.',
            'Die Marketing-Erlaubnis ist optional und kann später widerrufen werden.': 'Marketing permission is optional and can be withdrawn later.',
            'Abbrechen': 'Cancel',
            'Weiter zum Workspace': 'Continue to workspace',
            'Wird gespeichert...': 'Saving...',
            'Sicherer akademischer Workspace': 'Secure Academic Workspace',
            'Unternehmensgerechte Kollaborationsplattform für Universitäts-Projektleistungen. Vollständig DSGVO-konform, sicher und von den Kern-CRM-Umgebungen getrennt.': 'Enterprise-grade collaboration platform for University project deliverables. Fully GDPR compliant, secure, and isolated from core CRM environments.',
            'Portal öffnen': 'Access Portal',
            'Studentenportal': 'Student Portal',
            'Lehrerportal': 'Teacher Portal',
            'Mandanten-Admin': 'Tenant Admin',
            'Admin öffnen': 'Access Admin',
            'DSGVO-Hinweis:': 'GDPR Compliance Notice:',
            'Dieses akademische Portal verwendet ausschließlich essenzielle Cookies und sichere Tokens für Authentifizierung und Sitzungsverwaltung. Durch die weitere Nutzung stimmen Sie unseren Datenschutzbedingungen zu.': 'This academic portal uses essential cookies and secure tokens solely for authentication and session management. By continuing to use this service, you consent to our data processing terms.',
            'Ablehnen': 'Decline',
            'Akzeptieren & Fortfahren': 'Accept & Continue',
            'Datenschutzerklärung': 'Privacy Policy',
            'Nutzungsbedingungen': 'Terms of Service',
            'DSGVO-Informationen': 'GDPR Information',
            'Student-Anmeldung': 'Student sign in',
            'Professor-Zugang': 'Professor Access',
            'Sundeck-Organisationen': 'Sundeck Organizations',
            'Verwalten Sie bereitgestellte Universitäten und Schulen.': 'Manage provisioned universities and schools.',
            'Neuer Organisationsname...': 'New Organization Name...',
            '+ Neue Organisation': '+ New Organization',
            'Universität wechseln': 'Switch University',
            'Projektstatus und Workflow-Übersicht': 'Project Status & Workflow Oversight',
            'Teams gesamt': 'Total Teams',
            'Aufgaben gesamt': 'Total Tasks',
            'Ergebnisse': 'Deliverables',
            'Abhängigkeiten': 'Dependencies',
            'Keine Organisationen eingerichtet. Erstellen Sie oben eine.': 'No organizations provisioned. Create one above.',
            'Verwalten →': 'Manage &rarr;',
            'Rechts- und Compliance-Center': 'Legal & Compliance Hub',
            'Entwurfshinweis: noch nicht produktionsreif.': 'Draft notice: not ready for production.',
            'Identität und Kontaktdaten des Verantwortlichen, die Rollen von Universität/Sundeck, Rechtsgrundlagen, Aufbewahrungsfristen und Details der Auftragsverarbeiter müssen vor der Nutzung dieses Hinweises vom zuständigen Datenschutzberater bestätigt und ergänzt werden.': 'The controller identity and contact, the university/Sundeck roles, legal bases, retention periods, and processor details must be confirmed and added by the responsible privacy adviser before this notice is relied on.',
            'Datenschutzinformationen für Studierende': 'Student Privacy Information',
            'Kurs- und optionale Marketingnutzung': 'Course and Optional Marketing Use',
            'Zurück zum Hub': 'Return to Hub',
            'Deutsch': 'Deutsch',
            'English': 'English',
            'Professoren-Zugang zum Prüfen von Studenteneinsendungen, Auditieren von Dateien und Überwachen des Fortschritts.': 'Professor access for reviewing student submissions, auditing files, and overseeing progress.',
            'Authentifizieren Sie sich sicher, um Aufgaben, Projektdateien hochzuladen und die Ergebnisse Ihres Teams zu prüfen.': 'Securely authenticate to upload assignments, project files, and review your team\'s deliverables.',
            'Interne Organisationswerkzeuge zur Konfiguration von Studierenden, zum Zuordnen von Teams und zum Verwalten von Mandanten-Compliance-Daten.': 'Internal organization tools to configure students, map teams, and manage tenant compliance data.',
            'Nur Mitarbeiterzugang': 'Employee access only',
            'Forschungsportal': 'Research Portal',
            'Verwalten Sie Ihre Forschung und Projekte': 'Manage your research and projects',
            'Weiter': 'Continue',
            'Organisation löschen': 'Delete Organization',
            'Projekte': 'Projects',
            'Lehrkräfte': 'Teachers',
            'Alle Rechte vorbehalten. Academic Hub Projekt.': 'All rights reserved. Academic Hub Project.',
            'Verantwortlicher und rechtliche Grundlage für jeden Zweck müssen mit der teilnehmenden Institution vor der produktiven Nutzung bestätigt werden.': 'The controller and lawful basis for each purpose must be confirmed with the participating institution before production use.'
        }
    };

    const EXTRA_TRANSLATIONS = {
        'System Operational': 'System betriebsbereit',
        'ROOT': 'WURZEL',
        'Project Control Center': 'Projekt-Kontrollzentrum',
        'Back to Dashboard': 'Zurück zum Dashboard',
        'Back to Projects': 'Zurück zu den Projekten',
        'No projects created yet.': 'Es wurden noch keine Projekte erstellt.',
        'No teachers provisioned yet.': 'Es wurden noch keine Lehrkräfte eingerichtet.',
        'Select a project...': 'Projekt auswählen ...',
        'No projects assigned': 'Keine Projekte zugewiesen',
        'You have not been assigned to any projects yet.': 'Ihnen wurden noch keine Projekte zugewiesen.',
        'My Assigned Projects': 'Meine zugewiesenen Projekte',
        'Team Workspace': 'Team-Arbeitsbereich',
        'Your project workspace': 'Ihr Projektarbeitsbereich',
        'Your team': 'Ihr Team',
        'Team members': 'Teammitglieder',
        'Team Members': 'Teammitglieder',
        'No team members are listed yet.': 'Es sind noch keine Teammitglieder aufgeführt.',
        'No members found.': 'Keine Mitglieder gefunden.',
        'My Tasks': 'Meine Aufgaben',
        'My Deliverables': 'Meine Arbeitsergebnisse',
        'Tasks & Dependencies': 'Aufgaben und Abhängigkeiten',
        'Work Packages': 'Arbeitspakete',
        'No activities defined': 'Keine Aktivitäten definiert',
        'No tasks defined': 'Keine Aufgaben definiert',
        'No files submitted yet.': 'Es wurden noch keine Dateien eingereicht.',
        'Files submitted by your team.': 'Dateien, die Ihr Team eingereicht hat.',
        'No resources have been shared in this folder yet.': 'In diesem Ordner wurden noch keine Ressourcen geteilt.',
        'This folder is empty': 'Dieser Ordner ist leer',
        'No comments yet. Start the discussion!': 'Noch keine Kommentare. Starten Sie die Diskussion!',
        'No comments yet. Be the first to share your thoughts!': 'Noch keine Kommentare. Teilen Sie als Erste oder Erster Ihre Gedanken!',
        'No pending dependencies.': 'Keine offenen Abhängigkeiten.',
        'No teams are currently waiting for your work.': 'Derzeit wartet kein Team auf Ihre Arbeit.',
        'Select Project...': 'Projekt auswählen ...',
        'Select Team': 'Team auswählen',
        'Select Activity': 'Aktivität auswählen',
        'Select Work Package': 'Arbeitspaket auswählen',
        'Select internal task': 'Interne Aufgabe auswählen',
        'Select...': 'Auswählen ...',
        'Project Name': 'Projektname',
        'Project name': 'Projektname',
        'Project description': 'Projektbeschreibung',
        'Team Name': 'Teamname',
        'Team name': 'Teamname',
        'Team project': 'Teamprojekt',
        'Task Name': 'Aufgabenname',
        'Teacher Name': 'Name der Lehrkraft',
        'Teacher name': 'Name der Lehrkraft',
        'Teacher email': 'E-Mail-Adresse der Lehrkraft',
        'Student name': 'Name der studierenden Person',
        'Student email': 'E-Mail-Adresse der studierenden Person',
        'Full Name': 'Vollständiger Name',
        'Email Address': 'E-Mail-Adresse',
        'Description (Optional)': 'Beschreibung (optional)',
        'Expected Date': 'Voraussichtliches Datum',
        'Expected by:': 'Erwartet bis:',
        'Start Date': 'Startdatum',
        'End Date': 'Enddatum',
        'Overall Progress': 'Gesamtfortschritt',
        'At Risk': 'Gefährdet',
        'In Progress': 'In Bearbeitung',
        'Not Started': 'Nicht begonnen',
        'Under Review': 'Wird überprüft',
        'Revision Required': 'Überarbeitung erforderlich',
        'Waiting For': 'Wartet auf',
        'Unassigned': 'Nicht zugewiesen',
        'None assigned': 'Niemandem zugewiesen',
        'Not specified': 'Nicht angegeben',
        'Dates TBD': 'Termine noch offen',
        'Actions': 'Aktionen',
        'Add': 'Hinzufügen',
        'Create': 'Erstellen',
        'Save': 'Speichern',
        'Save Changes': 'Änderungen speichern',
        'Save & Notify Affected Teams': 'Speichern und betroffene Teams benachrichtigen',
        'Close': 'Schließen',
        'Close Details': 'Details schließen',
        'Delete Permanently': 'Dauerhaft löschen',
        'Remove': 'Entfernen',
        'Rename': 'Umbenennen',
        'Download': 'Herunterladen',
        'Post': 'Veröffentlichen',
        'Done': 'Fertig',
        'Create Project': 'Projekt erstellen',
        'Create Team': 'Team erstellen',
        'Create Task': 'Aufgabe erstellen',
        'Create Activity': 'Aktivität erstellen',
        'Create Package': 'Paket erstellen',
        'Add Task': 'Aufgabe hinzufügen',
        'Add Activity': 'Aktivität hinzufügen',
        'Add Member': 'Mitglied hinzufügen',
        'Add Teacher': 'Lehrkraft hinzufügen',
        'Register Student': 'Studierende Person registrieren',
        'Assign Projects': 'Projekte zuweisen',
        'Assigned Teachers': 'Zugewiesene Lehrkräfte',
        'Provision Teacher': 'Lehrkraft einrichten',
        'Filter by Project': 'Nach Projekt filtern',
        'Choose file': 'Datei auswählen',
        'Upload File': 'Datei hochladen',
        'Upload file': 'Datei hochladen',
        'Upload deliverable': 'Arbeitsergebnis hochladen',
        'Uploading...': 'Wird hochgeladen ...',
        'Uploading file…': 'Datei wird hochgeladen …',
        'File uploaded successfully': 'Datei erfolgreich hochgeladen',
        'Drag and drop a file here': 'Ziehen Sie eine Datei hierher oder legen Sie sie hier ab',
        'or choose a file from your device': 'oder wählen Sie eine Datei von Ihrem Gerät aus',
        'Write a comment...': 'Kommentar schreiben ...',
        'Privacy choices': 'Datenschutzeinstellungen',
        'Privacy notice:': 'Datenschutzhinweis:',
        'Marketing permission (work only; no identifying details):': 'Marketing-Einwilligung (nur Arbeitsergebnisse, keine identifizierenden Angaben):',
        'Optional notes...': 'Optionale Hinweise ...',
        'Folder Name': 'Ordnername',
        'Folder name': 'Ordnername',
        'New Folder': 'Neuer Ordner',
        'Create New Folder': 'Neuen Ordner erstellen',
        'New name...': 'Neuer Name ...',
        'This action cannot be undone.': 'Diese Aktion kann nicht rückgängig gemacht werden.',
        'Request Dependency': 'Abhängigkeit anfragen',
        'Send Dependency Request': 'Anfrage zur Abhängigkeit senden',
        'Confirm Dependency': 'Abhängigkeit bestätigen',
        'Request a deliverable or output from another team. They will map your request to their internal tasks.': 'Fordern Sie ein Arbeitsergebnis von einem anderen Team an. Das Team ordnet Ihre Anfrage seinen internen Aufgaben zu.',
        'Request something from another team if you need their work to continue.': 'Fordern Sie etwas von einem anderen Team an, wenn dessen Arbeit für Ihren Fortschritt erforderlich ist.',
        'Work required from other teams to continue.': 'Arbeit, die für den Fortschritt von anderen Teams benötigt wird.',
        'Requests from Other Teams': 'Anfragen anderer Teams',
        'Other Teams Need From Us': 'Was andere Teams von uns benötigen',
        'I Need From Other Teams': 'Was ich von anderen Teams benötige',
        'Incoming Requests (Requests directed TO this team)': 'Eingehende Anfragen (an dieses Team gerichtet)',
        'Outgoing Requests (I Need From Other Teams)': 'Ausgehende Anfragen (ich benötige etwas von anderen Teams)',
        'What do you need?': 'Was benötigen Sie?',
        'Why?': 'Warum?',
        'Which of your tasks will provide this output?': 'Welche Ihrer Aufgaben liefert dieses Ergebnis?',
        'I need something from:': 'Ich benötige etwas von:',
        'Click to Fulfill': 'Zum Erfüllen klicken',
        'Fulfill Request': 'Anfrage erfüllen',
        'Mapping...': 'Wird zugeordnet ...',
        'Requesting...': 'Anfrage wird gesendet ...',
        'Project Files': 'Projektdateien',
        'Project Resources': 'Projektressourcen',
        'Shared with every team in a project': 'Mit allen Teams eines Projekts geteilt',
        'Upload briefs, templates, and reference files to share them with all teams in this project.': 'Laden Sie Briefings, Vorlagen und Referenzdateien hoch, um sie mit allen Teams dieses Projekts zu teilen.',
        'Add briefs, templates, and reference files for all teams in the selected project': 'Fügen Sie Briefings, Vorlagen und Referenzdateien für alle Teams des ausgewählten Projekts hinzu',
        'Describe the purpose of this work package...': 'Beschreiben Sie den Zweck dieses Arbeitspakets ...',
        'What are we doing in this activity?': 'Was machen wir in dieser Aktivität?',
        'Provided for your project': 'Für Ihr Projekt bereitgestellt',
        'No description provided.': 'Keine Beschreibung vorhanden.',
        'No specific reason provided.': 'Keine konkrete Begründung angegeben.',
        'Failed to create task': 'Aufgabe konnte nicht erstellt werden',
        'Failed to save task': 'Aufgabe konnte nicht gespeichert werden',
        'Failed to create dependency.': 'Abhängigkeit konnte nicht erstellt werden.',
        'Enter email': 'E-Mail-Adresse eingeben',
        'Please enter your email.': 'Bitte geben Sie Ihre E-Mail-Adresse ein.',
        'Please enter the OTP.': 'Bitte geben Sie den Einmalcode ein.',
        'Name and email are required': 'Name und E-Mail-Adresse sind erforderlich',
        'Unable to load your team': 'Ihr Team konnte nicht geladen werden',
        'Unable to load privacy choices': 'Datenschutzeinstellungen konnten nicht geladen werden',
        'Unable to save privacy choices': 'Datenschutzeinstellungen konnten nicht gespeichert werden',
        'Unable to load folders': 'Ordner konnten nicht geladen werden',
        'Unable to delete resource': 'Ressource konnte nicht gelöscht werden',
        'Unable to download resource': 'Ressource konnte nicht heruntergeladen werden',
        'Unable to load comments': 'Kommentare konnten nicht geladen werden',
        'Unable to post comment': 'Kommentar konnte nicht veröffentlicht werden',
        'Unable to update project': 'Projekt konnte nicht aktualisiert werden',
        'Error creating folder': 'Fehler beim Erstellen des Ordners',
        'Error saving folder': 'Fehler beim Speichern des Ordners',
        'Error deleting item': 'Fehler beim Löschen des Elements',
        'Remove teacher from project?': 'Lehrkraft aus dem Projekt entfernen?',
        'For your security, you will be signed out in': 'Zu Ihrer Sicherheit werden Sie abgemeldet in',
        'Your session expires in': 'Ihre Sitzung läuft ab in',
        'Session expiring soon': 'Ihre Sitzung läuft bald ab',
        'Stay signed in': 'Angemeldet bleiben',
        'Stay signed in to continue working.': 'Bleiben Sie angemeldet, um weiterzuarbeiten.',
        'Please keep this window open': 'Bitte lassen Sie dieses Fenster geöffnet',
        'Organization logo': 'Organisationslogo',
        'Academic Hub home': 'Startseite des Academic Hub',
        'Academic Hub homepage': 'Startseite des Academic Hub',
        'Secure Academic Workspace': 'Sicherer akademischer Arbeitsbereich',
        'Student Privacy Information': 'Datenschutzinformationen für Studierende',
        'Course and Optional Marketing Use': 'Kursbezogene und optionale Marketingnutzung',
        'The Academic Hub processes account details such as name and university email, login and session information, and files and metadata submitted for course projects. These data are used to provide the student portal, administer course projects, review deliverables, and protect the service. The controller and lawful basis for each purpose must be confirmed with the participating institution before production use.': 'Der Academic Hub verarbeitet Kontodaten wie Name und Hochschul-E-Mail-Adresse, Anmelde- und Sitzungsinformationen sowie Dateien und Metadaten, die für Kursprojekte eingereicht werden. Diese Daten werden verwendet, um das Studierendenportal bereitzustellen, Kursprojekte zu verwalten, Arbeitsergebnisse zu prüfen und den Dienst zu schützen. Verantwortlicher und Rechtsgrundlage für jeden Zweck müssen vor dem produktiven Einsatz mit der teilnehmenden Institution abgestimmt werden.',
        'Currently, uploaded files are written to the Academic Hub application\'s local server filesystem, while file metadata is stored in the Academic Hub SQLite database. This deployment does not upload student files to a Contabo storage bucket. The hosting location, authorized recipients, any processors, and applicable retention periods must be confirmed and documented before launch.': 'Derzeit werden hochgeladene Dateien im lokalen Server-Dateisystem der Academic-Hub-Anwendung gespeichert; Dateimetadaten werden in der SQLite-Datenbank des Academic Hub abgelegt. Bei dieser Bereitstellung werden Studierendendateien nicht in einen Contabo-Speicher übertragen. Hosting-Standort, berechtigte Empfänger, etwaige Auftragsverarbeiter und geltende Aufbewahrungsfristen müssen vor dem Start bestätigt und dokumentiert werden.',
        'Before publication, complete this notice with the controller\'s legal name and contact details, the data protection contact, purposes and lawful bases, recipients, retention periods, international transfer details if applicable, and how students can exercise their rights or complain to a supervisory authority.': 'Ergänzen Sie diesen Hinweis vor der Veröffentlichung um den rechtlichen Namen und die Kontaktdaten des Verantwortlichen, die Datenschutzkontaktstelle, Zwecke und Rechtsgrundlagen, Empfänger, Aufbewahrungsfristen, gegebenenfalls Angaben zu internationalen Übermittlungen sowie Informationen dazu, wie Studierende ihre Rechte ausüben oder sich bei einer Aufsichtsbehörde beschweren können.',
        'Course administration and review are separate from optional marketing use. Students may decline marketing permission without affecting course access or assessment. The current draft marketing permission is limited to student-created work after personal and identifying details have been removed; it does not permit marketing use of a student\'s name, image, voice, email, or other identifying personal data. Third-party material and other contributors\' work are not covered. Uploading work alone does not transfer its copyright to Sundeck Consulting. Have the final scope and wording reviewed by the responsible privacy and legal advisers before production use.': 'Kursverwaltung und Bewertung sind von der optionalen Marketingnutzung getrennt. Studierende können eine Marketing-Einwilligung ablehnen, ohne dass sich dies auf den Kurszugang oder die Bewertung auswirkt. Die aktuelle Entwurfsfassung der Marketing-Einwilligung beschränkt sich auf von Studierenden erstellte Arbeiten, nachdem persönliche und identifizierende Angaben entfernt wurden. Sie erlaubt keine Marketingnutzung des Namens, Bildes, der Stimme, E-Mail-Adresse oder anderer identifizierender personenbezogener Daten einer studierenden Person. Materialien Dritter und Arbeiten anderer Mitwirkender sind nicht eingeschlossen. Durch das Hochladen einer Arbeit werden keine Urheberrechte auf Sundeck Consulting übertragen. Lassen Sie den endgültigen Umfang und Wortlaut vor dem produktiven Einsatz von den zuständigen Datenschutz- und Rechtsberatern prüfen.',
        'All rights reserved.': 'Alle Rechte vorbehalten.',
        '© 2026 Sundeck Consulting. All rights reserved.': '© 2026 Sundeck Consulting. Alle Rechte vorbehalten.',
        '© 2026 Sundeck Consulting. All rights reserved. Academic Hub Project.': '© 2026 Sundeck Consulting. Alle Rechte vorbehalten. Academic-Hub-Projekt.',
        'Professor access for reviewing student submissions, auditing files, and overseeing progress.': 'Professorenzugang zum Prüfen von Studierendenabgaben und Dateien sowie zur Überwachung des Fortschritts.',
        'Securely authenticate to upload assignments, project files, and review your team\'s deliverables.': 'Melden Sie sich sicher an, um Aufgaben und Projektdateien hochzuladen und die Arbeitsergebnisse Ihres Teams zu prüfen.',
        'Internal organization tools to configure students, map teams, and manage tenant compliance data.': 'Interne Organisationswerkzeuge zum Einrichten von Studierenden, Zuordnen von Teams und Verwalten der Compliance-Daten des Mandanten.',
        'Enterprise-grade collaboration platform for University project deliverables. Fully GDPR compliant, secure, and isolated from core CRM environments.': 'Leistungsstarke Kollaborationsplattform für universitäre Projektergebnisse. Vollständig DSGVO-konform, sicher und von zentralen CRM-Umgebungen getrennt.',
        'Delete project and all of its teams, members, and uploaded files? This cannot be undone.': 'Projekt sowie alle Teams, Mitglieder und hochgeladenen Dateien löschen? Dieser Vorgang kann nicht rückgängig gemacht werden.',
        'Delete this teacher and remove their project assignments? This cannot be undone.': 'Diese Lehrkraft löschen und ihre Projektzuweisungen entfernen? Dieser Vorgang kann nicht rückgängig gemacht werden.',
        'Are you sure you want to delete this organization? This action cannot be undone.': 'Möchten Sie diese Organisation wirklich löschen? Dieser Vorgang kann nicht rückgängig gemacht werden.',
        'Delete this team, its members, and uploaded files? This cannot be undone.': 'Dieses Team, seine Mitglieder und hochgeladenen Dateien löschen? Dieser Vorgang kann nicht rückgängig gemacht werden.',
        'Delete this student?': 'Diese studierende Person löschen?',
        'Delete this deliverable permanently?': 'Dieses Arbeitsergebnis dauerhaft löschen?',
        'Select a project and enter a team name': 'Wählen Sie ein Projekt aus und geben Sie einen Teamnamen ein.',
        'Fill all fields': 'Füllen Sie alle Felder aus.',
        'Failed to map dependency.': 'Abhängigkeit konnte nicht zugeordnet werden.',
        'Failed to create dependency request.': 'Anfrage zur Abhängigkeit konnte nicht erstellt werden.',
        'Network error.': 'Netzwerkfehler.',
        'Download failed. Check your connection and try again.': 'Download fehlgeschlagen. Überprüfen Sie Ihre Verbindung und versuchen Sie es erneut.',
        'Unable to load shared project resources': 'Gemeinsame Projektressourcen konnten nicht geladen werden',
        'Unable to download shared resource': 'Gemeinsame Ressource konnte nicht heruntergeladen werden',
        'Unable to download this file.': 'Diese Datei konnte nicht heruntergeladen werden.',
        'Unable to create project': 'Projekt konnte nicht erstellt werden',
        'Unable to delete project': 'Projekt konnte nicht gelöscht werden',
        'Unable to create team': 'Team konnte nicht erstellt werden',
        'Unable to delete team': 'Team konnte nicht gelöscht werden',
        'Unable to update team': 'Team konnte nicht aktualisiert werden',
        'Unable to create student': 'Studierende Person konnte nicht hinzugefügt werden',
        'Unable to delete student': 'Studierende Person konnte nicht gelöscht werden',
        'Unable to update student': 'Daten der studierenden Person konnten nicht aktualisiert werden',
        'Unable to create teacher': 'Lehrkraft konnte nicht hinzugefügt werden',
        'Unable to delete teacher': 'Lehrkraft konnte nicht gelöscht werden',
        'Unable to update teacher': 'Daten der Lehrkraft konnten nicht aktualisiert werden',
        'Unable to delete deliverable': 'Arbeitsergebnis konnte nicht gelöscht werden',
        'Unable to load student privacy records': 'Datenschutznachweise der Studierenden konnten nicht geladen werden',
        'Unable to save task': 'Aufgabe konnte nicht gespeichert werden',
        'Error creating task': 'Fehler beim Erstellen der Aufgabe',
        'Failed to create task': 'Aufgabe konnte nicht erstellt werden',
        'Failed to save task': 'Aufgabe konnte nicht gespeichert werden',
        'Email is required': 'E-Mail-Adresse ist erforderlich',
        'Teacher account not found.': 'Lehrkraftkonto nicht gefunden.',
        'Email and OTP required': 'E-Mail-Adresse und Einmalcode sind erforderlich',
        'Invalid OTP or email': 'Ungültiger Einmalcode oder ungültige E-Mail-Adresse',
        'Login code expired. Request a new code.': 'Der Anmeldecode ist abgelaufen. Fordern Sie einen neuen Code an.',
        'Login code already used. Request a new code.': 'Der Anmeldecode wurde bereits verwendet. Fordern Sie einen neuen Code an.',
        'Missing or invalid token': 'Token fehlt oder ist ungültig',
        'Unauthorized': 'Nicht autorisiert',
        'Session expired': 'Sitzung abgelaufen',
        'Token expired': 'Token abgelaufen',
        'Invalid token': 'Ungültiger Token',
        'Invalid admin passcode': 'Ungültiger Admin-Zugangscode',
        'Name and email required': 'Name und E-Mail-Adresse sind erforderlich',
        'Email already exists': 'Diese E-Mail-Adresse ist bereits vorhanden',
        'Project name required': 'Projektname ist erforderlich',
        'Project not found': 'Projekt nicht gefunden',
        'Project not found for your team': 'Für Ihr Team wurde kein Projekt gefunden',
        'Tenant administrator access required': 'Zugriff für Mandantenadministratoren erforderlich',
        'Select a file to upload': 'Wählen Sie eine Datei zum Hochladen aus',
        'File name is invalid': 'Dateiname ist ungültig',
        'Folder not found in this project': 'Ordner in diesem Projekt nicht gefunden',
        'Files must be 250 MB or smaller': 'Dateien dürfen höchstens 250 MB groß sein',
        'Files must be 50 MB or smaller': 'Dateien dürfen höchstens 50 MB groß sein',
        'Uploaded file exceeds maximum allowed size (250 MB)': 'Die hochgeladene Datei überschreitet die maximal zulässige Größe (250 MB)',
        'Unable to save project resource': 'Projektressource konnte nicht gespeichert werden',
        'Project resource not found': 'Projektressource nicht gefunden',
        'Project resource file is missing': 'Datei der Projektressource fehlt',
        'Folder name is required': 'Ordnername ist erforderlich',
        'Folder names must be 80 characters or fewer': 'Ordnernamen dürfen höchstens 80 Zeichen enthalten',
        'A folder with this name already exists': 'Ein Ordner mit diesem Namen ist bereits vorhanden',
        'Comments must contain 1 to 3000 characters': 'Kommentare müssen 1 bis 3000 Zeichen enthalten',
        'Team name and project required': 'Teamname und Projekt sind erforderlich',
        'Team already exists': 'Dieses Team ist bereits vorhanden',
        'Missing fields': 'Erforderliche Angaben fehlen',
        'Team not found': 'Team nicht gefunden',
        'Student email already exists': 'Diese E-Mail-Adresse ist bereits registriert',
        'Name required': 'Name ist erforderlich',
        'Student not found': 'Studierende Person nicht gefunden',
        'File not found': 'Datei nicht gefunden',
        'File missing from disk': 'Datei auf dem Datenträger nicht gefunden',
        'Student not found in any team.': 'Die studierende Person wurde keinem Team zugeordnet.',
        'No file part': 'Keine Datei übermittelt',
        'No selected file': 'Keine Datei ausgewählt',
        'Privacy notice acknowledgement required': 'Die Bestätigung des Datenschutzhinweises ist erforderlich',
        'Please acknowledge the course privacy notice to continue.': 'Bestätigen Sie den Datenschutzhinweis des Kurses, um fortzufahren.',
        'Choose yes or no for the optional marketing permission.': 'Wählen Sie für die optionale Marketing-Einwilligung Ja oder Nein aus.'
        ,'Activity': 'Aktivität'
        ,'Activities': 'Aktivitäten'
        ,'Activity:': 'Aktivität:'
        ,'Assignee': 'Zuständige Person'
        ,'Blocked': 'Blockiert'
        ,'Completed': 'Abgeschlossen'
        ,'Expected': 'Erwartet'
        ,'Delete': 'Löschen'
        ,'Delete Activity': 'Aktivität löschen'
        ,'Delete Task': 'Aufgabe löschen'
        ,'Delete Team': 'Team löschen'
        ,'Delete Work Package': 'Arbeitspaket löschen'
        ,'Deliverable': 'Arbeitsergebnis'
        ,'Dependency Details': 'Details zur Abhängigkeit'
        ,'Description': 'Beschreibung'
        ,'Earliest possible start:': 'Frühestmöglicher Beginn:'
        ,'Edit': 'Bearbeiten'
        ,'Edit Activity': 'Aktivität bearbeiten'
        ,'Edit Task': 'Aufgabe bearbeiten'
        ,'Edit Work Package': 'Arbeitspaket bearbeiten'
        ,'Faculty Roster': 'Lehrkräfteverzeichnis'
        ,'Impact on Our Team': 'Auswirkungen auf unser Team'
        ,'Manage →': 'Verwalten →'
        ,'Marketing:': 'Marketing:'
        ,'Name': 'Name'
        ,'New Work Package': 'Neues Arbeitspaket'
        ,'No teams in this project.': 'Keine Teams in diesem Projekt.'
        ,'Pending': 'Ausstehend'
        ,'Pending (Not Mapped)': 'Ausstehend (nicht zugeordnet)'
        ,'Planned start:': 'Geplanter Beginn:'
        ,'Privacy Notice:': 'Datenschutzhinweis:'
        ,'Progress': 'Fortschritt'
        ,'Project': 'Projekt'
        ,'Project Not Started': 'Projekt noch nicht begonnen'
        ,'Project Root': 'Projektstammordner'
        ,'Project files': 'Projektdateien'
        ,'Project milestone affected': 'Betroffener Projektmeilenstein'
        ,'Reason': 'Begründung'
        ,'Resources': 'Ressourcen'
        ,'Secure Academic': 'Sicherer akademischer'
        ,'Select a Team Workspace': 'Team-Arbeitsbereich auswählen'
        ,'Select a team from the list to view details.': 'Wählen Sie ein Team aus der Liste aus, um Details anzuzeigen.'
        ,'Selected Team': 'Ausgewähltes Team'
        ,'Sign out': 'Abmelden'
        ,'Status': 'Status'
        ,'Teams': 'Teams'
        ,'This change may affect other project work.': 'Diese Änderung kann sich auf andere Projektarbeiten auswirken.'
        ,'Waiting': 'Wartet'
        ,'Waiting on:': 'Wartet auf:'
        ,'We use your account details and submissions to run the course and review your work.': 'Wir verwenden Ihre Kontodaten und Einreichungen, um den Kurs durchzuführen und Ihre Arbeit zu bewerten.'
        ,'Work Package:': 'Arbeitspaket:'
        ,'Workspace': 'Arbeitsbereich'
        ,'You': 'Sie'
        ,'and ALL of its contents': 'und den gesamten Inhalt'
        ,'e.g. Customer expectation analysis': 'z. B. Analyse der Kundenerwartungen'
        ,'e.g. Market Research': 'z. B. Marktforschung'
        ,'e.g. Reference Files': 'z. B. Referenzdateien'
        ,'e.g. Required for our pricing analysis': 'z. B. Erforderlich für unsere Preisanalyse'
        ,'e.g. Science 101': 'z. B. Grundlagen der Naturwissenschaften'
        ,'e.g. Target Market Analysis': 'z. B. Zielgruppenanalyse'
        ,'e.g. Week 1 Materials': 'z. B. Materialien für Woche 1'
        ,'Create a project before adding shared resources.': 'Erstellen Sie ein Projekt, bevor Sie gemeinsame Ressourcen hinzufügen.'
        ,'Create your first Work Package to begin structuring your team\'s project work into manageable activities and tasks.': 'Erstellen Sie Ihr erstes Arbeitspaket, um die Projektarbeit Ihres Teams in überschaubare Aktivitäten und Aufgaben zu gliedern.'
        ,'Add briefs, templates, and reference files for all teams in the selected project': 'Fügen Sie Briefings, Vorlagen und Referenzdateien für alle Teams des ausgewählten Projekts hinzu.'
        ,'Sundeck Academic Hub | Enterprise': 'Sundeck Academic Hub | Unternehmen'
        ,'Sundeck Academic Hub | Legal Information': 'Sundeck Academic Hub | Rechtliche Informationen'
        ,'Sundeck Academic Hub | Student Login': 'Sundeck Academic Hub | Studierendenanmeldung'
        ,'Sundeck Academic Hub | Teacher Portal': 'Sundeck Academic Hub | Lehrkräfteportal'
        ,'Sundeck Academic Hub | Tenant Admin': 'Sundeck Academic Hub | Mandantenverwaltung'
        ,'Team:': 'Team:'
        ,'Active': 'Aktiv'
        ,'Add briefs, templates, and reference files for all teams in the selected project.': 'Fügen Sie Briefings, Vorlagen und Referenzdateien für alle Teams des ausgewählten Projekts hinzu.'
        ,'Confirm Deletion': 'Löschvorgang bestätigen'
        ,'No deliverables yet': 'Noch keine Arbeitsergebnisse vorhanden'
        ,'Your team hasn\'t uploaded any project files or folders yet.': 'Ihr Team hat noch keine Projektdateien oder Ordner hochgeladen.'
        ,'Project Workspace': 'Projektarbeitsbereich'
        ,'Your Team': 'Ihr Team'
        ,'+ Request': '+ Anfrage'
        ,'Upload': 'Hochladen'
        ,'Confirm': 'Bestätigen'
        ,'New Task': 'Neue Aufgabe'
        ,'PROJECT IMPACT': 'PROJEKTAUSWIRKUNGEN'
        ,'Task Details': 'Aufgabendetails'
        ,'Creating...': 'Wird erstellt ...'
        ,'New Activity': 'Neue Aktivität'
        ,'Close upload dialog': 'Upload-Dialog schließen'
        ,'Activity not found': 'Aktivität nicht gefunden'
        ,'Dependency request not found': 'Anfrage zur Abhängigkeit nicht gefunden'
        ,'Folder not found': 'Ordner nicht gefunden'
        ,'Forbidden': 'Zugriff verweigert'
        ,'Forbidden. Requires Superadmin.': 'Zugriff verweigert. Superadmin-Berechtigung erforderlich.'
        ,'Organization name required': 'Organisationsname ist erforderlich'
        ,'Student not assigned to a team': 'Studierende Person ist keinem Team zugewiesen'
        ,'Task not found': 'Aufgabe nicht gefunden'
        ,'Teacher already assigned or invalid IDs': 'Lehrkraft ist bereits zugewiesen oder IDs sind ungültig'
        ,'Teacher not found': 'Lehrkraft nicht gefunden'
        ,'Unauthorized to add activity to another team': 'Keine Berechtigung, eine Aktivität für ein anderes Team hinzuzufügen'
        ,'Unauthorized to add task to another team': 'Keine Berechtigung, eine Aufgabe für ein anderes Team hinzuzufügen'
        ,'Unauthorized to delete activity belonging to another team': 'Keine Berechtigung, eine Aktivität eines anderen Teams zu löschen'
        ,'Unauthorized to delete task belonging to another team': 'Keine Berechtigung, eine Aufgabe eines anderen Teams zu löschen'
        ,'Unauthorized to delete work package belonging to another team': 'Keine Berechtigung, ein Arbeitspaket eines anderen Teams zu löschen'
        ,'Unauthorized to edit activity belonging to another team': 'Keine Berechtigung, eine Aktivität eines anderen Teams zu bearbeiten'
        ,'Unauthorized to edit task belonging to another team': 'Keine Berechtigung, eine Aufgabe eines anderen Teams zu bearbeiten'
        ,'Unauthorized to edit work package belonging to another team': 'Keine Berechtigung, ein Arbeitspaket eines anderen Teams zu bearbeiten'
        ,'Unauthorized to map this request': 'Keine Berechtigung, diese Anfrage zuzuordnen'
        ,'Work package not found': 'Arbeitspaket nicht gefunden'
        ,'from_task_id is required': 'from_task_id ist erforderlich'
        ,'organization_id required': 'organization_id ist erforderlich'
        ,'teacher_id required': 'teacher_id ist erforderlich'
        ,'team_id required': 'team_id ist erforderlich'
        ,'A 6-digit secure code has been sent to your email inbox!': 'Ein sicherer 6-stelliger Code wurde an Ihren E-Mail-Posteingang gesendet!'
        ,'A dependency status has been updated.': 'Der Status einer Abhängigkeit wurde aktualisiert.'
        ,'A new deliverable was uploaded.': 'Ein neues Arbeitsergebnis wurde hochgeladen.'
        ,'A team has requested a new dependency.': 'Ein Team hat eine neue Abhängigkeit angefragt.'
        ,'Demo OTP requested. Use any OTP to login.': 'Demo-Einmalcode angefordert. Verwenden Sie zum Anmelden einen beliebigen Einmalcode.'
        ,'Delete Folder': 'Ordner löschen'
        ,'Delete File': 'Datei löschen'
        ,'Delete Activity': 'Aktivität löschen'
        ,'Delete Task': 'Aufgabe löschen'
        ,'Delete Work Package': 'Arbeitspaket löschen'
        ,'Folder is empty': 'Ordner ist leer'
        ,'No files have been uploaded to this folder.': 'In diesen Ordner wurden noch keine Dateien hochgeladen.'
        ,'No deliverables yet': 'Noch keine Arbeitsergebnisse vorhanden'
        ,'Failed to delete work package': 'Arbeitspaket konnte nicht gelöscht werden'
        ,'Failed to delete activity': 'Aktivität konnte nicht gelöscht werden'
        ,'Failed to delete task': 'Aufgabe konnte nicht gelöscht werden'
        ,'Failed to delete file': 'Datei konnte nicht gelöscht werden'
        ,'Failed to rename folder': 'Ordner konnte nicht umbenannt werden'
        ,'Unable to create folder': 'Ordner konnte nicht erstellt werden'
        ,'Are you sure you want to delete this folder? Files inside will be moved out of the folder.': 'Möchten Sie diesen Ordner wirklich löschen? Die enthaltenen Dateien werden aus dem Ordner verschoben.'
        ,'Are you sure you want to permanently delete this task?': 'Möchten Sie diese Aufgabe wirklich dauerhaft löschen?'
        ,'Are you sure you want to permanently delete this file?': 'Möchten Sie diese Datei wirklich dauerhaft löschen?'
        ,'WARNING This task is a dependency for other tasks. Deleting this task will invalidate these dependencies and may unblock downstream work unexpectedly. Are you sure?': 'WARNUNG Diese Aufgabe ist eine Abhängigkeit für andere Aufgaben. Wenn Sie sie löschen, werden diese Abhängigkeiten ungültig und nachfolgende Arbeiten könnten unerwartet freigegeben werden. Möchten Sie fortfahren?'
        ,'0 file(s) uploaded successfully': '0 Datei(en) erfolgreich hochgeladen'
    };

    const ENGLISH_TO_GERMAN = { ...TRANSLATIONS.de, ...EXTRA_TRANSLATIONS };
    const GERMAN_TO_ENGLISH = {
        ...TRANSLATIONS.en,
        ...Object.fromEntries(Object.entries(EXTRA_TRANSLATIONS).map(([english, german]) => [german, english]))
    };

    function normalizeText(value) {
        return String(value || '').replace(/\s+/g, ' ').trim();
    }

    function getCurrentLang() {
        const stored = localStorage.getItem('app_lang');
        return AVAILABLE_LANGS.includes(stored) ? stored : DEFAULT_LANG;
    }

    function setLanguage(lang) {
        const next = AVAILABLE_LANGS.includes(lang) ? lang : DEFAULT_LANG;
        localStorage.setItem('app_lang', next);
        document.documentElement.lang = next;
        applyTranslations();
        renderToggle();
    }

    function translateText(value, lang) {
        const normalized = normalizeText(value);
        if (!normalized) return value;

        const map = lang === 'en' ? GERMAN_TO_ENGLISH : ENGLISH_TO_GERMAN;
        if (Object.prototype.hasOwnProperty.call(map, normalized)) return map[normalized];

        if (lang === 'de') {
            const removeResource = normalized.match(/^Remove "(.+)" from shared project resources\?$/);
            if (removeResource) return `„${removeResource[1]}“ aus den gemeinsam genutzten Projektressourcen entfernen?`;
            const workPackagePrompt = normalized.match(/^Are you sure you want to delete the work package "(.+)"\? This will also delete all its activities and tasks\.$/);
            if (workPackagePrompt) return `Möchten Sie das Arbeitspaket „${workPackagePrompt[1]}“ wirklich löschen? Dadurch werden auch alle zugehörigen Aktivitäten und Aufgaben gelöscht.`;
            const activityPrompt = normalized.match(/^Are you sure you want to delete the activity "(.+)"\? This will also delete all its tasks\.$/);
            if (activityPrompt) return `Möchten Sie die Aktivität „${activityPrompt[1]}“ wirklich löschen? Dadurch werden auch alle zugehörigen Aufgaben gelöscht.`;
            const deletePrompt = normalized.match(/^Are you sure you want to delete(?:\s+(.+))?$/);
            if (deletePrompt) return deletePrompt[1]
                ? `Möchten Sie wirklich ${deletePrompt[1].replace(/\?$/, '')} löschen?`
                : 'Möchten Sie Folgendes wirklich löschen:';
        } else {
            const removeResource = normalized.match(/^„(.+)“ aus den gemeinsam genutzten Projektressourcen entfernen\?$/);
            if (removeResource) return `Remove "${removeResource[1]}" from shared project resources?`;
            const workPackagePrompt = normalized.match(/^Möchten Sie das Arbeitspaket „(.+)“ wirklich löschen\? Dadurch werden auch alle zugehörigen Aktivitäten und Aufgaben gelöscht\.$/);
            if (workPackagePrompt) return `Are you sure you want to delete the work package "${workPackagePrompt[1]}"? This will also delete all its activities and tasks.`;
            const activityPrompt = normalized.match(/^Möchten Sie die Aktivität „(.+)“ wirklich löschen\? Dadurch werden auch alle zugehörigen Aufgaben gelöscht\.$/);
            if (activityPrompt) return `Are you sure you want to delete the activity "${activityPrompt[1]}"? This will also delete all its tasks.`;
        }

        const uploadCount = normalized.match(/^(\d+) file\(s\) uploaded successfully$/i);
        if (uploadCount) return lang === 'en'
            ? `${uploadCount[1]} file(s) uploaded successfully`
            : `${uploadCount[1]} Datei(en) erfolgreich hochgeladen`;

        const reverseUploadCount = normalized.match(/^(\d+) Datei\(en\) erfolgreich hochgeladen$/i);
        if (reverseUploadCount && lang === 'en') return `${reverseUploadCount[1]} file(s) uploaded successfully`;

        const dynamicCount = normalized.match(/^(\d+)\s+(Teams?|Tasks?|members?|Projects?|Teachers?|Aufgaben?|Mitglieder?|Mitglied|Projekte?|Lehrkräfte?|Lehrkraft)$/i);
        if (dynamicCount) {
            const labels = lang === 'en'
                ? { team: 'Team', teams: 'Teams', aufgabe: 'Task', aufgaben: 'Tasks', mitglied: 'member', mitglieder: 'members', projekt: 'Project', projekte: 'Projects', lehrkraft: 'Teacher', lehrkräfte: 'Teachers' }
                : { team: 'Team', teams: 'Teams', task: 'Aufgabe', tasks: 'Aufgaben', member: 'Mitglied', members: 'Mitglieder', project: 'Projekt', projects: 'Projekte', teacher: 'Lehrkraft', teachers: 'Lehrkräfte' };
            const label = dynamicCount[2].toLowerCase();
            if (labels[label]) return `${dynamicCount[1]} ${labels[label]}`;
        }

        return value;
    }

    function applyTranslations() {
        const lang = getCurrentLang();
        document.documentElement.lang = lang;

        const walk = (node) => {
            if (!node || node.nodeType === Node.DOCUMENT_TYPE_NODE) return;

            if (node.nodeType === Node.TEXT_NODE) {
                const text = node.textContent || '';
                const normalized = normalizeText(text);
                if (!normalized || normalized.length < 2 || /\{\{|\$\{|\b[A-Za-z0-9_]+\s*\(/.test(normalized)) return;
                const translated = translateText(normalized, lang);
                if (translated !== normalized) {
                    const leadingWhitespace = text.match(/^\s*/)[0];
                    const trailingWhitespace = text.match(/\s*$/)[0];
                    node.textContent = `${leadingWhitespace}${translated}${trailingWhitespace}`;
                }
                return;
            }

            if (node.nodeType !== Node.ELEMENT_NODE || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(node.tagName)) {
                return;
            }

            ['placeholder', 'title', 'aria-label', 'alt', 'value'].forEach((attr) => {
                if (!node.hasAttribute(attr)) return;
                const current = node.getAttribute(attr) || '';
                const translated = translateText(current, lang);
                if (translated !== current && translated !== normalizeText(current)) {
                    node.setAttribute(attr, translated);
                }
            });

            if (node.childNodes) {
                node.childNodes.forEach(walk);
            }
        };

        const root = document.documentElement;
        if (root) {
            walk(root);
        }
    }

    function renderToggle() {
        const host = document.getElementById('lang-toggle-container');
        if (!host) return;

        const current = getCurrentLang();
        host.innerHTML = `
            <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-100 p-1 shadow-sm">
                <button type="button" data-lang="de" class="rounded-md px-2.5 py-1 text-[11px] font-semibold transition ${current === 'de' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'}">Deutsch</button>
                <button type="button" data-lang="en" class="rounded-md px-2.5 py-1 text-[11px] font-semibold transition ${current === 'en' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'}">English</button>
            </div>
        `;

        host.querySelectorAll('button[data-lang]').forEach((button) => {
            button.addEventListener('click', () => {
                const nextLang = button.dataset.lang;
                if (!AVAILABLE_LANGS.includes(nextLang)) return;
                setLanguage(nextLang);
            });
        });
    }

    function initLanguage() {
        const saved = localStorage.getItem('app_lang');
        const lang = AVAILABLE_LANGS.includes(saved) ? saved : DEFAULT_LANG;
        localStorage.setItem('app_lang', lang);
        renderToggle();
        applyTranslations();

        const observer = new MutationObserver(() => {
            applyTranslations();
        });

        if (document.body) {
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                characterData: true,
                attributes: true,
                attributeFilter: ['placeholder', 'title', 'aria-label', 'alt', 'value']
            });
        }
    }

    window.i18n = {
        getCurrentLang,
        setLanguage,
        applyTranslations,
        renderToggle,
        t: (value) => translateText(value, getCurrentLang())
    };
    window.t = window.i18n.t;

    const nativeAlert = window.alert.bind(window);
    window.alert = (message) => nativeAlert(window.t(message));
    const nativeConfirm = window.confirm.bind(window);
    window.confirm = (message) => nativeConfirm(window.t(message));

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLanguage, { once: true });
    } else {
        initLanguage();
    }
})();
