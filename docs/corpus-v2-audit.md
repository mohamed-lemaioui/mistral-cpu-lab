# Audit technique du corpus SFT v2 et de son entraîneur

Date : 2026-11-26. Portée : revue technique et méthodologique des 100 exemples `proxmox_sft_v2.jsonl`, des 12 cas gelés `proxmox_eval_v2.jsonl`, du formatage et de la reprise de `ministral_sft_epoch.py`. Ce rapport ne constitue pas une validation métier indépendante.

## Résultats réutilisés

- `FORMAT_OK 100` : le tokenizer réel a encodé les 100 exemples ; le prompt est masqué et seuls les tokens de réponse assistant contribuent à la loss. Séquences observées : 658–700 tokens, cibles 31–59 tokens selon les résultats conservés.
- `CONTAMINATION_OK` : contrôle exact et similarité lexicale sur train, évaluation v2, évaluations historiques et anciens jeux d’entraînement ; 100 exemples train, 12 cas d’évaluation, 10 cas historiques, 16 exemples d’anciens jeux. Aucune collision détectée par les seuils du script. Le plus grand cosinus TF-IDF rapporté pour l’évaluation v2 est 0,180 ; sources de l’évaluation v2 hors corpus train.
- `RESUME_OK` : fixture synthétique, reprise exacte des adaptateurs, état AdamW et RNG ; checkpoints corrompus, mauvais modèle ou recette refusés. Aucun poids de modèle métier entraîné.
- Les sources documentaires Proxmox, systemd, kernel, OpenZFS et chrony utilisées sont archivées dans `/tmp/opencode/audit-docs`.

## Corrections techniques

- Remplacement de `str.format` par substitution ciblée du placeholder `{observations}` dans le baseline Instruct et le formatteur SFT : les accolades présentes dans les observations ou dans les exemples de commandes ne sont plus interprétées comme des champs de format.
- Le formatteur impose un unique placeholder, une limite explicite de 1024 tokens sans troncature silencieuse et l’égalité des longueurs input/labels.
- L’entraîneur exige l’empreinte exacte approuvée du corpus, épingle modèle/révision, recette, versions, threads et code dans le plan, vérifie l’intégrité des checkpoints, l’état des gradients, les poids gelés et la progression des adaptateurs. Les checkpoints sont créés atomiquement et la reprise est verrouillée.

## Risques et limites restants

- Corpus synthétique assisté par IA, documentation technique relue automatiquement, réponses cibles non validées par un humain indépendant. La relecture cas par cas reste requise avant tout entraînement métier.
- Le contrôle de contamination est lexical/statistique ; il ne démontre pas l’indépendance sémantique ni la qualité des réponses. Seuils et corpus comparés sont documentés dans le script et son log.
- L’évaluation v2 ne remplace pas une évaluation humaine aveugle ; les scores du modèle ne sont pas encore mesurés.
- Les coûts pour l’époque réelle ne sont pas garantis par la fixture de reprise ; aucun entraînement ni benchmark nouveau n’a été lancé pendant cet audit.
- Hash SHA256 du train à approuver par le propriétaire : `5b5d9b023b67c716357fa9544d99d67744e7c6a62b4b18ee2f03d860087107a1`.

## Conclusion

Le pipeline technique et les contrôles de séparation sont prêts pour revue humaine. Ils établissent la faisabilité du formatage et de la reprise, pas une amélioration métier ni l’autorisation d’entraîner. Les données ne sont pas encore validées humainement.
