document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('orderForm');
    const quantityInputs = document.querySelectorAll('.quantity-input');
    const orderSummary = document.getElementById('orderSummary');
    const orderModal = new bootstrap.Modal(document.getElementById('orderConfirmation'));

    // Update order summary when quantities change
    quantityInputs.forEach(input => {
        input.addEventListener('change', updateOrderSummary);
    });

    // Update summary when quantities change
    function updateOrderSummary() {
        let summary = '';
        let hasItems = false;

        quantityInputs.forEach(input => {
            const quantity = parseInt(input.value);
            if (quantity > 0) {
                hasItems = true;
                const row = input.closest('tr');
                const product = row.cells[1].textContent;
                summary += `<div class="mb-2">
                    <strong>${product}</strong>: ${quantity} unidades
                </div>`;
            }
        });

        orderSummary.innerHTML = hasItems ? summary : '<p>Seleccione productos para ver el resumen</p>';
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Check if at least one product is selected
        let hasProducts = false;
        quantityInputs.forEach(input => {
            if (parseInt(input.value) > 0) hasProducts = true;
        });

        if (!hasProducts) {
            alert('Por favor seleccione al menos un producto');
            return;
        }

        // Submit order
        const formData = new FormData(form);        try {
            const response = await fetch('/create_order', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                document.getElementById('orderNumber').textContent = result.order_number;
                orderModal.show();
                form.reset();
                updateOrderSummary();
            } else {
                alert(result.message || 'Error al crear la orden');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al crear la orden. Por favor, inténtelo de nuevo.');
        }
    });
});
