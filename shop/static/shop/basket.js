document.querySelectorAll(".cart-quantity").forEach((input) => {
  input.addEventListener("input", () => {
    const maximum = Number(input.max);
    const notice = input.closest("form").querySelector(".quantity-notice");
    if (Number(input.value) > maximum) {
      input.value = maximum;
      notice.textContent = `${input.dataset.productName} üçün maksimum mövcud miqdara çatmısınız.`;
      notice.hidden = false;
    } else {
      notice.hidden = true;
    }
  });
});
