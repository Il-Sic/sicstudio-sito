#!/bin/zsh
# Il sito pubblicato su https://sicstudio.app confrontato con questa cartella, solo con curl (richieste GET, nient'altro).
# Per ogni file pubblicato: risposta 200 e contenuto identico byte per byte; le pagine anche al loro indirizzo con la
# barra finale. In git ci sono anche file che online non vanno: GitHub Pages costruisce il sito con Jekyll, che lascia
# fuori ciò che comincia con «_» o con «.» (_lavoro, _config.yml, .github, .gitignore). Ognuno di questi, la cartella
# /_lavoro/, una pagina che non c'è e il foglio di stile del tema di GitHub Pages, che _config.yml toglie, danno 404
# con la pagina «Fuori rotta». Da lanciare dopo che GitHub Pages ha finito (Actions › «pages build and deployment»):
#   zsh _lavoro/controlli/online.sh
SITO=${0:A:h:h:h}
BASE=https://sicstudio.app
TMP=$(mktemp -d)
problemi=0
richieste=0

# prova <indirizzo> <file locale con cui confrontare la risposta> <codice atteso>
prova() {
  local codice tipo
  read -r codice tipo <<< "$(curl -sS -o "$TMP/risposta" -w '%{http_code} %{content_type}' "$BASE$1")"
  (( richieste++ ))
  if [[ $codice != $3 ]]; then
    print -r -- "NO  $1: $codice invece di $3"; (( problemi++ ))
  elif ! cmp -s "$TMP/risposta" "$2"; then
    print -r -- "NO  $1: il contenuto è diverso da ${2#$SITO/}"; (( problemi++ ))
  else
    print -r -- "$3 ${2:e} $tipo" >> "$TMP/tipi"
  fi
}

# CNAME è in git ma non online: GitHub Pages lo usa per il dominio.
for f in ${(f)"$(git -C "$SITO" ls-files)"}; do
  [[ $f == CNAME ]] && continue
  if [[ $f == _* || $f == .* ]]; then
    prova "/$f" "$SITO/404.html" 404
    continue
  fi
  prova "/$f" "$SITO/$f" 200
  [[ $f == index.html || $f == */index.html ]] && prova "/${f%index.html}" "$SITO/$f" 200
done
prova /questa-pagina-non-c-e/ "$SITO/404.html" 404
prova /_lavoro/ "$SITO/404.html" 404
prova /assets/css/style.css "$SITO/404.html" 404

print -r -- "--- la privacy (sha-256), online e in questa cartella:"
curl -sS https://sicstudio.app/argonauta/privacy/ | shasum -a 256 | cut -c1-64
shasum -a 256 "$SITO/argonauta/privacy/index.html" | cut -c1-64
http=$(curl -sS -o /dev/null -w '%{http_code} %{redirect_url}' http://sicstudio.app/)
if [[ $http == 301\ https://* ]]; then
  print -r -- "--- http://sicstudio.app/ porta a https:// («Enforce HTTPS» acceso)"
else
  print -r -- "--- http://sicstudio.app/ risponde ${http% }: «Enforce HTTPS» è ancora spento"
fi
print -r -- "--- codici e tipi delle risposte giuste:"
sort "$TMP/tipi" | uniq -c
print -r -- "--- $richieste richieste, $problemi problemi"
rm -r "$TMP"
