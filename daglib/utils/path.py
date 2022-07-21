from pathlib import Path


def delete_folder(p: Path) -> None:
    for sub in p.iterdir():
        if sub.is_dir():
            delete_folder(sub)
        else:
            sub.unlink()
    p.rmdir()
