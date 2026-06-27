// Het Wilde Westen — the cover-style Wild West problem (GBR 1558.82, c3e4).
// Position lifted from the book diagram (data/.../p421), material-checked
// against the GBR code, and the 16-move king-march solution validated to
// mate with python-chess. Rendered with StudyBoard like the studies.
export const hetWildeWesten = {
  "number": 1558,
  "chapter": "Het Wilde Westen",
  "chapterNumber": 7,
  "source": "Rood aan zet",
  "gbr": "1558.82 c3e4",
  "fen": "RQR2b2/1P3P1p/1nP5/1p3n1P/4k2N/2K3P1/1PP2PN1/r3B2B b - - 0 1",
  "stipulation": "+",
  "moves": [
    {
      "id": "main.2",
      "ply": 2,
      "san": "b4+",
      "nl": "b4+",
      "fenAfter": "RQR2b2/1P3P1p/1nP5/5n1P/1p2k2N/2K3P1/1PP2PN1/r3B2B w - - 0 2",
      "variant": "main",
      "parent": null
    },
    {
      "id": "main.3",
      "ply": 3,
      "san": "Kd2",
      "nl": "Kd2",
      "fenAfter": "RQR2b2/1P3P1p/1nP5/5n1P/1p2k2N/6P1/1PPK1PN1/r3B2B b - - 1 2",
      "variant": "main",
      "parent": "main.2"
    },
    {
      "id": "main.4",
      "ply": 4,
      "san": "Nc4+",
      "nl": "Pc4+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/5n1P/1pn1k2N/6P1/1PPK1PN1/r3B2B w - - 2 3",
      "variant": "main",
      "parent": "main.3"
    },
    {
      "id": "main.5",
      "ply": 5,
      "san": "Ke2",
      "nl": "Ke2",
      "fenAfter": "RQR2b2/1P3P1p/2P5/5n1P/1pn1k2N/6P1/1PP1KPN1/r3B2B b - - 3 3",
      "variant": "main",
      "parent": "main.4"
    },
    {
      "id": "main.6",
      "ply": 6,
      "san": "Nd4+",
      "nl": "Pd4+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1pnnk2N/6P1/1PP1KPN1/r3B2B w - - 4 4",
      "variant": "main",
      "parent": "main.5"
    },
    {
      "id": "main.7",
      "ply": 7,
      "san": "Kf1",
      "nl": "Kf1",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1pnnk2N/6P1/1PP2PN1/r3BK1B b - - 5 4",
      "variant": "main",
      "parent": "main.6"
    },
    {
      "id": "main.8",
      "ply": 8,
      "san": "Nd2+",
      "nl": "Pd2+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p1nk2N/6P1/1PPn1PN1/r3BK1B w - - 6 5",
      "variant": "main",
      "parent": "main.7"
    },
    {
      "id": "main.9",
      "ply": 9,
      "san": "Kg1",
      "nl": "Kg1",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p1nk2N/6P1/1PPn1PN1/r3B1KB b - - 7 5",
      "variant": "main",
      "parent": "main.8"
    },
    {
      "id": "main.10",
      "ply": 10,
      "san": "Ne2+",
      "nl": "Pe2+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k2N/6P1/1PPnnPN1/r3B1KB w - - 8 6",
      "variant": "main",
      "parent": "main.9"
    },
    {
      "id": "main.11",
      "ply": 11,
      "san": "Kh2",
      "nl": "Kh2",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k2N/6P1/1PPnnPNK/r3B2B b - - 9 6",
      "variant": "main",
      "parent": "main.10"
    },
    {
      "id": "main.12",
      "ply": 12,
      "san": "Nf1+",
      "nl": "Pf1+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k2N/6P1/1PP1nPNK/r3Bn1B w - - 10 7",
      "variant": "main",
      "parent": "main.11"
    },
    {
      "id": "main.13",
      "ply": 13,
      "san": "Kh3",
      "nl": "Kh3",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k2N/6PK/1PP1nPN1/r3Bn1B b - - 11 7",
      "variant": "main",
      "parent": "main.12"
    },
    {
      "id": "main.14",
      "ply": 14,
      "san": "Ng1+",
      "nl": "Pg1+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k2N/6PK/1PP2PN1/r3BnnB w - - 12 8",
      "variant": "main",
      "parent": "main.13"
    },
    {
      "id": "main.15",
      "ply": 15,
      "san": "Kg4",
      "nl": "Kg4",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k1KN/6P1/1PP2PN1/r3BnnB b - - 13 8",
      "variant": "main",
      "parent": "main.14"
    },
    {
      "id": "main.16",
      "ply": 16,
      "san": "Nh2+",
      "nl": "Ph2+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/7P/1p2k1KN/6P1/1PP2PNn/r3B1nB w - - 14 9",
      "variant": "main",
      "parent": "main.15"
    },
    {
      "id": "main.17",
      "ply": 17,
      "san": "Kg5",
      "nl": "Kg5",
      "fenAfter": "RQR2b2/1P3P1p/2P5/6KP/1p2k2N/6P1/1PP2PNn/r3B1nB b - - 15 9",
      "variant": "main",
      "parent": "main.16"
    },
    {
      "id": "main.18",
      "ply": 18,
      "san": "Nh3+",
      "nl": "Ph3+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/6KP/1p2k2N/6Pn/1PP2PNn/r3B2B w - - 16 10",
      "variant": "main",
      "parent": "main.17"
    },
    {
      "id": "main.19",
      "ply": 19,
      "san": "Kf6",
      "nl": "Kf6",
      "fenAfter": "RQR2b2/1P3P1p/2P2K2/7P/1p2k2N/6Pn/1PP2PNn/r3B2B b - - 17 10",
      "variant": "main",
      "parent": "main.18"
    },
    {
      "id": "main.20",
      "ply": 20,
      "san": "Ng4+",
      "nl": "Pg4+",
      "fenAfter": "RQR2b2/1P3P1p/2P2K2/7P/1p2k1nN/6Pn/1PP2PN1/r3B2B w - - 18 11",
      "variant": "main",
      "parent": "main.19"
    },
    {
      "id": "main.21",
      "ply": 21,
      "san": "Ke6",
      "nl": "Ke6",
      "fenAfter": "RQR2b2/1P3P1p/2P1K3/7P/1p2k1nN/6Pn/1PP2PN1/r3B2B b - - 19 11",
      "variant": "main",
      "parent": "main.20"
    },
    {
      "id": "main.22",
      "ply": 22,
      "san": "Ng5+",
      "nl": "Pg5+",
      "fenAfter": "RQR2b2/1P3P1p/2P1K3/6nP/1p2k1nN/6P1/1PP2PN1/r3B2B w - - 20 12",
      "variant": "main",
      "parent": "main.21"
    },
    {
      "id": "main.23",
      "ply": 23,
      "san": "Kd7",
      "nl": "Kd7",
      "fenAfter": "RQR2b2/1P1K1P1p/2P5/6nP/1p2k1nN/6P1/1PP2PN1/r3B2B b - - 21 12",
      "variant": "main",
      "parent": "main.22"
    },
    {
      "id": "main.24",
      "ply": 24,
      "san": "Nf6+",
      "nl": "Pf6+",
      "fenAfter": "RQR2b2/1P1K1P1p/2P2n2/6nP/1p2k2N/6P1/1PP2PN1/r3B2B w - - 22 13",
      "variant": "main",
      "parent": "main.23"
    },
    {
      "id": "main.25",
      "ply": 25,
      "san": "Kc7",
      "nl": "Kc7",
      "fenAfter": "RQR2b2/1PK2P1p/2P2n2/6nP/1p2k2N/6P1/1PP2PN1/r3B2B b - - 23 13",
      "variant": "main",
      "parent": "main.24"
    },
    {
      "id": "main.26",
      "ply": 26,
      "san": "Ne6+",
      "nl": "Pe6+",
      "fenAfter": "RQR2b2/1PK2P1p/2P1nn2/7P/1p2k2N/6P1/1PP2PN1/r3B2B w - - 24 14",
      "variant": "main",
      "parent": "main.25"
    },
    {
      "id": "main.27",
      "ply": 27,
      "san": "Kb6",
      "nl": "Kb6",
      "fenAfter": "RQR2b2/1P3P1p/1KP1nn2/7P/1p2k2N/6P1/1PP2PN1/r3B2B b - - 25 14",
      "variant": "main",
      "parent": "main.26"
    },
    {
      "id": "main.28",
      "ply": 28,
      "san": "Nd5+",
      "nl": "Pd5+",
      "fenAfter": "RQR2b2/1P3P1p/1KP1n3/3n3P/1p2k2N/6P1/1PP2PN1/r3B2B w - - 26 15",
      "variant": "main",
      "parent": "main.27"
    },
    {
      "id": "main.29",
      "ply": 29,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "RQR2b2/1P3P1p/2P1n3/1K1n3P/1p2k2N/6P1/1PP2PN1/r3B2B b - - 27 15",
      "variant": "main",
      "parent": "main.28"
    },
    {
      "id": "main.30",
      "ply": 30,
      "san": "Nd4+",
      "nl": "Pd4+",
      "fenAfter": "RQR2b2/1P3P1p/2P5/1K1n3P/1p1nk2N/6P1/1PP2PN1/r3B2B w - - 28 16",
      "variant": "main",
      "parent": "main.29"
    },
    {
      "id": "main.31",
      "ply": 31,
      "san": "Kc4",
      "nl": "Kc4",
      "fenAfter": "RQR2b2/1P3P1p/2P5/3n3P/1pKnk2N/6P1/1PP2PN1/r3B2B b - - 29 16",
      "variant": "main",
      "parent": "main.30"
    },
    {
      "id": "main.32",
      "ply": 32,
      "san": "Nb6#",
      "nl": "Pb6#",
      "fenAfter": "RQR2b2/1P3P1p/1nP5/7P/1pKnk2N/6P1/1PP2PN1/r3B2B w - - 30 17",
      "variant": "main",
      "parent": "main.31"
    }
  ],
  "prose": {
    "nl": {
      "before": "",
      "after": "",
      "beforeVariant": {}
    }
  }
};
