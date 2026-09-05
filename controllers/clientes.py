from flask import Blueprint, flash, redirect, render_template, request, url_for

from forms.cliente_form import ClienteForm
from models.cliente import Cliente

clientes_bp = Blueprint("clientes", __name__)


@clientes_bp.route("/clientes")
def listar():
    return render_template("clientes.html", clientes=Cliente.listar())


@clientes_bp.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo():
    form = ClienteForm()
    if form.validate_on_submit():
        Cliente.crear(_datos_formulario(form))
        flash("Cliente registrado correctamente.", "success")
        return redirect(url_for("clientes.listar"))
    if request.method == "GET":
        form.canton.data = "Lago Agrio"
    return render_template("formulario_cliente.html", form=form, editando=False)


@clientes_bp.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar(cliente_id):
    cliente = Cliente.obtener(cliente_id)
    if cliente is None:
        flash("El cliente solicitado no existe.", "danger")
        return redirect(url_for("clientes.listar"))
    form = ClienteForm(data=cliente) if request.method == "GET" else ClienteForm()
    if form.validate_on_submit():
        Cliente.actualizar(cliente_id, _datos_formulario(form))
        flash(f'Cliente "{form.nombre.data}" actualizado correctamente.', "success")
        return redirect(url_for("clientes.listar"))
    return render_template("formulario_cliente.html", form=form, editando=True, id=cliente_id)


@clientes_bp.route("/clientes/eliminar/<int:cliente_id>", methods=["POST", "GET"])
def eliminar(cliente_id):
    cliente = Cliente.obtener(cliente_id)
    if cliente is None:
        flash("El cliente solicitado no existe.", "danger")
    else:
        Cliente.eliminar(cliente_id)
        flash(f'Cliente "{cliente["nombre"]}" eliminado correctamente.', "success")
    return redirect(url_for("clientes.listar"))


def _datos_formulario(form):
    return {
        "nombre": form.nombre.data,
        "negocio": form.negocio.data,
        "celular": form.celular.data,
        "provincia": form.provincia.data,
        "canton": form.canton.data,
    }
