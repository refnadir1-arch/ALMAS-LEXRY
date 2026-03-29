(function(){
  const qtyInput = document.querySelector('input[name="qty"]');
  if(!qtyInput) return;

  qtyInput.addEventListener("input", function(){
    const val = parseInt(this.value || "1", 10);
    if(val > 5) this.value = 5;
    if(val < 1) this.value = 1;
  });
})();