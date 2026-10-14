# Utiliser les skills de justice internationale — tutoriel en français

*(This is the French-language quick-start for practitioners. The English
walkthrough is in [`INSTALL.md`](INSTALL.md).)*

Guide pour juristes. Aucune compétence technique requise. Cinq minutes.

## Ce que c'est (et ce que ce n'est pas)

Ce n'est **pas une base de données** : aucun jugement n'est stocké dedans. Ce
sont treize guides de méthode, un par tribunal, de Nuremberg à la JEP
colombienne, qui apprennent à votre assistant IA à chercher dans les bonnes
sources, citer au bon format, et surtout : **ne jamais citer sans avoir
vérifié le document officiel**.

## Un skill et le serveur MCP : quelle différence ?

- **Un skill est un document de méthode.** L'assistant le lit et sait alors
  *comment* travailler : les sources autorisées, les formats de citation, la
  règle de vérification. Pas d'installation : ce sont des fichiers que vous
  déposez dans un projet.
- **Le serveur MCP est un branchement technique.** Il donne à l'assistant des
  outils d'action en plus : chercher dans les treize guides d'un coup,
  analyser une référence, vérifier une citation mot à mot contre le document
  officiel. Il demande une petite installation (voir
  [`mcp/README.md`](mcp/README.md)) et ne fonctionne que sur les assistants
  compatibles MCP, comme Claude.

**Les skills suffisent pour travailler.** Le serveur MCP automatise les
vérifications ; il n'est jamais obligatoire.

## Avec quels assistants IA ?

Les skills sont de simples fichiers texte : ils fonctionnent avec tout
assistant qui accepte des documents et dispose d'une recherche web.

| Assistant | Les skills (fichiers) | Le serveur MCP (outils de vérification) |
|---|---|---|
| **Claude** (claude.ai, Desktop, Code) | Oui — projet ou upload de skills | Oui — voir [`mcp/README.md`](mcp/README.md) |
| **Le Chat** (Mistral) | Oui — projet ou bibliothèque de documents | Non à ce jour |
| **ChatGPT** (OpenAI) | Oui — projet ou fichiers joints | Via les intégrations compatibles |
| Autre assistant acceptant des documents | Oui — même principe | Tout client MCP |

Le serveur MCP est un plus (vérification de citations et de quotes
automatisée) ; la méthode ne dépend pas de lui.

## Étape 1 · Télécharger les guides

Sur cette page GitHub, cliquez le bouton vert **« Code »** puis **« Download
ZIP »**, et décompressez le dossier. Chaque tribunal a son dossier : `icc/`
pour la CPI, `eccc/` pour les CETC, `icty-ictr-irmct/` pour les TPIY/TPIR,
etc.

## Étape 2 · Les donner à votre assistant

Ouvrez votre assistant habituel et créez un espace de travail, puis
ajoutez-y les fichiers du tribunal qui vous intéresse (tout le contenu du
dossier, sous-dossiers compris) :

- **Claude** : claude.ai → « Projects » → « New project » → « Add files ».
- **Le Chat (Mistral)** : créez un « Projet », ajoutez les documents, et
  vérifiez que la recherche web est activée.
- **ChatGPT** : créez un « Project », ou joignez les fichiers à la
  conversation.

## Étape 3 · Posez une question

Dans cet espace, travaillez normalement. Par exemple :

> « Vérifie cette référence : ICC-02/17-138, Chambre d'appel, 5 mars 2020. »

> « Que dit la Chambre d'appel dans Bemba sur le contrôle effectif ? Avec les sources. »

> « Relis ce paragraphe de mon mémoire et vérifie chacune de ses citations. »

L'assistant appliquera la méthode : il ira chercher les documents officiels
(site du tribunal, ICC Legal Tools Database) **avant** de citer, vous dira à
quel niveau chaque référence est vérifiée, refusera de confirmer ce qu'il ne
trouve pas, et ne citera jamais un document confidentiel.

Une version PDF d'une page de ce tutoriel, à partager, est dans
[`docs/Tutoriel-Skills-Justice-Internationale.pdf`](docs/Tutoriel-Skills-Justice-Internationale.pdf).

---

Open source · licence CC BY 4.0 · aussi sur le catalogue Lawve
(lawve.ai/explore) · Impact Litigation Lab · Paris
