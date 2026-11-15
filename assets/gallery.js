"use strict";
(() => {
  const data = JSON.parse(document.getElementById("collection-data").textContent);
  const $ = id => document.getElementById(id);
  let selected = data.characters[0];
  let variantId = selected.featured_variant;
  let comparing = false;
  const buttons = new Map();
  $("collection-count").textContent = data.character_count + " 位角色 / " + data.variant_count + " 套三视图";
  data.characters.forEach((c, index) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "character"; b.dataset.character = c.id;
    b.setAttribute("aria-pressed", "false");
    const title = document.createElement("strong"); title.textContent = c.short_name;
    const count = document.createElement("small"); count.textContent = c.variants.length + " 个版本";
    b.append(title, count); b.addEventListener("click", () => chooseCharacter(c.id));
    $("characters").append(b); buttons.set(c.id, b);
  });
  function changeImage(id, path, alt) {
    const img = $(id); img.src = path; img.alt = alt;
    img.classList.remove("changing");
    requestAnimationFrame(() => img.classList.add("changing"));
  }
  function show() {
    const v = selected.variants.find(v => v.id === variantId);
    buttons.forEach((b, id) => b.setAttribute("aria-pressed", String(id === selected.id)));
    $("character-name").textContent = selected.name;
    $("character-meta").textContent = selected.region + " / " + selected.organization;
    $("character-description").textContent = selected.description;
    $("position").textContent = String(data.characters.indexOf(selected) + 1).padStart(2, "0") + " / 08";
    changeImage("sheet-image", v.image.path, selected.name + " · " + v.label + " · 正面、左侧面、背面");
    $("full-image-link").href = v.image.path;
    $("download-link").href = v.image.path;
    $("download-link").download = selected.id + "-" + v.id + ".png";
    $("version-caption").textContent = v.label + (v.id === "v2-dance" ? " · FRONT / LEFT SIDE / BACK" : " · 历史版本");
    $("image-size").textContent = v.image.width + " × " + v.image.height + " · " + (v.image.bytes / 1048576).toFixed(2) + " MB";
    $("variant-note").textContent = v.notes + (v.quality_note ? " " + v.quality_note : "");
    $("character-doc").href = "characters/" + selected.id + "/README.md";
    $("stages").classList.toggle("compare", comparing);
    $("comparison").hidden = !comparing;
    $("compare-button").setAttribute("aria-pressed", String(comparing));
    if (comparing) {
      const other = v.id === selected.featured_variant ? selected.variants[0] : selected.variants.find(x => x.id === selected.featured_variant);
      changeImage("compare-image", other.image.path, selected.name + " · 对照：" + other.label);
      $("compare-image-link").href = other.image.path;
      $("compare-caption").textContent = "对照：" + other.label;
    }
    $("live-status").textContent = "正在展示 " + selected.name + " 的" + v.label;
    history.replaceState(null, "", "#" + selected.id + "/" + variantId);
  }
  function chooseCharacter(id, requested) {
    selected = data.characters.find(c => c.id === id) || data.characters[0];
    variantId = selected.variants.some(v => v.id === requested) ? requested : selected.featured_variant;
    $("version").replaceChildren();
    [...selected.variants].reverse().forEach(v => {
      const o = document.createElement("option"); o.value = v.id; o.textContent = v.label; $("version").append(o);
    });
    $("version").value = variantId; show();
  }
  $("version").addEventListener("change", e => {variantId = e.target.value; show();});
  $("compare-button").addEventListener("click", () => {comparing = !comparing; show();});
  $("reference-button").addEventListener("click", () => $("reference-dialog").showModal());
  $("close-reference").addEventListener("click", () => $("reference-dialog").close());
  $("reference-dialog").addEventListener("click", e => {if (e.target === $("reference-dialog")) {const r = e.target.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.target.close();}});
  const requested = location.hash.slice(1).split("/");
  chooseCharacter(requested[0], requested[1]);
})();
