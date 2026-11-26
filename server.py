"""
Kleiner lokaler Server fuer das Schulprojekt.

Start:   python server.py
Dann im Browser oeffnen:  http://localhost:8000

Er liefert die Seite aus und speichert jede Anmeldung
automatisch in die Datei 'anmeldungen.csv' im selben Ordner.
Nur fuer Versuchszwecke / lokal (bindet an 127.0.0.1).
"""

import csv
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ORDNER   = os.path.dirname(os.path.abspath(__file__))
CSV_DATEI = os.path.join(ORDNER, "anmeldungen.csv")
# Passwort wird bewusst NICHT gespeichert (Awareness-Demo, kein Diebstahl)
SPALTEN  = ["zeitstempel", "email", "rolle", "klasse"]
KOPF     = ["Zeitstempel", "E-Mail", "Rolle", "Klasse"]
PORT     = 8000


def email_gueltig(daten):
    """Nur gueltige HTL-Braunau-Adressen zulassen (kein Muell, keine Leereintraege)."""
    email = str(daten.get("email", "")).strip().lower()
    return "@" in email and email.endswith("@htl-braunau.at")


def anmeldung_speichern(daten):
    neu = not os.path.exists(CSV_DATEI)
    # utf-8-sig -> Excel zeigt Umlaute korrekt; Semikolon -> deutsche Excel-Spalten
    with open(CSV_DATEI, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        if neu:
            writer.writerow(KOPF)
        writer.writerow([str(daten.get(s, "")) for s in SPALTEN])


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ORDNER, **kwargs)

    def do_POST(self):
        if self.path.rstrip("/") in ("/speichern", "/save.php"):
            try:
                laenge = int(self.headers.get("Content-Length", 0))
                daten = json.loads(self.rfile.read(laenge).decode("utf-8"))
                if not email_gueltig(daten):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"status":"fehler","grund":"ungueltige-email"}')
                    return
                anmeldung_speichern(daten)
                print("Gespeichert:", daten.get("email"), "/", daten.get("rolle"),
                      "/", daten.get("klasse"))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                print("Fehler beim Speichern:", e)
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass  # ruhige Konsole


if __name__ == "__main__":
    print(f"Server laeuft:  http://localhost:{PORT}")
    print(f"Datei:          {CSV_DATEI}")
    print("Zum Beenden: Strg + C")
    with ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer beendet.")
