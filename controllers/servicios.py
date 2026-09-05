from flask import Blueprint, flash, redirect, render_template, request, url_for

from forms.servicio_form import ServicioForm
from models.servicio import Servicio

servicios_bp = Blueprint("servicios", __name__)


@servicios_bp.route("/servicios")
@servicios_bp.route("/servicio")
def listar():
    return render_template("servicios.html", servicios=Servicio.listar())


@servicios_bp.route("/servicios/nuevo", methods=["GET", "POST"])
@servicios_bp.route("/servicio/nuevo", methods=["GET", "POST"])
def nuevo():
    form = ServicioForm()
    if form.validate_on_submit():
        imagen = form.imagen.data.strip() if form.imagen.data else ""
        Servicio.crear({
            "nombre": form.nombre.data,
            "descripcion": form.descripcion.data,
            "precio": float(form.precio.data),
            "imagen": imagen or "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
            "estado": form.estado.data,
        })
        flash("Servicio registrado correctamente.", "success")
        return redirect(url_for("servicios.listar"))
    return render_template("formulario_servicio.html", form=form, editando=False)


@servicios_bp.route("/servicios/editar/<int:servicio_id>", methods=["GET", "POST"])
@servicios_bp.route("/servicio/editar/<int:servicio_id>", methods=["GET", "POST"])
def editar(servicio_id):
    servicio = Servicio.obtener(servicio_id)
    if servicio is None:
        flash("El servicio solicitado no existe.", "danger")
        return redirect(url_for("servicios.listar"))
    form = ServicioForm(data=servicio) if request.method == "GET" else ServicioForm()
    if form.validate_on_submit():
        imagen = form.imagen.data.strip() if form.imagen.data else servicio["imagen"]
        Servicio.actualizar(servicio_id, {
            "nombre": form.nombre.data,
            "descripcion": form.descripcion.data,
            "precio": float(form.precio.data),
            "imagen": imagen,
            "estado": form.estado.data,
        })
        flash(f'Servicio "{form.nombre.data}" actualizado correctamente.', "success")
        return redirect(url_for("servicios.listar"))
    return render_template("formulario_servicio.html", form=form, editando=True, id=servicio_id)


@servicios_bp.route("/servicios/eliminar/<int:servicio_id>", methods=["POST", "GET"])
@servicios_bp.route("/servicio/eliminar/<int:servicio_id>", methods=["POST", "GET"])
def eliminar(servicio_id):
    servicio = Servicio.obtener(servicio_id)
    if servicio is None:
        flash("El servicio solicitado no existe.", "danger")
    else:
        Servicio.eliminar(servicio_id)
        flash(f'Servicio "{servicio["nombre"]}" eliminado correctamente.', "success")
    return redirect(url_for("servicios.listar"))

