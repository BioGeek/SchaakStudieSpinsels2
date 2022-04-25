window.addEventListener("load", function () {
    "use strict";

    var options = {
        clickable: true,
        draggable: true,
        imagesPath: "../images/",
        markLegalSquares: true
    };
    var abc = new AbChess("chessboard", options);
    console.log(abc)
    console.log(abc.board)
    abc.board.draw();
    abc.board.setFEN();

    var fenSpan = document.getElementById("fen-span");
    var pgnParagraph = document.getElementById("pgn-paragraph");

    abc.board.onMovePlayed(function () {
        fenSpan.innerText = abc.board.getFEN();
        pgnParagraph.innerText = abc.game.getPGN();
    });

});