document.addEventListener('DOMContentLoaded', function() {
    const orderTypeSelect = document.getElementById('order_type');
    const limitPriceField = document.querySelector('.limit-price-field');
    const stopPriceField = document.querySelector('.stop-price-field');

    function updateVisibility(selectedOrderType) {
        limitPriceField.classList.add('hidden');
        stopPriceField.classList.add('hidden');

        if (selectedOrderType === 'limit' || selectedOrderType === 'stop_limit') {
            limitPriceField.classList.remove('hidden');
        }

        if (selectedOrderType === 'stop' || selectedOrderType === 'stop_limit') {
            stopPriceField.classList.remove('hidden');
        }
    }

    // Initial call to set the correct display state when the page loads
    updateVisibility(orderTypeSelect.value);

    // Event listener for when the select value changes
    orderTypeSelect.addEventListener('change', function() {
        updateVisibility(orderTypeSelect.value);
    });
  });