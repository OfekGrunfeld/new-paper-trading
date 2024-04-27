document.addEventListener('DOMContentLoaded', function() {
  const orderTypeSelect = document.getElementById('order_type');
  const limitPriceField = document.querySelector('.limit-price-field');
  const stopPriceField = document.querySelector('.stop-price-field');
  const limitPriceInput = document.getElementById('limit_price');
  const stopPriceInput = document.getElementById('stop_price');
  const tradeButton = document.getElementById('trade_form_submit');

  function updateVisibility(selectedOrderType) {
    limitPriceField.classList.add('hidden');
    stopPriceField.classList.add('hidden');
    limitPriceInput.required = false;
    stopPriceInput.required = false;

    if (selectedOrderType === 'limit' || selectedOrderType === 'stop_limit') {
      limitPriceField.classList.remove('hidden');
      limitPriceInput.required = true;
    }

    if (selectedOrderType === 'stop' || selectedOrderType === 'stop_limit') {
      stopPriceField.classList.remove('hidden');
      stopPriceInput.required = true;
    }
  }

  function checkOrderTypeDisabled() {
    // Disable the Trade button if the order type is disabled
    tradeButton.disabled = orderTypeSelect.disabled;
  }

  // Initial calls to set the correct display state when the page loads
  updateVisibility(orderTypeSelect.value);
  checkOrderTypeDisabled();

  // Event listener for when the select value changes
  orderTypeSelect.addEventListener('change', function() {
    updateVisibility(this.value);
    checkOrderTypeDisabled();
  });
});