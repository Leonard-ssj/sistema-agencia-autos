(function($) {
    $(document).ready(function() {
        // Funcion para actualizar precio y subtotal cuando se selecciona un vehiculo
        function actualizarPrecioSubtotal(row) {
            var vehiculoSelect = row.find('select[name$="-vehiculo"]');
            var cantidadInput = row.find('input[name$="-cantidad"]');
            var precioInput = row.find('input[name$="-precio_unitario"]');
            var subtotalInput = row.find('input[name$="-subtotal"]');
            
            if (vehiculoSelect.val()) {
                // Obtener precio del vehiculo via AJAX
                $.ajax({
                    url: '/admin/core/vehiculo/' + vehiculoSelect.val() + '/change/',
                    success: function(data) {
                        // Extraer precio del HTML
                        var parser = new DOMParser();
                        var doc = parser.parseFromString(data, 'text/html');
                        var precioField = doc.querySelector('input[name="precio"]');
                        if (precioField) {
                            var precio = parseFloat(precioField.value);
                            var cantidad = parseInt(cantidadInput.val()) || 1;
                            
                            precioInput.val(precio.toFixed(2));
                            subtotalInput.val((precio * cantidad).toFixed(2));
                        }
                    }
                });
            }
        }
        
        // Aplicar a todas las filas existentes
        $('.dynamic-detalle_venta_set').each(function() {
            var row = $(this);
            row.find('select[name$="-vehiculo"]').change(function() {
                actualizarPrecioSubtotal(row);
            });
            row.find('input[name$="-cantidad"]').change(function() {
                actualizarPrecioSubtotal(row);
            });
        });
        
        // Aplicar a nuevas filas que se agreguen
        $('.add-row a').click(function() {
            setTimeout(function() {
                $('.dynamic-detalle_venta_set:last').each(function() {
                    var row = $(this);
                    row.find('select[name$="-vehiculo"]').change(function() {
                        actualizarPrecioSubtotal(row);
                    });
                    row.find('input[name$="-cantidad"]').change(function() {
                        actualizarPrecioSubtotal(row);
                    });
                });
            }, 100);
        });
    });
})(django.jQuery);
