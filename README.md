# reVCDOS — GitHub Pages adapter

Este pacote adapta o projeto público `Lolendor/reVCDOS` para publicação pelo GitHub Pages.

O repositório original usa um servidor Python/PHP para duas funções que o GitHub Pages não oferece: proxy de `/vcsky/` e `/vcbr/`, e os headers `Cross-Origin-Opener-Policy` / `Cross-Origin-Embedder-Policy`.

Este adaptador resolve a parte estática assim:

- o GitHub Actions clona automaticamente o `Lolendor/reVCDOS` original;
- copia somente `dist/` para o artefato do Pages;
- troca os caminhos `/vcsky/` e `/vcbr/` por URLs configuráveis;
- corrige `/intro.mp4` para funcionar em `usuario.github.io/repositorio/`;
- adiciona um Service Worker para fornecer COOP/COEP na página controlada;
- publica automaticamente com o workflow oficial do GitHub Pages.

## Como usar

1. Crie um repositório vazio no GitHub.
2. Extraia este ZIP e envie **todo o conteúdo desta pasta** para a raiz do repositório.
3. Garanta que a branch principal se chama `main` ou `master`.
4. No GitHub abra **Settings → Pages**.
5. Em **Build and deployment → Source**, escolha **GitHub Actions**.
6. Vá em **Actions** e execute `Deploy reVCDOS to GitHub Pages` caso o primeiro push não tenha iniciado automaticamente.
7. Quando terminar, o endereço aparecerá no job `deploy`, normalmente `https://SEU-USUARIO.github.io/NOME-DO-REPO/`.

## CDN / CORS

Por padrão, `pages-config.js` aponta para:

```js
vcskyBaseUrl: "https://cdn.dos.zone/vcsky/"
vcbrBaseUrl: "https://br.cdn.dos.zone/vcsky/"
```

Se esses CDNs aceitarem requisições CORS diretamente do domínio do seu GitHub Pages, não é necessário configurar mais nada.

Se o navegador mostrar erro de CORS/CORP ao carregar `sha256sums.txt`, `.data.br`, `.wasm.br` ou outros assets, use o Worker opcional incluído em `cloudflare-worker/`. Depois altere `pages-config.js` para:

```js
window.REVCDOS_PAGES_CONFIG = Object.freeze({
  vcskyBaseUrl: "https://SEU-WORKER.workers.dev/vcsky/",
  vcbrBaseUrl: "https://SEU-WORKER.workers.dev/vcbr/"
});
```

O Worker apenas encaminha os requests; ele não inclui os arquivos do jogo neste ZIP.

## Atualizações do projeto original

A cada deploy o workflow faz:

```bash
git clone --depth 1 https://github.com/Lolendor/reVCDOS.git upstream
python3 build_pages.py upstream public
```

Assim, o artefato publicado usa a versão mais recente do `dist/` do upstream, desde que o bloco que o patch procura não tenha mudado. Se o upstream alterar essa parte, o build falha de propósito em vez de publicar uma versão quebrada.

## Observações

- GitHub Pages é somente hospedagem estática. `server.py`, PHP, Basic Auth e `--custom_saves` não são executados.
- O modo de save usado no Pages é o cliente normal de cloud saves do projeto.
- O projeto original exige/solicita confirmação de posse dos arquivos originais do jogo; este adaptador não inclui assets proprietários.
- O Service Worker consegue fornecer os headers de isolamento para a página, mas **não contorna CORS** do CDN. Por isso há o Worker opcional.

Projeto original: https://github.com/Lolendor/reVCDOS
