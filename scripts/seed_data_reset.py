from __future__ import annotations

import os
import sys
import argparse
import time # Importar para medir el tiempo de ejecución


def setup_django():
    """Inicializa el entorno de Django."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development"),
    )

    try:
        import django
        django.setup()
    except Exception as exc:
        print("!!! Error al inicializar Django:", exc)
        sys.exit(1)


def delete_all_data(dry_run: bool = False) -> int:
    """Elimina todos los objetos de todos los modelos manejados por Django (método 'delete')."""
    from django.apps import apps
    from django.db import transaction

    # Solo modelos que no son de Django ni de apps de terceros que no son 'managed'
    # Excluimos explícitamente auth, contenttypes, sessions, etc.
    EXCLUDE_APPS = ["admin", "auth", "contenttypes", "sessions", "messages", "staticfiles"]
    
    # Solo consideramos modelos 'managed' (True)
    models = [
        m for m in apps.get_models() 
        if getattr(m._meta, "managed", True) and m._meta.app_label not in EXCLUDE_APPS
    ]

    if not models:
        print("No se encontraron modelos de aplicación local para el borrado por objeto.")
        return 0

    # Ordenar modelos por dependencia inversa para evitar errores de Foreign Key
    # Esto es complejo de hacer en tiempo de ejecución, por lo que lo haremos en dos pasos:
    # 1. Intentar eliminar todo.
    # 2. Si falla, listar y borrar, y notificar qué apps no se borraron.
    
    total = 0
    start_time = time.time()
    
    if not dry_run:
        print("!!! Nota: El borrado por objeto puede ser más lento que 'flush'.")
        print("Iniciando transacción de borrado por objeto (delete_all_data)...")
    
    # Usaremos el borrado por objeto (delete) en un bucle para evitar fallas
    # de claves foráneas masivas, aunque el rendimiento es menor.
    
    # Ordenar de forma inversa para intentar borrar los modelos 'hijos' primero
    models.sort(key=lambda m: m._meta.app_label, reverse=True) 

    with transaction.atomic():
        for model in models:
            app_label = model._meta.app_label
            model_name = model.__name__
            qs = model.objects.all()
            
            try:
                count = qs.count()
            except Exception:
                # Fallo si la tabla no existe o hay problemas de DB. Se ignora este modelo.
                print(f"Advertencia: No se pudo contar objetos para {app_label}.{model_name}. Ignorando.")
                continue

            if count:
                total += count
                print(f" -> {app_label}.{model_name}: {count} objetos")
                if not dry_run:
                    try:
                        qs.delete()
                    except Exception as e:
                        print(f"!!! Error al borrar {app_label}.{model_name}: {e}. (La limpieza continuará)")
                        # No lanzamos excepción para que continúe con el resto de modelos

    if dry_run:
        print(f"\nDry run: Total de objetos que se eliminarían (excluyendo modelos de Django): {total}")
    else:
        end_time = time.time()
        print(f"\n✅ Éxito: Borrado por objeto completado. Total de objetos (estimado) borrados: {total}")
        print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos.")
        
    return total


def reset_database_flush() -> bool:
    """Intenta ejecutar el comando 'flush' de Django."""
    from django.core import management
    
    print("\n" + "="*50)
    print(" PASO 1: Intentando ejecutar 'flush' (rápido y recomendado) ")
    print("="*50)

    try:
        # interactive=False para no pedir confirmación; verbosity=0 para menos ruido
        management.call_command("flush", interactive=False, verbosity=0)
        print("✅ Éxito: El comando 'flush' se ejecutó correctamente.")
        return True
    except Exception as exc:
        print("\n" + "!"*50)
        print("!!! FALLO al ejecutar 'flush'.")
        print(f"!!! Razón: {exc}")
        print("!!! La base de datos no fue vaciada por completo.")
        print("!"*50 + "\n")
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reset total de datos de la base de datos (borra todos los objetos).",
        epilog="Si 'flush' falla, el script intentará un borrado objeto-por-objeto como alternativa.",
    )
    parser.add_argument("-y", "--yes", action="store_true", help="No pedir confirmación interactiva")
    parser.add_argument("--dry-run", action="store_true", help="Listar qué objetos serían eliminados sin borrarlos")
    args = parser.parse_args(argv)

    # Inicializar Django
    setup_django()

    if not args.yes:
        print("ATENCIÓN: Este script borrará datos de la base de datos de forma irreversible.")
        confirm = input("Escribe 'yes' para confirmar: ")
        if confirm.strip().lower() != "yes":
            print("Operación cancelada.")
            return 0
    
    if args.dry_run:
        # Si es dry-run, solo ejecuta el método 'delete' para listar
        print("\n" + "="*50)
        print(" Ejecutando Dry Run: Listando objetos a eliminar (sin tocar la DB) ")
        print("="*50)
        delete_all_data(dry_run=True)
        return 0

    # 1. Intentar el método 'flush' (rápido y completo)
    flush_success = reset_database_flush()
    
    # 2. Si flush falla, usar el método 'delete' como respaldo
    if not flush_success:
        print("\n" + "="*50)
        print(" PASO 2: Intentando método de Respaldo (Borrado objeto por objeto) ")
        print("="*50)
        delete_all_data(dry_run=False)
    
    print("\nReset de base de datos finalizado.")
    
    if flush_success:
        print("La base de datos se restableció completamente con 'flush'.")
    elif not flush_success and delete_all_data(dry_run=True) > 0:
        print("Advertencia: El método 'flush' falló. Se usó el borrado por objeto, que no toca la tabla 'django_migrations'.")
        print("Si tienes problemas con migraciones, considera investigar por qué falló el 'flush' inicial.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())