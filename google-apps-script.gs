/*
 * Google-Apps-Script fuer die Anmeldungen von htl-buffet.at
 * -----------------------------------------------------------
 * Schreibt jede Anmeldung (OHNE Passwort) in das Google Sheet,
 * zu dem dieses Script gehoert. Nur gueltige @htl-braunau.at-Adressen.
 *
 * EINRICHTEN (einmalig):
 *  1. Google Sheet anlegen:  https://sheets.new
 *  2. Oben im Menue:  Erweiterungen -> Apps Script
 *  3. Den gesamten Beispielcode dort loeschen und diesen hier einfuegen.
 *  4. Speichern (Diskettensymbol).
 *  5. Oben rechts:  Bereitstellen -> Neue Bereitstellung
 *       - Typ:  Web-App
 *       - Ausfuehren als:  Ich
 *       - Zugriff:  Jeder (auch anonym)   <-- wichtig, sonst kann die Seite nicht speichern
 *       - Bereitstellen -> Zugriff erlauben / bestaetigen
 *  6. Die angezeigte Web-App-URL kopieren (endet auf /exec)
 *       und mir schicken ODER in index.html bei SPEICHER_URL eintragen.
 */

var DOMAIN = '@htl-braunau.at';

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var email = String(d.email || '').trim();

    // nur gueltige HTL-Braunau-Adressen speichern (kein Passwort wird uebergeben)
    if (email.toLowerCase().slice(-DOMAIN.length) !== DOMAIN) {
      return antwort('ignoriert');
    }

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Zeitstempel', 'E-Mail', 'Rolle', 'Klasse']);
    }
    sheet.appendRow([
      d.zeitstempel || new Date().toLocaleString('de-AT'),
      email,
      d.rolle  || '',
      d.klasse || ''
    ]);
    return antwort('ok');
  } catch (err) {
    return antwort('fehler');
  }
}

// kleine Testantwort, falls man die URL im Browser oeffnet
function doGet() {
  return antwort('bereit');
}

function antwort(status) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: status }))
    .setMimeType(ContentService.MimeType.JSON);
}
