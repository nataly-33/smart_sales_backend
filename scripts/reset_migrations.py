from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# --- Funciones de limpieza de archivos (sin cambios) ---

def find_migration_dirs(base: Path) -> List[Path]:
    """Busca directorios llamados 'migrations' bajo base."""
    result: List[Path] = []
    for item in base.glob('**/migrations/'):
        if "site-packages" in item.parts or "venv" in item.parts or "venvs" in item.parts:
            continue
        result.append(item)
    return result


def clean_migration_dir(mig_dir: Path, dry_run: bool = False) -> Tuple[int, int]:
    """Elimina archivos de migración dejando __init__.py."""
    files_deleted = 0
    pyc_deleted = 0
    init_path = mig_dir / "__init__.py"

    for item in mig_dir.iterdir():
        if item.is_dir():
            if item.name == "__pycache__":
                if dry_run:
                    print(f"  (dry) remove dir: {item.relative_to(mig_dir)}")
                else:
                    shutil.rmtree(item, ignore_errors=True)
                continue
        if item.is_file():
            if item.name == "__init__.py":
                continue
            if item.suffix in (".py", ".pyc", ".pyo"):
                if dry_run:
                    print(f"  (dry) remove file: {item.relative_to(mig_dir)}")
                else:
                    try:
                        item.unlink()
                    except Exception as e:
                        print(f"  failed to delete {item}: {e}")
                if item.suffix == ".py":
                    files_deleted += 1
                else:
                    pyc_deleted += 1
    
    if not init_path.exists():
        if dry_run:
            print(f"  (dry) create file: {init_path.relative_to(mig_dir.parent)}")
        else:
            init_path.write_text("# migrations package\n")
    
    return files_deleted, pyc_deleted

# --- Funciones de utilidad (sin cambios) ---

def confirm(prompt: str) -> bool:
    try:
        return input(prompt).lower().strip() in ("y", "yes", "s", "si")
    except EOFError:
        return False

def run_django_command(command_parts: List[str], check: bool = True) -> bool:
    """Ejecuta un comando de Django usando subprocess."""
    print(f"\n---> Ejecutando: python manage.py {' '.join(command_parts)}")
    cmd = [sys.executable, "manage.py"] + command_parts
    
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8', # For Windows compatibility
            cwd=Path(os.getcwd())
        )
        print(result.stdout)
        if result.stderr:
            print("--- ERROR (STDERR) ---")
            print(result.stderr)
            print("----------------------")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n!!! ERROR al ejecutar el comando: {' '.join(cmd)}")
        print(f"Salida estándar (stdout): {e.stdout}")
        print(f"Salida de error (stderr): {e.stderr}")
        return False
    except FileNotFoundError:
        print("!!! ERROR: No se pudo encontrar 'python' o 'manage.py'.")
        print("Asegúrate de estar en el directorio correcto y el venv está activo.")
        return False

# --- Función Principal (MODIFICADA) ---

def main() -> int:
    parser = argparse.ArgumentParser(description="RESET COMPLETO DE MIGRACIONES Y TABLA django_migrations.")
    parser.add_argument("--yes", action="store_true", help="No pedir confirmación")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar acciones sin ejecutar")
    parser.add_argument("--base", type=str, default="..", help="Directorio base que contiene manage.py (por defecto: ..)")
    args = parser.parse_args()

    base_path = Path(__file__).resolve().parent / args.base
    os.chdir(base_path)
    print(f"Cambiando directorio de trabajo a: {base_path}")

    if not (base_path / "manage.py").exists():
        print(f"!!! ERROR: No se encontró 'manage.py' en {base_path}")
        return 1

    if not args.yes:
        print("\n!!! ADVERTENCIA: Esta acción es IRREVERSIBLE...")
        if not confirm("¿Estás ABSOLUTAMENTE seguro de proceder? [y/N]: "):
            print("Cancelado por el usuario.")
            return 1
    
    mig_dirs = find_migration_dirs(base_path)
    if not mig_dirs:
        print("\nNo se encontraron directorios de migraciones de apps locales.")

    # 1. Limpiar archivos de migración
    print("\n" + "="*50)
    print(" PASO 1: Eliminando archivos de migración del disco")
    print("="*50)
    
    total_py = 0
    total_pyc = 0
    for d in mig_dirs:
        print(f"\nProcesando: {d.relative_to(base_path)}")
        py_deleted, pyc_deleted = clean_migration_dir(d, dry_run=args.dry_run)
        total_py += py_deleted
        total_pyc += pyc_deleted
    
    print("\n--- Resumen de Archivos ---")
    print(f"  archivos .py eliminados: {total_py}")
    print(f"  archivos .pyc/.pyo eliminados: {total_pyc}")
    print("  archivos __init__.py conservados/creados.")

    if args.dry_run:
        print("\nDry run finalizado. No se realizaron cambios.")
        return 0

    # 2. ELIMINADO EL 'PASO 2: migrate ... zero'
    # Era la fuente del error 'Dependency on app with no migrations'

    # 3. Ejecutar FLUSH (Ahora es el PASO 2)
    print("\n" + "="*50)
    print(" PASO 2: Ejecutando FLUSH (Eliminar todos los datos de la DB)")
    print("="*50)
    
    print("Ejecutando FLUSH para una limpieza total de datos...")
    print("Esto eliminará TODOS los datos y limpiará la tabla django_migrations.")
    
    # 'check=True' está bien aquí. Si 'flush' falla, debemos parar.
    if not run_django_command(["flush", "--no-input"]):
        print("\n❌ FALLO CRÍTICO: El comando 'flush' falló.")
        print("   La base de datos NO está limpia. Revisa los permisos de 'sm_admin' en PostgreSQL.")
        return 1
    else:
        print("\n✅ ÉXITO: El comando 'flush' se ejecutó correctamente.")
        print("   La base de datos está completamente limpia.")


    # 4. Crear nuevas migraciones (Ahora es el PASO 3)
    print("\n" + "="*50)
    print(" PASO 3: Creando nuevas migraciones desde cero")
    print("="*50)
    
    print("Esto creará los nuevos archivos '0001_initial.py' para TODAS las apps,")
    print("incluyendo la app 'accounts', lo que corrige el error de dependencia.")
    
    if run_django_command(["makemigrations"]):
        print("\n✅ ÉXITO: Se crearon nuevas migraciones correctamente.")
        print("   Ahora puedes aplicar las migraciones con `python manage.py migrate`.")
    else:
        print("\n❌ FALLO: No se pudieron crear nuevas migraciones. Revisa los mensajes de error.")
        return 1

    print("\n" + "="*50)
    print("✨ RESET COMPLETADO ✨")
    print("="*50)
    print(" Ejecute directo: python manage.py migrate")

    return 0


if __name__ == "__main__":
    sys.exit(main())