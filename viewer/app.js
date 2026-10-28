/* Read-only catalogue explorer. All category records come from the canonical JSON. */
(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const pageSize = 12;
  const selected = { activity: new Set(), characteristic: new Set() };
  let catalogue;
  let activities = [];
  let characteristics = [];
  let byId = new Map();
  let page = 1;
  let exampleJSON = "";
  let exampleInView = false;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function normalise(value) {
    const entities = { amp: "&", quot: '"', apos: "'", lt: "<", gt: ">", nbsp: " " };
    return String(value)
      .replace(/&(#x[\da-f]+|#\d+|amp|quot|apos|lt|gt|nbsp);/gi, (match, entity) => {
        if (!entity.startsWith("#")) return entities[entity.toLowerCase()];
        const code = entity[1].toLowerCase() === "x" ? parseInt(entity.slice(2), 16) : Number(entity.slice(1));
        return code >= 0 && code <= 0x10ffff ? String.fromCodePoint(code) : match;
      })
      .normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase()
      .replace(/&/g, " and ").replace(/[^\p{L}\p{N}]+/gu, " ").trim();
  }

  function wordsMatch(query, text) {
    const words = normalise(text).split(" ");
    return query.split(" ").every((part) => words.some((word) => part.length <= 2 ? word === part : word.startsWith(part)));
  }

  function searchActivities(query) {
    const groupId = $("group").value;
    const candidates = activities.filter((category) => groupId === "all" || category.groupId === groupId);
    if (!query) return candidates;
    const matches = [];
    for (const category of candidates) {
      let rank;
      if (query === normalise(category.id)) rank = 0;
      else if (query === normalise(category.name)) rank = 1;
      else if (category.aliases.some((alias) => normalise(alias.alias) === query)) rank = 2;
      else if (wordsMatch(query, category.name)) rank = 3;
      else if (category.aliases.some((alias) => wordsMatch(query, alias.alias))) rank = 4;
      else continue;
      matches.push({ category, rank });
    }
    const best = Math.min(...matches.map((match) => match.rank));
    const cutoff = best === 0 ? 0 : best <= 2 ? 2 : 4;
    return matches.filter((match) => match.rank <= cutoff)
      .sort((a, b) => a.rank - b.rank || a.category.name.localeCompare(b.category.name, "en-AU"))
      .map((match) => match.category);
  }

  function announce(message) {
    if ($("details-dialog").open) $("detail-status").textContent = message;
    else {
      $("announcement").classList.toggle("sr-only", !message.includes("limit reached"));
      $("announcement").textContent = message;
    }
  }

  function updateToggle(button, category) {
    const active = selected[category.kind].has(category.id);
    const full = button.dataset.fullLabel === "true";
    button.setAttribute("aria-pressed", String(active));
    button.setAttribute("aria-label", `${active ? "Remove" : "Add"} ${category.name} ${active ? "from" : "to"} example`);
    button.textContent = active ? (full ? "Remove from example" : "✓ Added") : "+ Add to example";
  }

  function toggleButton(category) {
    const button = element("button", "add-button");
    button.type = "button";
    button.dataset.toggle = category.id;
    updateToggle(button, category);
    return button;
  }

  function aliasList(category, list) {
    list.replaceChildren();
    for (const alias of category.aliases) {
      const item = element("li");
      item.append(element("strong", "", alias.alias), document.createTextNode(` — ${alias.note}`));
      list.append(item);
    }
  }

  function renderActivities() {
    const rawQuery = $("search").value.trim();
    const query = normalise(rawQuery);
    const matches = rawQuery && !query ? [] : searchActivities(query);
    const pages = Math.max(1, Math.ceil(matches.length / pageSize));
    page = Math.min(page, pages);
    const start = (page - 1) * pageSize;
    const visible = matches.slice(start, start + pageSize);
    const list = $("activity-list");
    list.replaceChildren();
    for (const category of visible) {
      const article = element("article", "activity-row");
      article.dataset.categoryId = category.id;
      const heading = element("h3");
      const inspect = element("button", "activity-name", category.name);
      inspect.type = "button";
      inspect.dataset.inspect = category.id;
      inspect.setAttribute("aria-label", `View ${category.name} details`);
      heading.append(inspect);
      const meta = element("div", "row-meta");
      const context = element("span");
      context.append(element("code", "", category.id), element("span", "inspect-hint", " · View details & search terms"));
      meta.append(context, toggleButton(category));
      article.append(element("p", "activity-group", category.group), heading,
        element("p", "description", category.description), meta);
      list.append(article);
    }
    $("result-count").textContent = matches.length
      ? `${start + 1}–${Math.min(start + pageSize, matches.length)} of ${matches.length} activities`
      : "0 matching activities";
    $("empty-results").hidden = matches.length !== 0;
    $("previous").disabled = page <= 1 || matches.length === 0;
    $("next").disabled = page >= pages || matches.length === 0;
    $("page-number").textContent = matches.length ? `Page ${page} of ${pages}` : "No results";
    $("clear-search").hidden = !rawQuery;
    $("reset-filters").hidden = !rawQuery && $("group").value === "all";
  }

  function renderCharacteristics() {
    const list = $("characteristic-list");
    list.replaceChildren();
    for (const category of characteristics) {
      const article = element("article", "characteristic");
      article.dataset.categoryId = category.id;
      const meta = element("div", "row-meta");
      meta.append(element("code", "", category.id), toggleButton(category));
      article.append(element("h3", "", category.name), element("p", "description", category.description), meta);
      if (category.aliases.length) {
        const details = element("details");
        const terms = element("ul", "alias-list");
        aliasList(category, terms);
        details.append(element("summary", "", `Known search terms (${category.aliases.length})`), terms);
        article.append(details);
      }
      list.append(article);
    }
  }

  function renderSelected(kind, target, placeholder, counter) {
    const list = $(target);
    list.replaceChildren();
    for (const id of selected[kind]) {
      const category = byId.get(id);
      const item = element("li");
      const text = element("span", "", category.name);
      text.append(element("code", "", category.id));
      const remove = element("button", "remove-button", "×");
      remove.type = "button";
      remove.dataset.remove = id;
      remove.setAttribute("aria-label", `Remove ${category.name} from example`);
      item.append(text, remove);
      list.append(item);
    }
    $(placeholder).hidden = selected[kind].size !== 0;
    $(counter).textContent = `${selected[kind].size} / 3`;
  }

  function renderExample() {
    renderSelected("activity", "selected-activities", "no-activities", "activity-selection-count");
    renderSelected("characteristic", "selected-characteristics", "no-characteristics", "characteristic-selection-count");
    const valid = selected.activity.size >= 1 && selected.activity.size <= 3 && selected.characteristic.size <= 3;
    $("validity").textContent = valid ? "✓ Complete example classification" : "Incomplete — choose at least one activity.";
    $("validity").classList.toggle("complete", valid);
    exampleJSON = valid ? JSON.stringify({
      catalogueId: catalogue.catalogueId, version: catalogue.version,
      activities: [...selected.activity], characteristics: [...selected.characteristic],
    }, null, 2) : "";
    $("example-json").textContent = exampleJSON || "Choose an activity to generate a complete example.";
    $("copy-json").disabled = !valid;
    const hasSelections = selected.activity.size + selected.characteristic.size > 0;
    $("clear-example").disabled = !hasSelections;
    $("example-shortcut").hidden = !hasSelections || exampleInView;
    $("shortcut-count").textContent = `· ${selected.activity.size} ${selected.activity.size === 1 ? "activity" : "activities"}, ${selected.characteristic.size} ${selected.characteristic.size === 1 ? "characteristic" : "characteristics"}`;
    $("copy-status").textContent = "";
    document.querySelectorAll("button[data-toggle]").forEach((button) => updateToggle(button, byId.get(button.dataset.toggle)));
  }

  function toggleSelection(id) {
    const category = byId.get(id);
    if (!category) return;
    const entries = selected[category.kind];
    if (entries.has(id)) {
      entries.delete(id);
      announce(`${category.name} removed from the example.`);
    } else {
      if (entries.size >= 3) {
        announce(category.kind === "activity"
          ? "Activity limit reached. Remove an activity before adding another; the maximum is three."
          : "Characteristic limit reached. Remove a characteristic before adding another; the maximum is three.");
        return;
      }
      entries.add(id);
      announce(`${category.name} added to the example.`);
    }
    renderExample();
  }

  function showDetails(id) {
    const category = byId.get(id);
    $("detail-name").textContent = category.name;
    $("detail-group").textContent = category.group;
    $("detail-id").textContent = category.id;
    $("detail-description").textContent = category.description;
    aliasList(category, $("detail-aliases"));
    $("detail-no-aliases").hidden = category.aliases.length !== 0;
    $("detail-add").dataset.toggle = id;
    $("detail-add").dataset.fullLabel = "true";
    $("detail-status").textContent = "";
    $("announcement").textContent = "";
    updateToggle($("detail-add"), category);
    $("details-dialog").showModal();
  }

  function resetFilters() {
    $("search").value = "";
    $("group").value = "all";
    page = 1;
    renderActivities();
  }

  function validateData(data) {
    if (typeof data.catalogueId !== "string" || typeof data.version !== "string" || !Array.isArray(data.groups)) {
      throw new Error("Missing catalogue metadata");
    }
    const ids = new Set();
    for (const group of data.groups) {
      if (typeof group.id !== "string" || typeof group.name !== "string" || !Array.isArray(group.categories)) throw new Error("Invalid group");
      for (const category of group.categories) {
        if (typeof category.id !== "string" || ids.has(category.id) || typeof category.name !== "string"
          || typeof category.description !== "string" || !["activity", "characteristic"].includes(category.kind)
          || !Array.isArray(category.aliases) || category.aliases.some((alias) => typeof alias.alias !== "string" || typeof alias.note !== "string")) {
          throw new Error("Invalid category record");
        }
        ids.add(category.id);
      }
    }
  }

  async function load() {
    $("loading").hidden = false;
    $("load-error").hidden = true;
    $("explorer").hidden = true;
    $("retry").disabled = true;
    try {
      const response = await fetch(new URL("./taxonomy/categories.json", document.baseURI));
      if (!response.ok) throw new Error(`Catalogue request failed (${response.status})`);
      const data = await response.json();
      validateData(data);
      catalogue = data;
      const categories = data.groups.flatMap((group) => group.categories.map((category) => ({ ...category, group: group.name, groupId: group.id })));
      byId = new Map(categories.map((category) => [category.id, category]));
      activities = categories.filter((category) => category.kind === "activity");
      characteristics = categories.filter((category) => category.kind === "characteristic");
      document.querySelectorAll('[data-count="activities"]').forEach((node) => { node.textContent = activities.length; });
      document.querySelectorAll('[data-count="characteristics"]').forEach((node) => { node.textContent = characteristics.length; });
      $("catalogue-version").textContent = `v${data.version} · ${data.groups.length} groups`;
      $("footer-version").textContent = `· v${data.version}`;
      const groupSelect = $("group");
      groupSelect.replaceChildren(new Option("All industry groups", "all"));
      for (const group of data.groups) {
        const count = group.categories.filter((category) => category.kind === "activity").length;
        if (count) groupSelect.append(new Option(`${group.name} (${count})`, group.id));
      }
      const mappingExample = byId.get("c0053");
      if (mappingExample) {
        $("mapping-name").textContent = mappingExample.name;
        $("mapping-id").textContent = mappingExample.id;
        $("mapping-example").hidden = false;
      }
      renderActivities();
      renderCharacteristics();
      renderExample();
      $("explorer").hidden = false;
    } catch (error) {
      $("load-error").hidden = false;
      $("error-message").textContent = location.protocol === "file:"
        ? "Open the viewer through a local HTTP server so it can read the catalogue. The local running instructions show the command."
        : "Please retry. If the problem continues, check that the viewer is hosted alongside the catalogue files.";
      $("catalogue-version").textContent = "Catalogue unavailable";
      console.error(error);
    } finally {
      $("loading").hidden = true;
      $("retry").disabled = false;
    }
  }

  $("filters").addEventListener("submit", (event) => event.preventDefault());
  $("search").addEventListener("input", () => { page = 1; renderActivities(); });
  $("group").addEventListener("change", () => { page = 1; renderActivities(); });
  $("clear-search").addEventListener("click", () => { $("search").value = ""; page = 1; renderActivities(); $("search").focus(); });
  $("reset-filters").addEventListener("click", resetFilters);
  $("show-all").addEventListener("click", resetFilters);
  $("previous").addEventListener("click", () => { if (page > 1) { page -= 1; renderActivities(); } });
  $("next").addEventListener("click", () => { page += 1; renderActivities(); });
  $("retry").addEventListener("click", load);
  $("clear-example").addEventListener("click", () => { selected.activity.clear(); selected.characteristic.clear(); announce(""); renderExample(); });
  $("close-detail").addEventListener("click", () => $("details-dialog").close());
  $("details-dialog").addEventListener("click", (event) => { if (event.target === $("details-dialog")) { const r = event.target.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) event.target.close(); } });
  document.addEventListener("click", (event) => {
    const toggle = event.target.closest("button[data-toggle], button[data-remove]");
    if (toggle) toggleSelection(toggle.dataset.toggle || toggle.dataset.remove);
    const inspect = event.target.closest("button[data-inspect]");
    if (inspect) showDetails(inspect.dataset.inspect);
  });
  $("copy-json").addEventListener("click", async () => {
    if (!exampleJSON) return;
    try {
      await navigator.clipboard.writeText(exampleJSON);
      $("copy-status").textContent = "JSON copied.";
    } catch {
      $("json-details").open = true;
      const range = document.createRange();
      range.selectNodeContents($("example-json"));
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      $("example-json").parentElement.focus();
      $("copy-status").textContent = "Clipboard unavailable. The JSON is selected; use your browser’s Copy command.";
    }
  });
  new IntersectionObserver(([entry]) => {
    exampleInView = entry.isIntersecting;
    $("example-shortcut").hidden = exampleInView || selected.activity.size + selected.characteristic.size === 0;
  }, { threshold: 0.1 }).observe($("example"));
  load();
})();
