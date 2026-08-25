(() => {
  const input = document.getElementById("product-search");
  const panel = document.getElementById("search-suggestions");
  const data = document.getElementById("product-search-data");
  if (!input || !panel || !data) return;

  const products = JSON.parse(data.textContent);
  const render = () => {
    const query = input.value.trim().toLocaleLowerCase("az");
    const matches = products.filter((product) => `${product.name} ${product.part_number}`.toLocaleLowerCase("az").includes(query)).slice(0, 12);
    panel.replaceChildren();
    if (!matches.length) {
      panel.innerHTML = '<div class="search-empty">Uyğun məhsul tapılmadı.</div>';
    } else {
      matches.forEach((product) => {
        const item = document.createElement("a");
        item.className = "search-suggestion";
        item.href = `/?q=${encodeURIComponent(product.part_number)}`;
        item.innerHTML = `<span><strong></strong><small></small></span><em></em>`;
        item.querySelector("strong").textContent = product.name;
        item.querySelector("small").textContent = `ID: ${product.id} · Kod: ${product.part_number}`;
        const stock = item.querySelector("em");
        stock.textContent = product.is_available ? "Mövcuddur" : "Mövcud deyil";
        if (!product.is_available) stock.classList.add("off");
        panel.appendChild(item);
      });
    }
    panel.hidden = false;
    input.setAttribute("aria-expanded", "true");
  };
  const hide = () => window.setTimeout(() => { panel.hidden = true; input.setAttribute("aria-expanded", "false"); }, 150);
  input.addEventListener("focus", render);
  input.addEventListener("input", render);
  input.addEventListener("blur", hide);
  input.addEventListener("keydown", (event) => { if (event.key === "Escape") { panel.hidden = true; input.blur(); } });
})();
