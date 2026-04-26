(function () {
  const wilayaSelect = document.querySelector('select[name="wilaya_code"]');
  const deliverySelect = document.querySelector('select[name="delivery_type"]');

  const subtotalEl = document.getElementById("itemsSubtotal"); // جديد
  const productPriceEl = document.getElementById("productPrice");
  const qtyInput = document.getElementById("qtyInput"); // قد لا يكون موجود الآن

  const shippingPriceText = document.getElementById("shippingPriceText");
  const returnFeeText = document.getElementById("returnFeeText");
  const expectedTotalText = document.getElementById("expectedTotalText");
  const shippingErrorBox = document.getElementById("shippingErrorBox");

  if (!wilayaSelect || !deliverySelect) return;

  function formatDZD(value) {
    const num = Number(value || 0);
    return num.toLocaleString("en-US") + " دج";
  }

  function clearError() {
    if (!shippingErrorBox) return;
    shippingErrorBox.style.display = "none";
    shippingErrorBox.textContent = "";
  }

  function setError(msg) {
    if (!shippingErrorBox) return;
    shippingErrorBox.style.display = "block";
    shippingErrorBox.textContent = msg || "حدث خطأ.";
  }

  function getSubtotal() {
    if (subtotalEl && subtotalEl.dataset && subtotalEl.dataset.subtotal) {
      return Number(subtotalEl.dataset.subtotal || 0);
    }
    const price = productPriceEl ? Number(productPriceEl.dataset.price || 0) : 0;
    const qty = qtyInput ? Number(qtyInput.value || 1) : 1;
    return price * qty;
  }

  async function updateShipping() {
    const wilayaCode = (wilayaSelect.value || "").trim();
    const deliveryType = (deliverySelect.value || "").trim();
    const subtotal = getSubtotal();

    clearError();

    if (shippingPriceText) shippingPriceText.textContent = "اختاري الولاية ونوع التوصيل";
    if (returnFeeText) returnFeeText.textContent = "اختاري الولاية";
    if (expectedTotalText) expectedTotalText.textContent = formatDZD(subtotal);

    if (!wilayaCode) return;

    try {
      const response = await fetch(`/api/shipping-info/?wilaya_code=${encodeURIComponent(wilayaCode)}`);
      const data = await response.json();

      if (!data.ok) {
        setError(data.error || "تعذر جلب أسعار التوصيل");
        return;
      }

      let shippingValue = null;
      if (deliveryType === "HOME") shippingValue = data.home;
      if (deliveryType === "OFFICE") shippingValue = data.office;

      if (returnFeeText) {
        returnFeeText.textContent = (data.return_fee == null) ? "غير متاح" : formatDZD(data.return_fee);
      }

      if (shippingValue == null) {
        if (shippingPriceText) shippingPriceText.textContent = "غير متاح";
        setError("التوصيل غير متاح حاليًا لهذه الولاية بهذا النوع من التوصيل.");
        if (expectedTotalText) expectedTotalText.textContent = formatDZD(subtotal);
        return;
      }

      if (shippingPriceText) shippingPriceText.textContent = formatDZD(shippingValue);
      if (expectedTotalText) expectedTotalText.textContent = formatDZD(subtotal + Number(shippingValue));
    } catch (error) {
      setError("حدث خطأ أثناء حساب سعر التوصيل.");
    }
  }

  wilayaSelect.addEventListener("change", updateShipping);
  deliverySelect.addEventListener("change", updateShipping);
  if (qtyInput) qtyInput.addEventListener("input", updateShipping);

  document.addEventListener("items:changed", updateShipping); // جديد
  updateShipping();
})();