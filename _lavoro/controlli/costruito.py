"""Il sito costruito da Jekyll, come lo costruisce GitHub Pages, confrontato con i file in git: dentro ci devono essere
tutti e soli i file pubblici, identici byte per byte. Pubblico è ogni file in git che Jekyll non lascia fuori: quelli
il cui percorso non ha pezzi che cominciano con «_» o con «.», tolti quelli della lista exclude di _config.yml.
Così _lavoro, le note in .md e qualunque file aggiunto da GitHub Pages non arrivano online senza che si veda.

Non fa parte di tutti.py, perché serve il sito già costruito. Lo lancia GitHub a ogni pull request
(.github/workflows/controlli.yml), dopo aver costruito il sito in _site:
    python3 -I _lavoro/controlli/costruito.py _site
"""
import fnmatch, pathlib, re, subprocess, sys

SITO = pathlib.Path(__file__).resolve().parents[2]


def esclusi():
    """Le voci di exclude in _config.yml: le righe «  - voce» dopo «exclude:», fino alla prima riga che non lo è."""
    voci, dentro = [], False
    for riga in (SITO / "_config.yml").read_text(encoding="utf-8").splitlines():
        if riga.startswith("exclude:"):
            dentro = True
        elif dentro:
            m = re.match(r"\s+-\s+(.+?)\s*$", riga)
            if not m:
                break
            voci.append(m.group(1).strip("\"'"))
    return voci


def pubblico(f, fuori):
    """Come decide Jekyll: fuori ciò che comincia con «_» o «.» a ogni livello, e ciò che combacia con una voce di
    exclude (il nome com'è, una cartella con ciò che contiene, o un modello con «*»)."""
    if any(pezzo.startswith(("_", ".")) for pezzo in f.split("/")):
        return False
    return not any(f == v or f.startswith(v.rstrip("/") + "/") or fnmatch.fnmatchcase(f, v) for v in fuori)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    costruito = pathlib.Path(sys.argv[1]).resolve()
    if not costruito.is_dir():
        print(f"Sito costruito: {sys.argv[1]} non è una cartella")
        return 2
    fuori = esclusi()
    in_git = subprocess.run(["git", "-C", str(SITO), "ls-files", "-z"], capture_output=True, check=True).stdout
    pubblici = {f for f in in_git.decode("utf-8").split("\0") if f and pubblico(f, fuori)}
    usciti = {p.relative_to(costruito).as_posix() for p in costruito.rglob("*") if p.is_file()}
    problemi = 0
    for f in sorted(usciti - pubblici):
        print(f"IN PIÙ {f}: è nel sito costruito ma non è un file pubblico in git")
        problemi += 1
    for f in sorted(pubblici - usciti):
        print(f"MANCA {f}: è un file pubblico in git ma non è nel sito costruito")
        problemi += 1
    for f in sorted(pubblici & usciti):
        if (costruito / f).read_bytes() != (SITO / f).read_bytes():
            print(f"DIVERSO {f}: nel sito costruito non è uguale al file in git")
            problemi += 1
    print(f"Sito costruito: {len(usciti)} file, {len(pubblici)} pubblici in git, fuori {', '.join(fuori)}; {problemi} problemi")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
