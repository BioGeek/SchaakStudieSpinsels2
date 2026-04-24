import { Chessboard, BORDER_TYPE, COLOR, FEN } from 'cm-chessboard';
import 'cm-chessboard/assets/chessboard.css';

interface StudyMove {
  id: string;
  ply: number;
  san: string;
  nl: string;
  fenAfter: string;
  variant: string;
  parent: string | null;
}

interface StudyData {
  number: number;
  fen: string;
  moves: StudyMove[];
}

interface Controller {
  el: HTMLElement;
  board: Chessboard;
  study: StudyData;
  // All move-buttons in this component, in DOM order.
  buttons: HTMLButtonElement[];
  // Parallel array of move-ids (including "" for "start of study").
  ids: (string | '')[];
  // Index into `ids` of the currently-active position.
  active: number;
}

/**
 * Mount an interactive board inside a `.study-board` element.
 *
 * The surrounding Astro component has already laid out the moves list
 * (main line + variants) with `data-move="…"` on each clickable move
 * button. This controller wires those up to the cm-chessboard instance.
 */
export function initStudyBoard(host: HTMLElement): Controller {
  const boardId = host.dataset.boardId!;
  const boardEl = host.querySelector<HTMLElement>(`#${CSS.escape(boardId)}`);
  if (!boardEl) throw new Error(`StudyBoard: missing #${boardId}`);

  const study: StudyData = JSON.parse(host.dataset.study ?? '{}');

  const board = new Chessboard(boardEl, {
    position: study.fen,
    style: {
      borderType: BORDER_TYPE.none,
      pieces: { file: '/pieces/staunty.svg' }, // cm-chessboard default sprite (site-rooted)
    },
    responsive: true,
    animationDuration: 180,
  });

  const buttons = Array.from(host.querySelectorAll<HTMLButtonElement>('button[data-move]'));
  // The controller treats position 0 = start-of-study (no move applied yet),
  // position i = after the i-th button's move. Buttons are already in
  // rendering order, which matches ply order within each variant.
  const ids: (string | '')[] = ['', ...buttons.map((b) => b.dataset.move ?? '')];

  const ctrl: Controller = {
    el: host,
    board,
    study,
    buttons,
    ids,
    active: 0,
  };

  const setActive = (idx: number) => {
    idx = Math.max(0, Math.min(ids.length - 1, idx));
    ctrl.active = idx;
    const targetId = ids[idx];
    const fen =
      targetId === ''
        ? study.fen
        : study.moves.find((m) => m.id === targetId)?.fenAfter ?? study.fen;
    board.setPosition(fen, true);
    buttons.forEach((b, i) => b.classList.toggle('active', i + 1 === idx));
    const activeBtn = idx > 0 ? buttons[idx - 1] : undefined;
    activeBtn?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  };

  // Click-to-jump on move buttons.
  buttons.forEach((b, i) => {
    b.addEventListener('click', () => setActive(i + 1));
  });

  // Nav controls.
  host.querySelectorAll<HTMLButtonElement>('button[data-nav]').forEach((b) => {
    b.addEventListener('click', () => {
      const nav = b.dataset.nav;
      if (nav === 'start') setActive(0);
      else if (nav === 'prev') setActive(ctrl.active - 1);
      else if (nav === 'next') setActive(ctrl.active + 1);
      else if (nav === 'end') setActive(ids.length - 1);
    });
  });

  // Keyboard arrows anywhere within the component.
  host.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); setActive(ctrl.active - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); setActive(ctrl.active + 1); }
    else if (e.key === 'Home') { e.preventDefault(); setActive(0); }
    else if (e.key === 'End') { e.preventDefault(); setActive(ids.length - 1); }
  });

  return ctrl;
}
