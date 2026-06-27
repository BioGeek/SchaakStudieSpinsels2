// De Bermuda Driehoek — original 2009 problem, 'mate in 22: seven times the
// Bermuda Triangle'. White's queen circles three corners (Dh8/Da8+/Da1)
// while Black is in zugzwang, burning the doubled h-pawns as waiting moves
// until forced to play c5, then Da4# mates. Position read from the book
// diagram (p426); the full 22-move line validated to mate with python-chess.
export const bermudaDriehoek = {
  "number": 22000,
  "chapter": "De Bermuda Driehoek",
  "chapterNumber": 7,
  "source": "Origineel, 2009",
  "gbr": "",
  "fen": "8/1p5p/1pp4p/1k6/1p6/1P6/5p1p/Q4Kbr w - - 0 1",
  "stipulation": "",
  "moves": [
    {
      "id": "main.1",
      "ply": 1,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p5p/1pp4p/1k6/1p6/1P6/5p1p/5Kbr b - - 1 1",
      "variant": "main",
      "parent": null
    },
    {
      "id": "main.2",
      "ply": 2,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p5p/kpp4p/8/1p6/1P6/5p1p/5Kbr w - - 2 2",
      "variant": "main",
      "parent": "main.1"
    },
    {
      "id": "main.3",
      "ply": 3,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p5p/kpp4p/8/1p6/1P6/5p1p/5Kbr b - - 3 2",
      "variant": "main",
      "parent": "main.2"
    },
    {
      "id": "main.4",
      "ply": 4,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p5p/1pp4p/1k6/1p6/1P6/5p1p/5Kbr w - - 4 3",
      "variant": "main",
      "parent": "main.3"
    },
    {
      "id": "main.5",
      "ply": 5,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p5p/1pp4p/1k6/1p6/1P6/5p1p/Q4Kbr b - - 5 3",
      "variant": "main",
      "parent": "main.4"
    },
    {
      "id": "main.6",
      "ply": 6,
      "san": "h5",
      "nl": "h5",
      "fenAfter": "8/1p5p/1pp5/1k5p/1p6/1P6/5p1p/Q4Kbr w - - 0 4",
      "variant": "main",
      "parent": "main.5"
    },
    {
      "id": "main.7",
      "ply": 7,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p5p/1pp5/1k5p/1p6/1P6/5p1p/5Kbr b - - 1 4",
      "variant": "main",
      "parent": "main.6"
    },
    {
      "id": "main.8",
      "ply": 8,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p5p/kpp5/7p/1p6/1P6/5p1p/5Kbr w - - 2 5",
      "variant": "main",
      "parent": "main.7"
    },
    {
      "id": "main.9",
      "ply": 9,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p5p/kpp5/7p/1p6/1P6/5p1p/5Kbr b - - 3 5",
      "variant": "main",
      "parent": "main.8"
    },
    {
      "id": "main.10",
      "ply": 10,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p5p/1pp5/1k5p/1p6/1P6/5p1p/5Kbr w - - 4 6",
      "variant": "main",
      "parent": "main.9"
    },
    {
      "id": "main.11",
      "ply": 11,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p5p/1pp5/1k5p/1p6/1P6/5p1p/Q4Kbr b - - 5 6",
      "variant": "main",
      "parent": "main.10"
    },
    {
      "id": "main.12",
      "ply": 12,
      "san": "h4",
      "nl": "h4",
      "fenAfter": "8/1p5p/1pp5/1k6/1p5p/1P6/5p1p/Q4Kbr w - - 0 7",
      "variant": "main",
      "parent": "main.11"
    },
    {
      "id": "main.13",
      "ply": 13,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p5p/1pp5/1k6/1p5p/1P6/5p1p/5Kbr b - - 1 7",
      "variant": "main",
      "parent": "main.12"
    },
    {
      "id": "main.14",
      "ply": 14,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p5p/kpp5/8/1p5p/1P6/5p1p/5Kbr w - - 2 8",
      "variant": "main",
      "parent": "main.13"
    },
    {
      "id": "main.15",
      "ply": 15,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p5p/kpp5/8/1p5p/1P6/5p1p/5Kbr b - - 3 8",
      "variant": "main",
      "parent": "main.14"
    },
    {
      "id": "main.16",
      "ply": 16,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p5p/1pp5/1k6/1p5p/1P6/5p1p/5Kbr w - - 4 9",
      "variant": "main",
      "parent": "main.15"
    },
    {
      "id": "main.17",
      "ply": 17,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p5p/1pp5/1k6/1p5p/1P6/5p1p/Q4Kbr b - - 5 9",
      "variant": "main",
      "parent": "main.16"
    },
    {
      "id": "main.18",
      "ply": 18,
      "san": "h3",
      "nl": "h3",
      "fenAfter": "8/1p5p/1pp5/1k6/1p6/1P5p/5p1p/Q4Kbr w - - 0 10",
      "variant": "main",
      "parent": "main.17"
    },
    {
      "id": "main.19",
      "ply": 19,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p5p/1pp5/1k6/1p6/1P5p/5p1p/5Kbr b - - 1 10",
      "variant": "main",
      "parent": "main.18"
    },
    {
      "id": "main.20",
      "ply": 20,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p5p/kpp5/8/1p6/1P5p/5p1p/5Kbr w - - 2 11",
      "variant": "main",
      "parent": "main.19"
    },
    {
      "id": "main.21",
      "ply": 21,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p5p/kpp5/8/1p6/1P5p/5p1p/5Kbr b - - 3 11",
      "variant": "main",
      "parent": "main.20"
    },
    {
      "id": "main.22",
      "ply": 22,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p5p/1pp5/1k6/1p6/1P5p/5p1p/5Kbr w - - 4 12",
      "variant": "main",
      "parent": "main.21"
    },
    {
      "id": "main.23",
      "ply": 23,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p5p/1pp5/1k6/1p6/1P5p/5p1p/Q4Kbr b - - 5 12",
      "variant": "main",
      "parent": "main.22"
    },
    {
      "id": "main.24",
      "ply": 24,
      "san": "h6",
      "nl": "h6",
      "fenAfter": "8/1p6/1pp4p/1k6/1p6/1P5p/5p1p/Q4Kbr w - - 0 13",
      "variant": "main",
      "parent": "main.23"
    },
    {
      "id": "main.25",
      "ply": 25,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p6/1pp4p/1k6/1p6/1P5p/5p1p/5Kbr b - - 1 13",
      "variant": "main",
      "parent": "main.24"
    },
    {
      "id": "main.26",
      "ply": 26,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p6/kpp4p/8/1p6/1P5p/5p1p/5Kbr w - - 2 14",
      "variant": "main",
      "parent": "main.25"
    },
    {
      "id": "main.27",
      "ply": 27,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p6/kpp4p/8/1p6/1P5p/5p1p/5Kbr b - - 3 14",
      "variant": "main",
      "parent": "main.26"
    },
    {
      "id": "main.28",
      "ply": 28,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p6/1pp4p/1k6/1p6/1P5p/5p1p/5Kbr w - - 4 15",
      "variant": "main",
      "parent": "main.27"
    },
    {
      "id": "main.29",
      "ply": 29,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p6/1pp4p/1k6/1p6/1P5p/5p1p/Q4Kbr b - - 5 15",
      "variant": "main",
      "parent": "main.28"
    },
    {
      "id": "main.30",
      "ply": 30,
      "san": "h5",
      "nl": "h5",
      "fenAfter": "8/1p6/1pp5/1k5p/1p6/1P5p/5p1p/Q4Kbr w - - 0 16",
      "variant": "main",
      "parent": "main.29"
    },
    {
      "id": "main.31",
      "ply": 31,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p6/1pp5/1k5p/1p6/1P5p/5p1p/5Kbr b - - 1 16",
      "variant": "main",
      "parent": "main.30"
    },
    {
      "id": "main.32",
      "ply": 32,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p6/kpp5/7p/1p6/1P5p/5p1p/5Kbr w - - 2 17",
      "variant": "main",
      "parent": "main.31"
    },
    {
      "id": "main.33",
      "ply": 33,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p6/kpp5/7p/1p6/1P5p/5p1p/5Kbr b - - 3 17",
      "variant": "main",
      "parent": "main.32"
    },
    {
      "id": "main.34",
      "ply": 34,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p6/1pp5/1k5p/1p6/1P5p/5p1p/5Kbr w - - 4 18",
      "variant": "main",
      "parent": "main.33"
    },
    {
      "id": "main.35",
      "ply": 35,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p6/1pp5/1k5p/1p6/1P5p/5p1p/Q4Kbr b - - 5 18",
      "variant": "main",
      "parent": "main.34"
    },
    {
      "id": "main.36",
      "ply": 36,
      "san": "h4",
      "nl": "h4",
      "fenAfter": "8/1p6/1pp5/1k6/1p5p/1P5p/5p1p/Q4Kbr w - - 0 19",
      "variant": "main",
      "parent": "main.35"
    },
    {
      "id": "main.37",
      "ply": 37,
      "san": "Qh8",
      "nl": "Dh8",
      "fenAfter": "7Q/1p6/1pp5/1k6/1p5p/1P5p/5p1p/5Kbr b - - 1 19",
      "variant": "main",
      "parent": "main.36"
    },
    {
      "id": "main.38",
      "ply": 38,
      "san": "Ka6",
      "nl": "Ka6",
      "fenAfter": "7Q/1p6/kpp5/8/1p5p/1P5p/5p1p/5Kbr w - - 2 20",
      "variant": "main",
      "parent": "main.37"
    },
    {
      "id": "main.39",
      "ply": 39,
      "san": "Qa8+",
      "nl": "Da8+",
      "fenAfter": "Q7/1p6/kpp5/8/1p5p/1P5p/5p1p/5Kbr b - - 3 20",
      "variant": "main",
      "parent": "main.38"
    },
    {
      "id": "main.40",
      "ply": 40,
      "san": "Kb5",
      "nl": "Kb5",
      "fenAfter": "Q7/1p6/1pp5/1k6/1p5p/1P5p/5p1p/5Kbr w - - 4 21",
      "variant": "main",
      "parent": "main.39"
    },
    {
      "id": "main.41",
      "ply": 41,
      "san": "Qa1",
      "nl": "Da1",
      "fenAfter": "8/1p6/1pp5/1k6/1p5p/1P5p/5p1p/Q4Kbr b - - 5 21",
      "variant": "main",
      "parent": "main.40"
    },
    {
      "id": "main.42",
      "ply": 42,
      "san": "c5",
      "nl": "c5",
      "fenAfter": "8/1p6/1p6/1kp5/1p5p/1P5p/5p1p/Q4Kbr w - - 0 22",
      "variant": "main",
      "parent": "main.41"
    },
    {
      "id": "main.43",
      "ply": 43,
      "san": "Qa4#",
      "nl": "Da4#",
      "fenAfter": "8/1p6/1p6/1kp5/Qp5p/1P5p/5p1p/5Kbr b - - 1 22",
      "variant": "main",
      "parent": "main.42"
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
