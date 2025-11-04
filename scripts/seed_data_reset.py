from __future__ import annotations

import os
import sys
import argparse


def setup_django():
    # Añadir el directorio raíz del proyecto al sys.path para que se pueda
    # importar el paquete `config` cuando el script se ejecute desde
    # `scripts/` (por ejemplo: python scripts\seed_data_reset.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Use DJANGO_SETTINGS_MODULE si está presente, sino usar desarrollo por defecto
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development"),
    )

    try:
        import django

        django.setup()
    except Exception as exc:  # pragma: no cover - environment dependent
        print("Error al inicializar Django:", exc)
        sys.exit(1)


def delete_all_data(dry_run: bool = False) -> None:
    """Elimina todos los objetos de todos los modelos manejados por Django.

    dry_run=True solo lista cuántos objetos habría que borrar por modelo.
    """
    from django.apps import apps
    from django.db import transaction

    models = [m for m in apps.get_models() if getattr(m._meta, "managed", True)]

    if not models:
        print("No se encontraron modelos manejados.")
        return

    total = 0
    with transaction.atomic():
        for model in models:
            app_label = model._meta.app_label
            model_name = model.__name__
            qs = model.objects.all()
            try:
                count = qs.count()
            except Exception:
                # Algunos modelos o backends pueden fallar en count; fall back a len(list())
                count = len(list(qs))

            if count:
                total += count
                print(f"{app_label}.{model_name}: {count} objetos")
                if not dry_run:
                    qs.delete()

    if dry_run:
        print(f"Total objetos que se eliminarían: {total}")
    else:
        print(f"Eliminación completada. Total eliminado (estimado): {total}")


def reset_database(method: str = "flush", dry_run: bool = False) -> None:
    """Resetea la base de datos actual.

    method: 'flush' usa el management command 'flush' de Django (recomendado).
            'delete' recorre los modelos y borra objetos (función delete_all_data).
    dry_run: si True no borra, solo muestra qué haría.
    """
    if method not in {"flush", "delete"}:
        raise ValueError("method debe ser 'flush' o 'delete'")

    if method == "delete":
        print("Usando método 'delete' — borrando objetos por modelo...")
        delete_all_data(dry_run=dry_run)
        return

    # Método flush
    from django.core import management

    if dry_run:
        print("Dry run: se ejecutaría 'flush' para eliminar todos los datos de la base de datos.")
        return

    print("Ejecutando 'flush' — esto eliminará todos los datos de la base de datos actual...")
    try:
        # interactive=False para no pedir confirmación; ya controlamos con --yes
        management.call_command("flush", interactive=False, verbosity=1)
    except Exception as exc:  # pragma: no cover - depende del entorno
        print("Error al ejecutar 'flush':", exc)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reset total de datos de la base de datos (borra todos los objetos de todos los modelos)."
    )
    parser.add_argument("-y", "--yes", action="store_true", help="No pedir confirmación interactiva")
    parser.add_argument("--dry-run", action="store_true", help="Listar cuántos objetos serían eliminados sin borrarlos")
    parser.add_argument(
        "--method",
        choices=["flush", "delete"],
        default="flush",
        help="Método para resetear la base: 'flush' (por defecto) o 'delete' por modelo",
    )
    args = parser.parse_args(argv)

    # Inicializar Django
    setup_django()

    if not args.yes:
        print("ATENCIÓN: Este script borrará datos de la base de datos de forma irreversible.")
        confirm = input("Escribe 'yes' para confirmar: ")
        if confirm.strip().lower() != "yes":
            print("Operación cancelada.")
            return 0

    try:
        reset_database(method=args.method, dry_run=args.dry_run)
        print("Reset de base de datos completado.")
    except Exception as exc:  # pragma: no cover - depende del entorno y modelos
        print("Error durante la eliminación:", exc)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
