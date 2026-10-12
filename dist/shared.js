'use strict';

// Pure helpers shared by app.js, cycle.js and evidence.js. No DOM access, so Node tests can load this file.
const Shared = (() => {
  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

  // External links must be https without embedded credentials; anything else renders as plain text.
  const safeURL = value => {
    if (typeof value !== 'string') return null;
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
    } catch {
      return null;
    }
  };

  // Control, zero-width and bidirectional formatting characters can hide or reorder text. Whitespace controls become a
  // space; the others are removed.
  const INVISIBLE = /[\u0000-\u0008\u000E-\u001F\u007F-\u009F\u00AD\u061C\u180E\u200B-\u200F\u202A-\u202E\u2060-\u2064\u2066-\u206F\uFEFF\uFFF9-\uFFFB]/g;
  const cleanText = value => typeof value === 'string' ? value.replace(/[\t\n\v\f\r]+/g, ' ').replace(INVISIBLE, '') : value;

  // Managed-cycle start state. Cycle failure takes precedence over freeze exposure; old payloads have no cycle_failure.
  const scanState = (start, favourable) => {
    const loss = start.recurring_crop_loss ?? [];
    if (loss.includes('cycle_failure')) return 'failure';
    if (loss.length) return 'loss';
    if (!start.rankable) return 'unrankable';
    return favourable.has(start.budbreak) ? 'favourable' : 'other';
  };

  // Sums per-start outcomes; null for payloads that predate the four-outcome accounting.
  const scanOutcomes = starts => {
    if (!starts?.length || !starts.every(start => start.outcomes)) return null;
    const total = { complete: 0, stalled_slow: 0, stalled_horizon: 0, weather_incomplete: 0 };
    for (const start of starts) for (const key of Object.keys(total)) total[key] += Number(start.outcomes[key]) || 0;
    return total;
  };

  return Object.freeze({ escapeHTML, safeURL, cleanText, scanState, scanOutcomes });
})();
