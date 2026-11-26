<?php
/*
 * Speichert eine Anmeldung (OHNE Passwort) in anmeldungen.csv.
 * Nur fuer die interne Awareness-Schulung gedacht.
 * Laeuft auf normalem PHP-Webhosting.
 */
header('Content-Type: application/json; charset=utf-8');

$roh = file_get_contents('php://input');
$d = json_decode($roh, true);
if (!is_array($d)) {
    http_response_code(400);
    echo json_encode(['status' => 'fehler']);
    exit;
}

// Nur gueltige HTL-Braunau-Adressen speichern (kein Muell, keine Leereintraege)
$email = isset($d['email']) ? trim($d['email']) : '';
$domain = '@htl-braunau.at';
$endetAufDomain = substr(strtolower($email), -strlen($domain)) === $domain;
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || !$endetAufDomain) {
    http_response_code(400);
    echo json_encode(['status' => 'fehler', 'grund' => 'ungueltige-email']);
    exit;
}

$datei = __DIR__ . '/anmeldungen.csv';
$neu = !file_exists($datei);

// Passwort wird bewusst NICHT uebernommen
$zeile = [
    isset($d['zeitstempel']) ? $d['zeitstempel'] : date('d.m.Y, H:i:s'),
    $email,
    isset($d['rolle'])       ? $d['rolle']        : '',
    isset($d['klasse'])      ? $d['klasse']       : '',
];

$fp = fopen($datei, 'a');
if ($fp === false) {
    http_response_code(500);
    echo json_encode(['status' => 'fehler']);
    exit;
}
flock($fp, LOCK_EX);
if ($neu) {
    fwrite($fp, "\xEF\xBB\xBF"); // BOM -> Excel zeigt Umlaute korrekt
    fputcsv($fp, ['Zeitstempel', 'E-Mail', 'Rolle', 'Klasse'], ';');
}
fputcsv($fp, $zeile, ';');
flock($fp, LOCK_UN);
fclose($fp);

echo json_encode(['status' => 'ok']);
