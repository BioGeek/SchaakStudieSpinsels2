// Een Vervelende Viervoeter (EG 2014) — bishop+king+pawn vs knight+king+2
// pawns. The black knight ('the annoying quadruped') jumps around 14 times
// to delay White's win to move 16; both defences (Variant A and B) end in
// Lxb6#. Position from the book diagram (p429, classifier + GBR 0013.12);
// the main line and both variants validated to mate with python-chess.
export const vervelendeViervoeter = {
  "number": 1300,
  "chapter": "Een Vervelende Viervoeter",
  "chapterNumber": 7,
  "source": "EG, 2014, 4de Eervolle Vermelding",
  "gbr": "0013.12 c4a4",
  "fen": "8/n7/p7/8/kpK5/8/1P6/2B5 w - - 0 1",
  "stipulation": "+",
  "moves": [
    {
      "id": "main.1",
      "ply": 1,
      "san": "b3+",
      "nl": "b3+",
      "fenAfter": "8/n7/p7/8/kpK5/1P6/8/2B5 b - - 0 1",
      "variant": "main",
      "parent": null
    },
    {
      "id": "main.2",
      "ply": 2,
      "san": "Ka5",
      "nl": "Ka5",
      "fenAfter": "8/n7/p7/k7/1pK5/1P6/8/2B5 w - - 1 2",
      "variant": "main",
      "parent": "main.1"
    },
    {
      "id": "main.3",
      "ply": 3,
      "san": "Kc5",
      "nl": "Kc5",
      "fenAfter": "8/n7/p7/k1K5/1p6/1P6/8/2B5 b - - 2 2",
      "variant": "main",
      "parent": "main.2"
    },
    {
      "id": "main.4",
      "ply": 4,
      "san": "Nb5",
      "nl": "Pb5",
      "fenAfter": "8/8/p7/knK5/1p6/1P6/8/2B5 w - - 3 3",
      "variant": "main",
      "parent": "main.3"
    },
    {
      "id": "main.5",
      "ply": 5,
      "san": "Bd2",
      "nl": "Ld2",
      "fenAfter": "8/8/p7/knK5/1p6/1P6/3B4/8 b - - 4 3",
      "variant": "main",
      "parent": "main.4"
    },
    {
      "id": "main.6",
      "ply": 6,
      "san": "Nc3",
      "nl": "Pc3",
      "fenAfter": "8/8/p7/k1K5/1p6/1Pn5/3B4/8 w - - 5 4",
      "variant": "main",
      "parent": "main.5"
    },
    {
      "id": "main.7",
      "ply": 7,
      "san": "Bf4",
      "nl": "Lf4",
      "fenAfter": "8/8/p7/k1K5/1p3B2/1Pn5/8/8 b - - 6 4",
      "variant": "main",
      "parent": "main.6"
    },
    {
      "id": "main.8",
      "ply": 8,
      "san": "Nd5",
      "nl": "Pd5",
      "fenAfter": "8/8/p7/k1Kn4/1p3B2/1P6/8/8 w - - 7 5",
      "variant": "main",
      "parent": "main.7"
    },
    {
      "id": "main.9",
      "ply": 9,
      "san": "Be5",
      "nl": "Le5",
      "fenAfter": "8/8/p7/k1KnB3/1p6/1P6/8/8 b - - 8 5",
      "variant": "main",
      "parent": "main.8"
    },
    {
      "id": "main.10",
      "ply": 10,
      "san": "Nb6",
      "nl": "Pb6",
      "fenAfter": "8/8/pn6/k1K1B3/1p6/1P6/8/8 w - - 9 6",
      "variant": "main",
      "parent": "main.9"
    },
    {
      "id": "main.11",
      "ply": 11,
      "san": "Kc6",
      "nl": "Kc6",
      "fenAfter": "8/8/pnK5/k3B3/1p6/1P6/8/8 b - - 10 6",
      "variant": "main",
      "parent": "main.10"
    },
    {
      "id": "main.12",
      "ply": 12,
      "san": "Nd5",
      "nl": "Pd5",
      "fenAfter": "8/8/p1K5/k2nB3/1p6/1P6/8/8 w - - 11 7",
      "variant": "main",
      "parent": "main.11"
    },
    {
      "id": "main.13",
      "ply": 13,
      "san": "Bb8",
      "nl": "Lb8",
      "fenAfter": "1B6/8/p1K5/k2n4/1p6/1P6/8/8 b - - 12 7",
      "variant": "main",
      "parent": "main.12"
    },
    {
      "id": "main.14",
      "ply": 14,
      "san": "Nb6",
      "nl": "Pb6",
      "fenAfter": "1B6/8/pnK5/k7/1p6/1P6/8/8 w - - 13 8",
      "variant": "main",
      "parent": "main.13"
    },
    {
      "id": "main.15",
      "ply": 15,
      "san": "Bg3",
      "nl": "Lg3",
      "fenAfter": "8/8/pnK5/k7/1p6/1P4B1/8/8 b - - 14 8",
      "variant": "main",
      "parent": "main.14"
    },
    {
      "id": "main.16",
      "ply": 16,
      "san": "Nd5",
      "nl": "Pd5",
      "fenAfter": "8/8/p1K5/k2n4/1p6/1P4B1/8/8 w - - 15 9",
      "variant": "main",
      "parent": "main.15"
    },
    {
      "id": "main.17",
      "ply": 17,
      "san": "Bf2",
      "nl": "Lf2",
      "fenAfter": "8/8/p1K5/k2n4/1p6/1P6/5B2/8 b - - 16 9",
      "variant": "main",
      "parent": "main.16"
    },
    {
      "id": "main.18",
      "ply": 18,
      "san": "Ne7+",
      "nl": "Pe7+",
      "fenAfter": "8/4n3/p1K5/k7/1p6/1P6/5B2/8 w - - 17 10",
      "variant": "main",
      "parent": "main.17"
    },
    {
      "id": "main.19",
      "ply": 19,
      "san": "Kc5",
      "nl": "Kc5",
      "fenAfter": "8/4n3/p7/k1K5/1p6/1P6/5B2/8 b - - 18 10",
      "variant": "main",
      "parent": "main.18"
    },
    {
      "id": "main.20",
      "ply": 20,
      "san": "Nd5",
      "nl": "Pd5",
      "fenAfter": "8/8/p7/k1Kn4/1p6/1P6/5B2/8 w - - 19 11",
      "variant": "main",
      "parent": "main.19"
    },
    {
      "id": "main.21",
      "ply": 21,
      "san": "Be1",
      "nl": "Le1",
      "fenAfter": "8/8/p7/k1Kn4/1p6/1P6/8/4B3 b - - 20 11",
      "variant": "main",
      "parent": "main.20"
    },
    {
      "id": "main.22",
      "ply": 22,
      "san": "Nc3",
      "nl": "Pc3",
      "fenAfter": "8/8/p7/k1K5/1p6/1Pn5/8/4B3 w - - 21 12",
      "variant": "main",
      "parent": "main.21"
    },
    {
      "id": "main.23",
      "ply": 23,
      "san": "Bh4",
      "nl": "Lh4",
      "fenAfter": "8/8/p7/k1K5/1p5B/1Pn5/8/8 b - - 22 12",
      "variant": "main",
      "parent": "main.22"
    },
    {
      "id": "A.24",
      "ply": 24,
      "san": "Ne4+",
      "nl": "Pe4+",
      "fenAfter": "8/8/p7/k1K5/1p2n2B/1P6/8/8 w - - 23 13",
      "variant": "A",
      "parent": "main.23"
    },
    {
      "id": "A.25",
      "ply": 25,
      "san": "Kc6",
      "nl": "Kc6",
      "fenAfter": "8/8/p1K5/k7/1p2n2B/1P6/8/8 b - - 24 13",
      "variant": "A",
      "parent": "A.24"
    },
    {
      "id": "A.26",
      "ply": 26,
      "san": "Nf6",
      "nl": "Pf6",
      "fenAfter": "8/8/p1K2n2/k7/1p5B/1P6/8/8 w - - 25 14",
      "variant": "A",
      "parent": "A.25"
    },
    {
      "id": "A.27",
      "ply": 27,
      "san": "Bg5",
      "nl": "Lg5",
      "fenAfter": "8/8/p1K2n2/k5B1/1p6/1P6/8/8 b - - 26 14",
      "variant": "A",
      "parent": "A.26"
    },
    {
      "id": "A.28",
      "ply": 28,
      "san": "Nd5",
      "nl": "Pd5",
      "fenAfter": "8/8/p1K5/k2n2B1/1p6/1P6/8/8 w - - 27 15",
      "variant": "A",
      "parent": "A.27"
    },
    {
      "id": "A.29",
      "ply": 29,
      "san": "Bd8+",
      "nl": "Ld8+",
      "fenAfter": "3B4/8/p1K5/k2n4/1p6/1P6/8/8 b - - 28 15",
      "variant": "A",
      "parent": "A.28"
    },
    {
      "id": "A.30",
      "ply": 30,
      "san": "Nb6",
      "nl": "Pb6",
      "fenAfter": "3B4/8/pnK5/k7/1p6/1P6/8/8 w - - 29 16",
      "variant": "A",
      "parent": "A.29"
    },
    {
      "id": "A.31",
      "ply": 31,
      "san": "Bxb6#",
      "nl": "Lxb6#",
      "fenAfter": "8/8/pBK5/k7/1p6/1P6/8/8 b - - 0 16",
      "variant": "A",
      "parent": "A.30"
    },
    {
      "id": "B.24",
      "ply": 24,
      "san": "Na4+",
      "nl": "Pa4+",
      "fenAfter": "8/8/p7/k1K5/np5B/1P6/8/8 w - - 23 13",
      "variant": "B",
      "parent": "main.23"
    },
    {
      "id": "B.25",
      "ply": 25,
      "san": "Kc6",
      "nl": "Kc6",
      "fenAfter": "8/8/p1K5/k7/np5B/1P6/8/8 b - - 24 13",
      "variant": "B",
      "parent": "B.24"
    },
    {
      "id": "B.26",
      "ply": 26,
      "san": "Nb6",
      "nl": "Pb6",
      "fenAfter": "8/8/pnK5/k7/1p5B/1P6/8/8 w - - 25 14",
      "variant": "B",
      "parent": "B.25"
    },
    {
      "id": "B.27",
      "ply": 27,
      "san": "Be7",
      "nl": "Le7",
      "fenAfter": "8/4B3/pnK5/k7/1p6/1P6/8/8 b - - 26 14",
      "variant": "B",
      "parent": "B.26"
    },
    {
      "id": "B.28",
      "ply": 28,
      "san": "Na8",
      "nl": "Pa8",
      "fenAfter": "n7/4B3/p1K5/k7/1p6/1P6/8/8 w - - 27 15",
      "variant": "B",
      "parent": "B.27"
    },
    {
      "id": "B.29",
      "ply": 29,
      "san": "Bd8+",
      "nl": "Ld8+",
      "fenAfter": "n2B4/8/p1K5/k7/1p6/1P6/8/8 b - - 28 15",
      "variant": "B",
      "parent": "B.28"
    },
    {
      "id": "B.30",
      "ply": 30,
      "san": "Nb6",
      "nl": "Pb6",
      "fenAfter": "3B4/8/pnK5/k7/1p6/1P6/8/8 w - - 29 16",
      "variant": "B",
      "parent": "B.29"
    },
    {
      "id": "B.31",
      "ply": 31,
      "san": "Bxb6#",
      "nl": "Lxb6#",
      "fenAfter": "8/8/pBK5/k7/1p6/1P6/8/8 b - - 0 16",
      "variant": "B",
      "parent": "B.30"
    }
  ],
  "prose": {
    "nl": {
      "before": "",
      "after": "",
      "beforeVariant": {
        "A": "",
        "B": ""
      }
    }
  }
};
