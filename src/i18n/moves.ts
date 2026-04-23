import type { Locale } from './ui';

// Canonical move storage is English SAN (fed to chess.js).
// Dutch uses K/D/T/L/P for the big pieces; pawns stay lowercase.
const EN_TO_NL: Record<string, string> = { K: 'K', Q: 'D', R: 'T', B: 'L', N: 'P' };
const NL_TO_EN: Record<string, string> = { K: 'K', D: 'Q', T: 'R', L: 'B', P: 'N' };

// Replace leading piece letter + any disambiguation piece letter inside the move
// (e.g. "Nbd2" -> "Pbd2", "Qxe4+" -> "Dxe4+", "O-O", "e4", "f8=Q" -> "f8=D").
export function sanToDutch(san: string): string {
  return san
    .replace(/^([KQRBN])/, (_, c: string) => EN_TO_NL[c] ?? c)
    .replace(/=([QRBN])/, (_, c: string) => '=' + (EN_TO_NL[c] ?? c));
}

export function dutchToSan(move: string): string {
  return move
    .replace(/^([KDTLP])/, (_, c: string) => NL_TO_EN[c] ?? c)
    .replace(/=([DTLP])/, (_, c: string) => '=' + (NL_TO_EN[c] ?? c))
    // Also translate when Dutch uses a trailing piece letter for promotion (e.g. f8D)
    .replace(/([a-h][18])([DTLP])$/, (_, sq: string, c: string) => sq + '=' + (NL_TO_EN[c] ?? c));
}

export function renderMove(san: string, locale: Locale): string {
  return locale === 'nl' ? sanToDutch(san) : san;
}
