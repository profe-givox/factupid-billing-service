
document.addEventListener('DOMContentLoaded', function() {
    var saveButton = document.querySelector('button[name="_save"]');
    if (saveButton) {
        var saveAsDraftButton = document.createElement('button');
        saveAsDraftButton.setAttribute('type', 'submit');
        saveAsDraftButton.setAttribute('name', '_guardar_como_borrador');
        saveAsDraftButton.setAttribute('class', 'default');
        saveAsDraftButton.innerText = 'Guardar como borrador';
        saveButton.parentNode.insertBefore(saveAsDraftButton, saveButton.nextSibling);
    }
});