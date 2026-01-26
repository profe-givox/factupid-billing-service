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
      <a class="plan-action" href="#" data-plan-code="ondemand" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-pink">
      <div class="plan-badge">Mas vendido</div>
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 9</span>
      </div>
      <h3>Enterprise</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="enterprise" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-salmon">
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 7</span>
      </div>
      <h3>PRO</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="pro" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-blue">
      <div class="plan-header">
        <span class="plan-service">CFDI</span>
        <span class="plan-id">ID 6</span>
      </div>
      <h3>FREE</h3>
      <div class="plan-type">Tipo de servicio: App</div>
      <a class="plan-action" href="#" data-plan-code="free" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-indigo">
      <div class="plan-header">
        <span class="plan-service">Invoice stamping</span>
        <span class="plan-id">ID 9</span>
      </div>
      <h3>Enterprise</h3>
      <div class="plan-type">Tipo de servicio: API</div>
      <a class="plan-action" href="#" data-plan-code="enterprise_api" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-teal">
      <div class="plan-header">
        <span class="plan-service">Invoice stamping</span>
        <span class="plan-id">ID 7</span>
      </div>
      <h3>PRO</h3>
      <div class="plan-type">Tipo de servicio: API</div>
      <a class="plan-action" href="#" data-plan-code="pro_api" data-user-id="0">Comprar</a>
    </div>
    <div class="plan-card plan-orange">
      <div class="plan-header">
        <span class="plan-service">Invoice stamping</span>
        <span class="plan-id">ID 6</span>
      </div>
      <h3>FREE</h3>
      <div class="plan-type">Tipo de servicio: API</div>
      <a class="plan-action" href="#" data-plan-code="free_api" data-user-id="0">Comprar</a>
    </div>
  </div>
</section>

  <script>
  (function () {
    var section = document.querySelector(".services-plans");
    if (!section) return;

    // URL base del endpoint Django que inicia el checkout
    var checkoutStart = section.getAttribute("data-checkout-start") || "http://127.0.0.1:8000/checkout/start";

    var buttons = section.querySelectorAll(".plan-action[data-plan-code]");
    buttons.forEach(function (button) {
      button.addEventListener("click", function (event) {
        event.preventDefault();

        var planCode = button.getAttribute("data-plan-code");
        if (!planCode) return;

        var originalText = button.textContent;
        button.textContent = "Procesando...";
        button.setAttribute("aria-busy", "true");

        // Construye la URL con el plan
        var url = new URL(checkoutStart, window.location.origin);
        url.searchParams.set("plan", planCode);

        // Solicita correo para asociar el pago al usuario invitado
        var email = window.prompt("Ingresa tu correo para recibir el acceso:", "");
        if (email && email.trim()) {
          url.searchParams.set("email", email.trim());
        }

        // Redirige a Django para crear la sesión de Stripe
        window.location.href = url.toString();

        button.textContent = originalText;
        button.removeAttribute("aria-busy");
      });
    });
  })();
</script>

## Comienza en minutos
1. Crea tu cuenta y sube tus XML.
2. Revisa ingresos, egresos y polizas desde un solo lugar.
3. Exporta reportes listos para tu contador.

### Necesitas ayuda?
Escribenos a contacto@factupid.com y te acompanamos en la implementacion.
