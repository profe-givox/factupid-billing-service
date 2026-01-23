document.addEventListener('DOMContentLoaded', function () {
    const originalSelect = document.querySelector('#id_regimen_fiscal_receptor');
    const selectedSelect = document.createElement('select');
    
    selectedSelect.setAttribute('multiple', 'multiple');
    selectedSelect.setAttribute('id', 'selected-regimen-fiscal');
    selectedSelect.style.width = '100%';

    // Añadir un contenedor para mostrar ambos selects
    const container = document.createElement('div');
    container.style.display = 'flex';

    const allBox = document.createElement('div');
    allBox.style.flex = '1';
    allBox.appendChild(originalSelect);
    
    const selectedBox = document.createElement('div');
    selectedBox.style.flex = '1';
    selectedBox.appendChild(selectedSelect);
    
    container.appendChild(allBox);
    container.appendChild(selectedBox);

    // Añadir la funcionalidad para mover elementos entre selects
    originalSelect.addEventListener('change', function () {
        const selectedOptions = Array.from(originalSelect.selectedOptions);
        selectedOptions.forEach(option => {
            selectedSelect.appendChild(option);
        });
    });

    selectedSelect.addEventListener('change', function () {
        const selectedOptions = Array.from(selectedSelect.selectedOptions);
        selectedOptions.forEach(option => {
            originalSelect.appendChild(option);
        });
    });

    // Reemplazar el select original por el nuevo contenedor
    const parent = originalSelect.parentNode;
    parent.replaceChild(container, originalSelect);
});