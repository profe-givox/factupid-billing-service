(function () {
  const MIN_QUERY_LENGTH = 3;
  let isPopulating = false;

  const FORMSET_CONFIG = {
    nominaPercepciones: {
      addButtonSelector: '#agregar-percepcion',
      totalFormsId: 'id_nominaPercepciones-TOTAL_FORMS',
      initialFormsId: 'id_nominaPercepciones-INITIAL_FORMS',
    },
    nominaDeducciones: {
      addButtonSelector: '#agregar-deduccion',
      totalFormsId: 'id_nominaDeducciones-TOTAL_FORMS',
      initialFormsId: 'id_nominaDeducciones-INITIAL_FORMS',
    },
    nominaOtrosPagos: {
      addButtonSelector: '#agregar-otro-pago',
      totalFormsId: 'id_nominaOtrosPagos-TOTAL_FORMS',
      initialFormsId: 'id_nominaOtrosPagos-INITIAL_FORMS',
    },
    subcontrataciones: {
      addButtonSelector: '#agregar-subcontratacion',
      totalFormsId: 'id_subcontrataciones-TOTAL_FORMS',
      initialFormsId: 'id_subcontrataciones-INITIAL_FORMS',
    },
  };

  function createDatalist(input) {
    const datalistId = input.id ? `${input.id}-nomina-suggestions` : `${input.name}-nomina-suggestions`;
    let datalist = document.getElementById(datalistId);
    if (!datalist) {
      datalist = document.createElement('datalist');
      datalist.id = datalistId;
      input.setAttribute('list', datalistId);
      input.parentNode.appendChild(datalist);
    }
    return datalist;
  }

  function normalizeValue(value) {
    if (value === null || typeof value === 'undefined') {
      return '';
    }
    return typeof value === 'number' ? value.toString() : String(value);
  }

  function dispatchInputEvents(element) {
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function dispatchChangeEvent(element) {
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function applyValueToElement(element, rawValue) {
    if (!element) {
      return;
    }

    if (element.type === 'checkbox') {
      const checked = Boolean(rawValue) && rawValue !== '0' && rawValue !== 'false' && rawValue !== 'False';
      if (element.checked !== checked) {
        element.checked = checked;
        dispatchChangeEvent(element);
      }
      return;
    }

    const normalizedValue = normalizeValue(rawValue);
    if (element.tagName === 'SELECT') {
      if (element.value !== normalizedValue) {
        element.value = normalizedValue;
        dispatchChangeEvent(element);
      }
      return;
    }

    if (element.value !== normalizedValue) {
      element.value = normalizedValue;
      dispatchInputEvents(element);
    }
  }

  function buildNameSelector(name) {
    if (window.CSS && typeof window.CSS.escape === 'function') {
      return `[name="${window.CSS.escape(name)}"]`;
    }
    return `[name="${name.replace(/"/g, '\\"')}"]`;
  }

  function fillNominaFields(input, fields) {
    if (!fields || typeof fields !== 'object') {
      return;
    }

    const nameParts = input.name.split('-');
    if (nameParts.length < 2) {
      return;
    }
    const baseName = nameParts.slice(0, -1).join('-');

    Object.entries(fields).forEach(([key, value]) => {
      const targetName = `${baseName}-${key}`;
      const fieldElement = document.querySelector(buildNameSelector(targetName));
      applyValueToElement(fieldElement, value);
    });
  }

  function getFormsetConfig(prefix) {
    const config = FORMSET_CONFIG[prefix] || {};
    return {
      addButtonSelector: config.addButtonSelector || null,
      totalFormsId: config.totalFormsId || `id_${prefix}-TOTAL_FORMS`,
      initialFormsId: config.initialFormsId || `id_${prefix}-INITIAL_FORMS`,
    };
  }

  function setDeleteField(prefix, index, shouldDelete) {
    const selector = buildNameSelector(`${prefix}-${index}-DELETE`);
    const deleteField = document.querySelector(selector);
    if (!deleteField) {
      return;
    }
    if (deleteField.checked !== shouldDelete) {
      deleteField.checked = shouldDelete;
      dispatchChangeEvent(deleteField);
    }
  }

  function clearFormFields(prefix, index) {
    const selector = `[name^="${prefix}-${index}-"]`;
    const elements = document.querySelectorAll(selector);
    elements.forEach((element) => {
      if (element.name.endsWith('-DELETE')) {
        setDeleteField(prefix, index, false);
        return;
      }
      if (element.name.endsWith('-id')) {
        return;
      }
      if (element.type === 'checkbox') {
        if (element.checked) {
          element.checked = false;
          dispatchChangeEvent(element);
        }
        return;
      }
      if (element.value !== '') {
        element.value = '';
        if (element.tagName === 'SELECT') {
          dispatchChangeEvent(element);
        } else {
          dispatchInputEvents(element);
        }
      }
    });
  }

  function ensureFormsetForms(prefix, requiredCount) {
    if (!requiredCount || requiredCount < 0) {
      requiredCount = 0;
    }
    const { addButtonSelector, totalFormsId } = getFormsetConfig(prefix);
    const totalFormsInput = document.getElementById(totalFormsId);
    if (!totalFormsInput) {
      return 0;
    }

    let total = parseInt(totalFormsInput.value, 10);
    if (Number.isNaN(total)) {
      total = 0;
    }

    const addButton = addButtonSelector ? document.querySelector(addButtonSelector) : null;

    while (total < requiredCount) {
      if (!addButton) {
        break;
      }
      addButton.click();
      const updatedTotal = parseInt(totalFormsInput.value, 10);
      if (Number.isNaN(updatedTotal) || updatedTotal <= total) {
        break;
      }
      total = updatedTotal;
    }

    return total;
  }

  function setFormsetFieldValue(prefix, index, fieldName, value) {
    const targetName = `${prefix}-${index}-${fieldName}`;
    const fieldElement = document.querySelector(buildNameSelector(targetName));
    applyValueToElement(fieldElement, value);
  }

  function fillFormset(prefix, records) {
    const entries = Array.isArray(records) ? records : [];
    const { totalFormsId, initialFormsId } = getFormsetConfig(prefix);
    const totalFormsInput = document.getElementById(totalFormsId);
    if (!totalFormsInput) {
      return;
    }

    ensureFormsetForms(prefix, entries.length);

    entries.forEach((record, index) => {
      setDeleteField(prefix, index, false);
      if (!record || typeof record !== 'object') {
        return;
      }
      Object.entries(record).forEach(([fieldName, value]) => {
        setFormsetFieldValue(prefix, index, fieldName, value);
      });
    });

    const total = parseInt(totalFormsInput.value, 10);
    const initialInput = document.getElementById(initialFormsId);
    const initialCount = initialInput ? parseInt(initialInput.value, 10) || 0 : 0;

    if (Number.isNaN(total)) {
      return;
    }

    for (let index = entries.length; index < total; index += 1) {
      if (index < initialCount) {
        setDeleteField(prefix, index, true);
      } else {
        clearFormFields(prefix, index);
      }
    }
  }

  function populateFromSuggestion(input, suggestion) {
    if (!suggestion || typeof suggestion !== 'object') {
      return;
    }

    if (isPopulating) {
      return;
    }

    isPopulating = true;

    try {
      if (suggestion.fields) {
        fillNominaFields(input, suggestion.fields);
      }

      fillFormset('nominaPercepciones', suggestion.percepciones);
      fillFormset('nominaDeducciones', suggestion.deducciones);
      fillFormset('nominaOtrosPagos', suggestion.otros_pagos);
      fillFormset('subcontrataciones', suggestion.subcontrataciones);
    } finally {
      isPopulating = false;
    }
  }

  function initAutocomplete(input) {
    if (input.dataset.nominaAutocompleteInitialized === 'true') {
      return;
    }

    const url = input.dataset.autocompleteUrl;
    const field = input.dataset.autocompleteField;

    if (!url || !field) {
      return;
    }

    input.dataset.nominaAutocompleteInitialized = 'true';
    const datalist = createDatalist(input);
    let lastResults = [];
    let lastTerm = '';

    input.addEventListener('input', () => {
      if (isPopulating) {
        return;
      }
      const term = input.value.trim();
      if (term.length < MIN_QUERY_LENGTH) {
        datalist.innerHTML = '';
        lastResults = [];
        lastTerm = '';
        return;
      }

      if (term === lastTerm) {
        return;
      }
      lastTerm = term;

      const params = new URLSearchParams({ term, field });
      fetch(`${url}?${params.toString()}`, { credentials: 'include' })
        .then((response) => (response.ok ? response.json() : Promise.resolve({ results: [] })))
        .then((data) => {
          lastResults = Array.isArray(data.results) ? data.results : [];
          datalist.innerHTML = '';
          lastResults.forEach((item) => {
            if (!item || !item.value) {
              return;
            }
            const option = document.createElement('option');
            option.value = item.value;
            if (item.label) {
              option.label = item.label;
            }
            datalist.appendChild(option);
          });
        })
        .catch(() => {
          datalist.innerHTML = '';
          lastResults = [];
        });
    });

    input.addEventListener('change', () => {
      if (isPopulating) {
        return;
      }
      const value = input.value.trim();
      if (!value) {
        return;
      }
      const match = lastResults.find((item) => item && item.value === value);
      if (match) {
        populateFromSuggestion(input, match);
      }
    });
  }

  function scanInputs() {
    const inputs = document.querySelectorAll('input.nomina-autocomplete');
    inputs.forEach(initAutocomplete);
  }

  if (document.readyState !== 'loading') {
    scanInputs();
  } else {
    document.addEventListener('DOMContentLoaded', scanInputs);
  }

  const observer = new MutationObserver(() => {
    scanInputs();
  });

  observer.observe(document.documentElement || document.body, {
    childList: true,
    subtree: true,
  });
})();