---
title: "Bienvenido a Factupid"
description: "Centraliza tus CFDI, reportes y cumplimiento fiscal en un solo lugar."
featured_image: "/imagenes/cfdi-fondo.png"
---

Bienvenido a **Factupid**, la forma rapida de interpretar tus CFDI y tomar decisiones con datos confiables.

## Que puedes hacer
- Subir y validar CFDI masivamente sin complicaciones.
- Obtener reportes financieros y metricas en tiempo real.
- Detectar anomalias y riesgos antes de presentar declaraciones.

## Por que elegirnos
- Catalogos SAT al dia para asegurar cumplimiento.
- Tablero claro para tu equipo contable y de negocio.
- Integraciones listas con tus sistemas y servicios web.

<section class="services-plans" data-checkout-start="http://127.0.0.1:8000/checkout/start">
  <h2>Tenemos el paquete que se adapta a tu necesidad</h2>
  <p>Consulta los planes disponibles por servicio y tipo de integracion.</p>
  <div class="plans-grid">
    <div class="plan-card plan-orange">
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 10</span>
      </div>
      <h3>OnDemand</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="ondemand" data-plan-id="10" data-service-id="1" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-pink">
      <div class="plan-badge">Mas vendido</div>
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 9</span>
      </div>
      <h3>Enterprise</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="enterprise" data-plan-id="9" data-service-id="1" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-salmon">
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 7</span>
      </div>
      <h3>PRO</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="pro" data-plan-id="7" data-service-id="1" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-blue">
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 6</span>
      </div>
      <h3>FREE</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="free" data-plan-id="6" data-service-id="1" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-indigo">
      <div class="plan-header">
        <span class="plan-service">Invoice stamping</span>
        <span class="plan-id">ID 9</span>
      </div>
      <h3>Enterprise</h3>
      <div class="plan-type">Tipo de servicio: API</div>
      <a class="plan-action" href="#" data-plan-code="enterprise_api" data-plan-id="9" data-service-id="2" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-teal">
      <div class="plan-header">
        <span class="plan-service">Invoice stamping</span>
        <span class="plan-id">ID 7</span>
      </div>
      <h3>PRO</h3>
      <div class="plan-type">Tipo de servicio: API</div>
      <a class="plan-action" href="#" data-plan-code="pro_api" data-plan-id="7" data-service-id="2" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-orange">
      <div class="plan-header">
        <span class="plan-service">Invoice stamping</span>
        <span class="plan-id">ID 6</span>
      </div>
      <h3>FREE</h3>
      <div class="plan-type">Tipo de servicio: API</div>
      <a class="plan-action" href="#" data-plan-code="free_api" data-plan-id="6" data-service-id="2" data-user-id="0">Comprar</a>
    </div>
  </div>
</section>

<div id="checkout-email-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,.55); z-index:9999; align-items:center; justify-content:center; padding:16px;">
  <div role="dialog" aria-modal="true" aria-labelledby="checkout-email-title" style="width:100%; max-width:460px; background:#fff; border-radius:12px; box-shadow:0 20px 40px rgba(0,0,0,.25); overflow:hidden;">
    <div style="padding:16px 18px; border-bottom:1px solid #ececec;">
      <h3 id="checkout-email-title" style="margin:0; font-size:1.2rem;">Ingresa tu correo</h3>
      <p style="margin:8px 0 0; color:#555;">Lo usaremos para asociar tu compra y enviarte acceso.</p>
    </div>
    <div style="padding:16px 18px;">
      <label for="checkout-email-input" style="display:block; margin-bottom:8px;">Correo electronico</label>
      <input id="checkout-email-input" type="email" placeholder="tu-correo@dominio.com" style="width:100%; box-sizing:border-box; border:1px solid #cfcfcf; border-radius:8px; padding:10px 12px; font-size:1rem;">
      <p id="checkout-email-error" style="display:none; color:#b42318; margin:8px 0 0; font-size:.92rem;">Ingresa un correo valido.</p>
    </div>
    <div style="padding:12px 18px 16px; display:flex; gap:10px; justify-content:flex-end; border-top:1px solid #ececec;">
      <button id="checkout-email-cancel" type="button" style="border:1px solid #d0d5dd; background:#fff; color:#222; border-radius:8px; padding:8px 12px; cursor:pointer;">Cancelar</button>
      <button id="checkout-email-submit" type="button" style="border:none; background:#0d6efd; color:#fff; border-radius:8px; padding:8px 12px; cursor:pointer;">Continuar</button>
    </div>
  </div>
</div>

<script>
(function () {
  var section = document.querySelector(".services-plans");
  if (!section) return;

  var checkoutStart = section.getAttribute("data-checkout-start") || "http://127.0.0.1:8000/checkout/start";
  var modal = document.getElementById("checkout-email-modal");
  var emailInput = document.getElementById("checkout-email-input");
  var emailError = document.getElementById("checkout-email-error");
  var cancelBtn = document.getElementById("checkout-email-cancel");
  var submitBtn = document.getElementById("checkout-email-submit");
  var pendingUrl = null;
  var activeButton = null;

  function resetButtonState() {
    if (!activeButton) return;
    var originalText = activeButton.getAttribute("data-original-text") || "Comprar";
    activeButton.textContent = originalText;
    activeButton.removeAttribute("aria-busy");
    activeButton = null;
  }

  function closeModal() {
    modal.style.display = "none";
    emailError.style.display = "none";
    emailInput.value = "";
    pendingUrl = null;
    resetButtonState();
  }

  function openModal(url, button) {
    pendingUrl = url;
    activeButton = button;
    modal.style.display = "flex";
    emailInput.focus();
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  var buttons = section.querySelectorAll(".plan-action");
  buttons.forEach(function (button) {
    button.setAttribute("data-original-text", button.textContent);
    button.addEventListener("click", function (event) {
      event.preventDefault();

      var planCode = button.getAttribute("data-plan-code");
      var planId = button.getAttribute("data-plan-id");
      var serviceId = button.getAttribute("data-service-id");
      if (!planCode && !planId) return;

      button.textContent = "Procesando...";
      button.setAttribute("aria-busy", "true");

      var url = new URL(checkoutStart, window.location.origin);
      if (planCode) {
        url.searchParams.set("plan", planCode);
      }
      if (planId) {
        url.searchParams.set("plan_id", planId);
      }
      if (serviceId) {
        url.searchParams.set("service_id", serviceId);
      }
      // Fuerza flujo invitado: si el correo no existe, Django muestra registro.
      url.searchParams.set("mode", "guest");

      openModal(url, button);
    });
  });

  cancelBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", function (event) {
    if (event.target === modal) closeModal();
  });

  submitBtn.addEventListener("click", function () {
    if (!pendingUrl) return;
    var email = (emailInput.value || "").trim();
    if (!isValidEmail(email)) {
      emailError.style.display = "block";
      return;
    }
    emailError.style.display = "none";
    pendingUrl.searchParams.set("email", email);
    window.location.href = pendingUrl.toString();
  });

  emailInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      submitBtn.click();
    }
    if (event.key === "Escape") {
      closeModal();
    }
  });
})();
</script>

## Comienza en minutos
1. Crea tu cuenta y sube tus XML.
2. Revisa ingresos, egresos y polizas desde un solo lugar.
3. Exporta reportes listos para tu contador.

### Necesitas ayuda?
Escribenos a contacto@factupid.com y te acompanamos en la implementacion.

