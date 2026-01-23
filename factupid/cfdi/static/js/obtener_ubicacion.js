
function obtenerUbicacion(callback) {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude.toFixed(6);
                const lon = position.coords.longitude.toFixed(6);
                document.getElementById("inputLatitud").value = lat;
                document.getElementById("inputLongitud").value = lon;
                if (callback) callback(lat, lon);
            },
            (error) => {
                console.warn("No se pudo obtener ubicación:", error);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    }
}
document.addEventListener("DOMContentLoaded", () => {
    obtenerUbicacion();
});

