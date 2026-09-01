// controllers/options.js
//
// Suppliers, customers and items for the invoice pickers.
//
// These are the site's biggest masters (tens of thousands of rows), the app
// runs on phones, and the whole set used to be downloaded again on every
// visit to the invoice screen. It is now stored on the device instead: the
// lists render from localStorage with no network at all, and the server is
// only asked for a version stamp. Nothing is cached on the server.
import axios from "axios";

const STORAGE_KEY = "ifv_options_v1";
const LISTS = ["suppliers", "customers", "items"];

// Cap on how many matches an overlay is asked to render at once. Filtering
// stays instant; drawing 18,000 rows on a phone does not.
export const MAX_SUGGESTIONS = 50;

// Held for the lifetime of the tab so moving between Drafts and an invoice
// costs nothing. `inflight` collapses concurrent callers onto one request.
let cache = null;
let inflight = null;

/**
 * Display label for a picker option.
 *
 * Shows "(name) code" so both halves are searchable and visible, and falls
 * back to the code alone when the name adds nothing.
 */
export function formatOption(code, name) {
  code = (code || "").toString();
  name = (name || "").toString();

  return {
    label: name && name !== code ? `(${name}) ${code}` : code,
    code,
    name,
    // Precomputed once here rather than lowercasing every entry on every
    // keystroke, and it lets a search match the code or the name.
    search: `${name} ${code}`.toLowerCase(),
  };
}

/** Options whose code or name contains `query`, capped for rendering. */
export function filterOptions(list, query, limit = MAX_SUGGESTIONS) {
  const needle = (query || "").trim().toLowerCase();
  const matches = [];

  for (const option of list || []) {
    if (!needle || option.search.includes(needle)) {
      matches.push(option);
      if (matches.length >= limit) break;
    }
  }

  return matches;
}

function readStored() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const stored = JSON.parse(raw);
    if (!stored?.version || !LISTS.every((key) => Array.isArray(stored[key]))) {
      return null;
    }
    return stored;
  } catch (error) {
    // Corrupt entry, private browsing, storage disabled: fall back to the
    // network rather than failing the screen.
    console.warn("Could not read cached options:", error);
    return null;
  }
}

function writeStored(payload) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch (error) {
    // Out of quota or storage unavailable. The lists still work for this
    // session, they just will not survive a restart.
    console.warn("Could not cache options on this device:", error);
  }
}

/** Turn the server's compact [code, name] rows into picker options. */
function toOptions(payload) {
  const options = { version: payload.version };
  for (const key of LISTS) {
    options[key] = (payload[key] || []).map(([code, name]) =>
      formatOption(code, name)
    );
  }
  return options;
}

async function fetchOptions(knownVersion) {
  const response = await axios.get(
    "/api/method/invoice_form_vue.api.get_suppliers_and_customers",
    { params: knownVersion ? { version: knownVersion } : {} }
  );

  return response.data?.message || response.data;
}

/**
 * Load the picker lists.
 *
 * `onUpdate` is called with the options as soon as they are available from
 * the device, and again only if the server reports a change, so a screen can
 * paint immediately and still pick up an edit made in the desk.
 */
export async function loadOptions(onUpdate) {
  if (!cache) {
    const stored = readStored();
    if (stored) cache = toOptions(stored);
  }

  // Hand over whatever is on hand first; the screen can render from it.
  if (cache) onUpdate?.(cache);

  if (!inflight) {
    const knownVersion = cache?.version;
    inflight = (async () => {
      try {
        const payload = await fetchOptions(knownVersion);

        // Same version: what is already on the device is current.
        if (payload?.unchanged) return cache;

        cache = toOptions(payload);
        writeStored(payload);
        return cache;
      } finally {
        inflight = null;
      }
    })();
  }

  // Held before awaiting, so the comparison below sees what this caller was
  // actually given rather than whatever the request has since replaced.
  const emitted = cache;

  try {
    const fresh = await inflight;
    if (fresh && fresh !== emitted) onUpdate?.(fresh);
    return fresh;
  } catch (error) {
    // Offline or the request failed. Whatever the device already holds is
    // better than an empty picker.
    if (cache) return cache;
    throw error;
  }
}

/** Drop the device copy and re-download on the next load. */
export function clearOptionsCache() {
  cache = null;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn("Could not clear cached options:", error);
  }
}
