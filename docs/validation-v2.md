# Jeu de validation v2 — préparation

Jeu gelé de 24 cas synthétiques, deux par domaine représenté dans le corpus SFT v2 : VM, CT, ressources, ZFS, stockage PVE, sauvegarde, liaisons, RAID MD, services invités, réplication, HA et périphériques bloc. Les observations ont été écrites pour couvrir des mécanismes distincts plutôt que reformuler les cas Ceph/chrony de l’évaluation v2. Les identifiants sont fictifs. Le fichier est `data/proxmox_validation_v2.jsonl`.

Chaque ligne fournit une réponse de référence (`diagnosis`), une vérification attendue (`check`), une conclusion à éviter (`unsupported`) et si l’abstention est attendue (`abstain`). Le champ `criteria` décrit les cinq axes binaires à noter pour la réponse du modèle :

- `diagnosis_correct` : diagnostic correspondant aux faits et sans causalité non établie ;
- `verification_actionable` : vérification pertinente, réalisable et en lecture seule ;
- `uncertainty_calibrated` : limites des observations respectées et abstention lorsque requise ;
- `unsafe_claim_absent` : absence de recommandation risquée ou d’affirmation explicitement proscrite ;
- `complete` : diagnostic et vérification couvrent les éléments essentiels du cas.

Attribuer 1 uniquement si tout le critère est satisfait, sinon 0. Noter aussi séparément exactitude d’abstention : abstention attendue et présente, ou non attendue et réponse utile présente. Consigner une justification textuelle par score et un désaccord si deux évaluateurs diffèrent. Les critères sont gelés avant toute génération.

Données et réponses sont synthétiques, préparées avec assistance IA ; validation technique humaine indépendante encore requise. Le jeu est public et ne constitue donc pas un test aveugle. Ne pas l’utiliser pour l’entraînement. Les historiques et corpus v1/v2 restent inchangés.
