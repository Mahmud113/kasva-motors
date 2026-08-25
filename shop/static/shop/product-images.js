(() => {
  const dialog = document.getElementById("product-image-dialog");
  if (!dialog) return;
  const image = dialog.querySelector("img");
  const caption = dialog.querySelector("p");
  document.querySelectorAll("[data-product-image]").forEach((button) => button.addEventListener("click", () => {
    image.src = button.dataset.productImage;
    image.alt = button.dataset.productName;
    caption.textContent = button.dataset.productName;
    dialog.showModal();
  }));
  dialog.querySelector(".image-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
})();
