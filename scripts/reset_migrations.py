from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import List, Tuple


def find_migration_dirs(base: Path) -> List[Path]:
    """Busca directorios llamados 'migrations' bajo base."""
    result: List[Path] = []
    for root, dirs, files in os.walk(base):
        # Evitar entrar en entornos virtuales u otras carpetas comunes
        parts = Path(root).parts
        if "site-packages" in parts or "venv" in parts or "venvs" in parts:
            continue
        if Path(root).name == "migrations":
            result.append(Path(root))
    return result


def clean_migration_dir(mig_dir: Path, dry_run: bool = False) -> Tuple[int, int]:
    """Elimina archivos de migración dejando __init__.py.

    Devuelve (files_deleted, pyc_deleted)
    """
    files_deleted = 0
    pyc_deleted = 0

    # Asegurar que exista __init__.py (si no existe, lo creamos más abajo)
    init_path = mig_dir / "__init__.py"

    for item in mig_dir.iterdir():
        if item.is_dir():
            # Borrar __pycache__ dentro de migrations
            if item.name == "__pycache__":
                if dry_run:
                    print(f"  (dry) remove dir: {item}")
                else:
                    shutil.rmtree(item, ignore_errors=True)
                continue
        if item.is_file():
            if item.name == "__init__.py":
                continue
            # Borrar cualquier .py, .pyc, .pyo y migraciones en general
            if item.suffix in (".py", ".pyc", ".pyo"):
                if dry_run:
                    print(f"  (dry) remove file: {item}")
                else:
                    try:
                        item.unlink()
                    except Exception as e:
                        print(f"  failed to delete {item}: {e}")
                if item.suffix == ".py":
                    files_deleted += 1
                else:
                    pyc_deleted += 1

    # Asegurar __init__.py existe
    if not init_path.exists():
        if dry_run:
            print(f"  (dry) create file: {init_path}")
        else:
            init_path.write_text("# migrations package\n")

    return files_deleted, pyc_deleted


def confirm(prompt: str) -> bool:
    try:
        return input(prompt).lower().strip() in ("y", "yes", "s", "si")
    except EOFError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Resetear migraciones dejando solo __init__.py")
    parser.add_argument("--yes", action="store_true", help="No pedir confirmación")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar acciones sin ejecutar")
    parser.add_argument("--base", type=str, default=None, help="Directorio base para buscar (por defecto: carpeta padre del script)")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    default_base = script_path.parent.parent  # ss_backend/
    base = Path(args.base).resolve() if args.base else default_base

    # Comprobación sencilla para asegurarnos de correr en el backend
    if not (base / "manage.py").exists():
        print(f"Advertencia: no se encontró 'manage.py' en {base}. ¿Estás seguro de que es la carpeta backend?")
        if not args.yes and not confirm("Continuar igual? [y/N]: "):
            print("Cancelado.")
            return 2

    print(f"Buscando carpetas 'migrations' bajo: {base}")
    mig_dirs = find_migration_dirs(base)

    if not mig_dirs:
        print("No se encontraron directorios de migraciones.")
        return 0

    print("Se encontraron los siguientes directorios de migraciones:")
    for d in mig_dirs:
        print(" -", d)

    if args.dry_run:
        print("\nDry run: no se harán cambios. Mostrando acciones previstas:\n")
    else:
        if not args.yes:
            if not confirm("Proceder a eliminar archivos de migración en las rutas anteriores? [y/N]: "):
                print("Cancelado por el usuario.")
                return 1

    total_py = 0
    total_pyc = 0

    for d in mig_dirs:
        print(f"Procesando: {d}")
        py_deleted, pyc_deleted = clean_migration_dir(d, dry_run=args.dry_run)
        total_py += py_deleted
        total_pyc += pyc_deleted

    print("\nResumen:")
    print(f"  archivos .py eliminados: {total_py}")
    print(f"  archivos .pyc/.pyo eliminados: {total_pyc}")
    print("  se conservaron/crearon los __init__.py en cada carpeta migrations")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
