// ===== Manejo y Validación Segura del Formulario de Contacto =====
document.addEventListener("DOMContentLoaded", () => {
    const formularioContacto = document.getElementById("contactoForm");

    // Si el formulario no está en la página actual, salir de forma segura
    if (!formularioContacto) return;

    const nombreContacto = document.getElementById("nombre");
    const correoContacto = document.getElementById("correo");
    const asuntoContacto = document.getElementById("asunto");
    const mensajeContacto = document.getElementById("mensaje");

    // Validaciones
    function validarNombreContacto() {
        if (!nombreContacto) return false;
        const valor = nombreContacto.value.trim();
        const patron = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,}$/;

        if (!patron.test(valor)) {
            nombreContacto.classList.add("is-invalid");
            nombreContacto.classList.remove("is-valid");
            return false;
        } else {
            nombreContacto.classList.add("is-valid");
            nombreContacto.classList.remove("is-invalid");
            return true;
        }
    }

    function validarCorreoContacto() {
        if (!correoContacto) return false;
        const valor = correoContacto.value.trim();
        const patron = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!patron.test(valor)) {
            correoContacto.classList.add("is-invalid");
            correoContacto.classList.remove("is-valid");
            return false;
        } else {
            correoContacto.classList.add("is-valid");
            correoContacto.classList.remove("is-invalid");
            return true;
        }
    }

    function validarAsuntoContacto() {
        if (!asuntoContacto) return false;
        const valor = asuntoContacto.value.trim();

        if (valor.length < 5) {
            asuntoContacto.classList.add("is-invalid");
            asuntoContacto.classList.remove("is-valid");
            return false;
        } else {
            asuntoContacto.classList.add("is-valid");
            asuntoContacto.classList.remove("is-invalid");
            return true;
        }
    }

    function validarMensajeContacto() {
        if (!mensajeContacto) return false;
        const valor = mensajeContacto.value.trim();

        if (valor.length < 10) {
            mensajeContacto.classList.add("is-invalid");
            mensajeContacto.classList.remove("is-valid");
            return false;
        } else {
            mensajeContacto.classList.add("is-valid");
            mensajeContacto.classList.remove("is-invalid");
            return true;
        }
    }

    // Eventos dinámicos en tiempo real
    [nombreContacto, correoContacto, asuntoContacto, mensajeContacto].forEach(campo => {
        if (!campo) return;
        campo.addEventListener("input", () => {
            if (campo === nombreContacto) validarNombreContacto();
            if (campo === correoContacto) validarCorreoContacto();
            if (campo === asuntoContacto) validarAsuntoContacto();
            if (campo === mensajeContacto) validarMensajeContacto();
        });
        campo.addEventListener("blur", () => {
            if (campo === nombreContacto) validarNombreContacto();
            if (campo === correoContacto) validarCorreoContacto();
            if (campo === asuntoContacto) validarAsuntoContacto();
            if (campo === mensajeContacto) validarMensajeContacto();
        });
    });

    // Envío del formulario
    formularioContacto.addEventListener("submit", function (e) {
        e.preventDefault();

        const nombreOk = validarNombreContacto();
        const correoOk = validarCorreoContacto();
        const asuntoOk = validarAsuntoContacto();
        const mensajeOk = validarMensajeContacto();

        if (!nombreOk || !correoOk || !asuntoOk || !mensajeOk) {
            const modalEl = document.getElementById("statusErrorsModal");
            if (modalEl && typeof bootstrap !== "undefined") {
                const modalError = bootstrap.Modal.getOrCreateInstance(modalEl);
                modalError.show();
            }
            return;
        }

        const modalExitoEl = document.getElementById("statusSuccessModal");
        if (modalExitoEl && typeof bootstrap !== "undefined") {
            const modalExito = bootstrap.Modal.getOrCreateInstance(modalExitoEl);
            modalExito.show();
        }

        // Limpiar formulario y estados visuales
        formularioContacto.reset();
        [nombreContacto, correoContacto, asuntoContacto, mensajeContacto].forEach(campo => {
            if (campo) campo.classList.remove("is-valid", "is-invalid");
        });
    });
});
