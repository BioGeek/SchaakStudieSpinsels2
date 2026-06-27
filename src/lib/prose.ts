// Render study prose to safe HTML. The prose is plain text except for
// cross-reference links written as `[label](study:N)` (added by
// scripts/apply_xref or by hand), which point to another study. We HTML-escape
// everything first, then turn those markers into locale-aware <a> links — so
// no raw HTML from the content can leak through.
const STUDY_LINK = /\[([^\]]+)\]\(study:(\d+)\)/g;

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

export function renderProse(text: string, locale: string): string {
  return escapeHtml(text).replace(STUDY_LINK, (_m, label: string, num: string) => {
    const n = String(num).padStart(3, '0');
    return `<a href="/${locale}/studies/${n}" class="study-xref">${label}</a>`;
  });
}
