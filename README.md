# Devir Bordado

[![Deploy](https://github.com/devirbordado/devir-bordado.github.io/actions/workflows/hugo.yaml/badge.svg)](https://github.com/devirbordado/devir-bordado.github.io/actions)
[![Site](https://img.shields.io/badge/site-devirbordado.space-951822)](https://devirbordado.space)
[![Hugo](https://img.shields.io/badge/Hugo-0.168%20Extended-74415B)](https://gohugo.io)
[![Idiomas](https://img.shields.io/badge/idiomas-PT--BR%20%7C%20EN--US-556A82)](#)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-35322F)](LICENSE)
[![Conteúdos: CC BY-NC 4.0](https://img.shields.io/badge/conte%C3%BAdos-CC%20BY--NC%204.0-996515)](LICENSE-ASSETS.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23460361.svg)](https://doi.org/10.5281/zenodo.23460361)

**Experimento 01 · Sistema Devir Bordado**

A creative research project dedicated to exploring embroidery as a practice of memory, knowledge and transformation.
*Um projeto de pesquisa criativa dedicado a explorar o bordado como prática de memória, conhecimento e transformação.*

---

## Project Information / Informações do Projeto

**Author / Autoria:** Iara Lima
**Started / Data de início:** 16 July 2026 (16 de julho de 2026)
**Status / Estado:** Version 1.0 · Online / Versão 1.0 · No ar
**Website / Site:** [devirbordado.space](https://devirbordado.space)
**Repository / Repositório:** Public / Público
**License / Licença:** MIT (code / código) · CC BY-NC 4.0 (content / conteúdos)

---

## Vision / Visão

Devir Bordado is an independent, author-led laboratory that investigates embroidery as a form of artistic expression, research and knowledge production. The website brings together essays, a textile herbarium, collections, publications, playlists and, in the future, downloadable tutorials, connecting textile work with memory, symbolism, nature and human experience. This repository holds the complete source code and content of that website.

*O Devir Bordado é um laboratório autoral e independente que investiga o bordado como forma de expressão artística, pesquisa e produção de conhecimento. O site reúne ensaios, um herbário têxtil, coleções, publicações, playlists e, no futuro, tutoriais para baixar, conectando o fazer têxtil com memória, simbolismo, natureza e experiência humana. Este repositório guarda todo o código-fonte e o conteúdo desse site.*

---

## About the name / Sobre o nome

The name **Devir Bordado** combines two concepts related to transformation and textile practice. **Devir** is the Portuguese word for "becoming", the philosophical concept of processes of change, movement and continuous transformation. **Bordado** means "embroidery", a practice based on threads, gestures and time, which connects the project to textile traditions, craftsmanship and the preservation of stories through material practices. Together, the name expresses embroidery as a process of becoming, where threads, memories and meanings are continuously woven.

*O nome **Devir Bordado** combina dois conceitos ligados à transformação e à prática têxtil. **Devir** vem do conceito filosófico do vir a ser, e se refere a processos de mudança, movimento e transformação contínua. **Bordado** remete à prática tradicional do bordar, baseada em fios, gestos e tempo, que liga o projeto às tradições têxteis, ao trabalho manual e à preservação de histórias por meio de práticas materiais. Juntos, os termos expressam o bordado como um processo de devir, em que fios, memórias e sentidos são tecidos continuamente.*

---

## How the system works / Como o sistema funciona

| Layer / Camada | Tool / Ferramenta | Role / Função |
|---|---|---|
| Source / Fonte | **GitHub** | stores code, texts and images, with version history / guarda código, textos e imagens, com histórico de versões |
| Generator / Gerador | **Hugo** 0.168 Extended | turns Markdown texts and templates into static pages / transforma textos em Markdown e modelos em páginas estáticas |
| Publishing / Publicação | **GitHub Pages** + GitHub Actions | builds on every change and daily at 03:00 (Brasília) / compila a cada alteração e todos os dias às 03:00 (Brasília) |
| Domain / Domínio | **Hostinger** | domain, DNS and institutional email / domínio, DNS e e-mail institucional |
| Functions / Funções (*in activation / em ativação*) | **Cloudflare** | anti-bot check (Turnstile), comments and download files / verificação anti-robô (Turnstile), comentários e arquivos para download |
| Newsletter (*in activation / em ativação*) | **Brevo** | sign-up, confirmation and sending / cadastro, confirmação e envio |
| Archive / Arquivo | **Zenodo** | archived versions with DOI / versões arquivadas com DOI |

---

## Resources / Recursos

| Resource / Recurso | Link |
|---|---|
| Website / Site | [devirbordado.space](https://devirbordado.space) |
| Repository / Repositório | [github.com/devirbordado/devir-bordado.github.io](https://github.com/devirbordado/devir-bordado.github.io) |
| Citable DOI, institutional document / DOI citável, documento institucional | [10.5281/zenodo.23460361](https://doi.org/10.5281/zenodo.23460361) · [Zenodo record](https://zenodo.org/records/23460361) |
| Citable DOI, whole repository / DOI citável, repositório completo | *forthcoming, with release v1.0.0 / em breve, com a versão v1.0.0* |
| How to cite / Como citar | [`CITATION.cff`](CITATION.cff) (GitHub shows "Cite this repository" / o GitHub mostra "Cite this repository") |
| Contact / Contato | contato@devirbordado.space |

The institutional document ***Arquitetura Institucional: fundação, identidade, pesquisa, editorial e governança*** (Iara Lima, version 1.0, in Portuguese and English) is the founding document of the laboratory and the reference for the decisions implemented in this site. It is also listed in the Publications section of the website.

*O documento institucional **Arquitetura Institucional: fundação, identidade, pesquisa, editorial e governança** (Iara Lima, versão 1.0, em português e inglês) é o documento fundador do laboratório e a referência das decisões implementadas neste site. Ele também consta na seção Publicações do site.*

---

## Technical Stack / Tecnologias

- **Generator / Gerador:** Hugo Extended (Go templates, shortcodes, render hooks)
- **Languages / Idiomas:** Portuguese (PT-BR) and English (EN-US), paired by `translationKey` / pareados por `translationKey`
- **Design:** Fraunces font (self-hosted), custom SVG logo and icons / fonte Fraunces (hospedada no site), logotipo e ícones em SVG
- **Images / Imagens:** WebP
- **Data / Dados:** JSON files in `data/` (menu, footer, social links, cookie notice, authorship)
- **Search / Busca:** client-side, no data sent to servers / no navegador, sem envio de dados a servidores
- **Statistics / Estatísticas:** Google Analytics 4, statistics only, loaded only after consent / somente estatísticas, carregado só depois do consentimento
- **Embedded media / Mídia incorporada:** YouTube (privacy-enhanced mode) and Spotify, loaded only after a click / carregados só depois de um clique

---

## Folder structure / Estrutura das pastas

| Folder or file / Pasta ou arquivo | What it holds / O que contém |
|---|---|
| `content/pt-br/`, `content/en-us/` | all texts, one file per language: blog, herbarium, collection, publications, institutional and legal pages / todos os textos, um arquivo por idioma: blog, herbário, acervo, publicações, páginas institucionais e legais |
| `content/*/blog/` | Markdown posts (`index.md`) / posts em Markdown (`index.md`) |
| `layouts/` | page templates and reusable components (`partials`, `shortcodes`) / modelos de página e componentes reutilizáveis (`partials`, `shortcodes`) |
| `data/` | editable site data / dados editáveis do site |
| `i18n/` | interface strings in each language / textos de interface em cada idioma |
| `static/css`, `static/js` | styles and scripts / estilos e scripts |
| `static/assets/fonts` | Fraunces typeface (SIL OFL) / tipografia Fraunces (SIL OFL) |
| `static/assets/images` | WebP images by section / imagens WebP por seção |
| `tools/` | Python scripts used to migrate and format the older texts / scripts em Python usados para migrar e formatar os textos antigos |
| `.github/workflows/` | publishing automation / automação de publicação |
| `LICENSE`, `LICENSE-ASSETS.md`, `CITATION.cff` | licenses and how to cite / licenças e forma de citar |

---

## Run from source / Rodar no seu computador

1. Install Hugo Extended (Windows: `winget install Hugo.Hugo.Extended`). / *Instale o Hugo Extended (Windows: `winget install Hugo.Hugo.Extended`).*
2. Clone the repository and run `hugo server` inside the folder. / *Clone o repositório e execute `hugo server` dentro da pasta.*
3. Open the address shown in the terminal, usually `http://localhost:1313/`. / *Abra o endereço mostrado no terminal, normalmente `http://localhost:1313/`.*

Texts with a future date only appear on their scheduled day; to preview them, use `hugo server -F`.
*Textos com data futura só aparecem no dia marcado; para vê-los antes, use `hugo server -F`.*

---

## Privacy / Privacidade

By default the site uses no advertising or trackers. Analytics loads only if the visitor allows it, and YouTube and Spotify load only after a click. See the [Privacy policy](https://devirbordado.space/en-us/privacy-policy/) and the [Cookie policy](https://devirbordado.space/en-us/cookie-policy/).

*Por padrão, o site não usa publicidade nem rastreadores. As estatísticas só carregam se a pessoa permitir, e YouTube e Spotify só carregam depois de um clique. Veja a [Política de privacidade](https://devirbordado.space/pt-br/politica-de-privacidade/) e a [Política de cookies](https://devirbordado.space/pt-br/politica-de-cookies/).*

---

## Licenses / Licenças

- **Code / Código:** [MIT](LICENSE).
- **Texts, photographs and PDFs / Textos, fotografias e PDFs:** [CC BY-NC 4.0](LICENSE-ASSETS.md). Share and adapt with credit and without commercial purposes. / *Compartilhe e adapte com crédito e sem fins comerciais.*
- **Publications / Publicações:** each record states its own license: articles and preprints CC BY, institutional documents CC BY-NC-ND. / *cada ficha indica a sua licença: artigos e preprints CC BY, documentos institucionais CC BY-NC-ND.*
- **Visual identity / Identidade visual:** the Devir Bordado name, logo, symbol and brand: all rights reserved. / *nome, logotipo, símbolo e marca Devir Bordado: todos os direitos reservados.*
- **Fraunces typeface / Fonte Fraunces:** SIL Open Font License 1.1 (`static/assets/fonts/OFL.txt`).

---

## Contributing / Como contribuir

The content has a single author, so the repository does not accept text contributions. Fixes to code, accessibility or errors you find are welcome: open an issue or write to contato@devirbordado.space.

*O conteúdo tem autoria única, então o repositório não recebe contribuições de texto. Correções de código, acessibilidade ou erros encontrados são bem-vindas: abra uma issue ou escreva para contato@devirbordado.space.*

---

## References / Referências

References will be added as the project evolves.
*As referências serão adicionadas à medida que o projeto evoluir.*

---

## Notes / Notas

This repository also serves as a research notebook. Ideas, concepts, visual decisions and editorial structures may evolve throughout the project's development.
*Este repositório também serve como um caderno de pesquisa. Ideias, conceitos, decisões visuais e estruturas editoriais podem evoluir ao longo do desenvolvimento do projeto.*

---

Created by Iara Lima. / Criado por Iara Lima.
