# Relecture du corpus français v2

100 exemples synthétiques rédigés avec assistance IA. Validation du propriétaire en attente. Chaque section donne les observations visibles par le modèle, la réponse cible complète et le repère dans la documentation officielle. Les identifiants d’infrastructure sont fictifs. Pour demander une correction, indiquer l’identifiant du cas et la phrase concernée.

Audit technique et méthodologique du 26 novembre 2026 : voir [docs/corpus-v2-audit.md](corpus-v2-audit.md). Les corrections apportées par cet audit ne constituent pas une validation humaine indépendante.

Empreinte SHA256 du [JSONL d’entraînement](../data/proxmox_sft_v2.jsonl)

`5b5d9b023b67c716357fa9544d99d67744e7c6a62b4b18ee2f03d860087107a1`

## vm

### 01 · `v2_balloon_min`

Sur le nœud Proxmox hébergeant la VM 410. La mémoire configurée est de 8192 Mio avec un minimum de 2048 Mio. L’invité voit moins de 8 Gio.

**Réponse cible.** Le minimum inférieur au maximum permet une allocation dynamique. Vérifier les valeurs memory et balloon avec qm config 410 et comparer au relevé dans l’invité au même instant.

[qm · balloon](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 02 · `v2_vcpu_topology`

Sur le nœud Proxmox hébergeant la VM 410. La configuration effective indique sockets=2 et cores=3, sans limite vcpus inférieure. L’application annonce six processeurs logiques.

**Réponse cible.** La topologie présente six vCPU à la VM. Relire sockets et cores dans qm config 410 --current ; cela ne renseigne pas sur le nombre de cœurs physiques réservés.

[qm · sockets](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 03 · `v2_cpu_model`

Sur le nœud Proxmox hébergeant la VM 410. La VM utilise le modèle CPU host. Une migration à chaud entre générations de processeurs différentes est envisagée. Aucun inventaire de la cible.

**Réponse cible.** La compatibilité reste indéterminée. Relever le modèle CPU effectif avec qm config 410 --current et comparer les fonctionnalités CPU exposées par les deux hôtes.

[qm · Migration](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 04 · `v2_disk_limit`

Sur le nœud Proxmox hébergeant la VM 410. scsi0 est configuré avec mbps_rd=20 ; les lectures longues plafonnent près de cette valeur.

**Réponse cible.** Le plafond de lecture du disque virtuel peut expliquer ce débit. Vérifier scsi0 dans qm config 410 --current et comparer les débits de lecture et d’écriture pendant la même période.

[qm · mbps_rd](https://pve.proxmox.com/pve-docs/qm.conf.5.html)

### 05 · `v2_agent_state`

Sur le nœud Proxmox hébergeant la VM 410. La case Guest Agent est cochée ; l’interface n’affiche aucune adresse IP de l’invité.

**Réponse cible.** L’option côté hôte ne prouve pas que l’agent répond dans l’invité. Vérifier agent dans qm config 410 puis, depuis la console Linux de l’invité, consulter systemctl status qemu-guest-agent.service.

[qm · guest agent](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 06 · `v2_pending_memory`

Sur le nœud Proxmox hébergeant la VM 410. Le panneau affiche une nouvelle valeur de mémoire en attente ; le système invité continue de rapporter l’ancienne.

**Réponse cible.** La valeur demandée peut différer de celle appliquée. Comparer qm pending 410 et qm config 410 --current sur l’hôte avant d’attribuer l’écart à l’invité.

[qm · pending](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 07 · `v2_unused_volume`

Sur le nœud Proxmox hébergeant la VM 410. La configuration contient unused0 et aucune entrée scsi, sata ou virtio ne référence ce même volume. Le disque manque dans l’invité.

**Réponse cible.** Le volume est référencé comme inutilisé et ne figure pas parmi les disques attachés. Comparer les identifiants dans qm config 410 --current sans supposer que les données ont été effacées.

[qm · unused](https://pve.proxmox.com/pve-docs/qm.conf.5.html)

### 08 · `v2_serial_console`

Sur le nœud Proxmox hébergeant la VM 410. La console série reste vide. La configuration contient serial0: socket ; aucun réglage de console de l’OS n’a été observé.

**Réponse cible.** Le port virtuel existe, mais l’émission sur ce port par l’OS reste inconnue. Vérifier serial0 dans qm config 410 et les réglages de console série de l’invité depuis sa console graphique.

[qm · serial0](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 09 · `v2_autostart_vm`

Sur le nœud Proxmox hébergeant la VM 410. Après le démarrage du nœud, cette VM hors HA reste arrêtée. La configuration indique onboot: 0.

**Réponse cible.** Le démarrage automatique au boot n’est pas demandé. Vérifier onboot dans qm config 410 et l’état présent avec qm status 410 ; cela n’explique pas un éventuel arrêt ultérieur.

[qm · onboot](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 10 · `v2_discard_vm`

Sur le nœud Proxmox hébergeant la VM 410. Le disque scsi0 ne transmet pas le discard. Après suppression de fichiers dans l’invité, la taille allouée côté stockage ne baisse pas.

**Réponse cible.** Sans transmission du discard, le stockage ne reçoit pas cette indication de libération par ce chemin. Vérifier discard sur scsi0 dans qm config 410 --current et la prise en charge du backend.

[qm · discard](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 11 · `v2_template_vm`

Sur le nœud Proxmox hébergeant la VM 410. La fiche de l’objet indique template: 1 ; l’opérateur le traite comme une VM de production à démarrer.

**Réponse cible.** L’objet est un modèle de clonage. Relire template dans qm config 410 et vérifier l’identifiant de la VM de travail dans l’inventaire avant d’interpréter son état.

[qm · template](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 12 · `v2_keyboard`

Sur le nœud de la VM 410, la saisie via la console VNC donne des symboles différents de la disposition attendue. Le clavier fonctionne en SSH.

**Réponse cible.** Le chemin de saisie de la console a sa propre disposition. Comparer keyboard dans qm config 410 avec le clavier du client et la disposition de l’invité avant de conclure à une panne matérielle.

[qm · keyboard](https://pve.proxmox.com/pve-docs/qm.conf.5.html)

## ct

### 13 · `v2_bind_backup`

Sur le nœud Proxmox du CT 420. mp0 lie directement /srv/docs à /docs. Après restauration de la sauvegarde vzdump, le contenu de /docs manque.

**Réponse cible.** Le contenu d’un bind mount hôte est exclu de la sauvegarde du CT. Vérifier le type et les deux chemins de mp0 avec pct config 420 et consulter le périmètre de la sauvegarde.

[pct · Bind Mount Points](https://github.com/proxmox/pve-docs/blob/master/pct.adoc)

### 14 · `v2_ct_features`

Sur le nœud Proxmox du CT 420. Un outil indique que l’imbrication est désactivée ; features ne contient pas nesting=1. Le système invité seul a été inspecté jusqu’ici.

**Réponse cible.** La fonctionnalité nesting n’est pas activée dans la configuration décrite. Relire features avec pct config 420 ; cela ne suffit pas à établir que toutes les erreurs de l’outil en découlent.

[pct · nesting](https://github.com/proxmox/pve-docs/blob/master/pct.adoc)

### 15 · `v2_ct_dns`

Sur le nœud Proxmox du CT 420. Le CT utilise un serveur DNS explicitement configuré différent de celui du nœud. L’opérateur s’attend à une copie de la configuration hôte.

**Réponse cible.** Une valeur nameserver explicite explique la divergence attendue. Comparer nameserver dans pct config 420 avec les résolveurs visibles dans le CT.

[pct · nameserver](https://pve.proxmox.com/pve-docs/pct.conf.5.html)

### 16 · `v2_ct_console`

Sur le nœud Proxmox du CT 420. La console PVE du CT utilise cmode=shell ; l’opérateur attend l’écran de connexion d’un terminal.

**Réponse cible.** Le mode shell ouvre directement un shell. Relire cmode dans pct config 420 et distinguer cet accès de l’ouverture d’un terminal avec invite de connexion.

[pct · cmode](https://pve.proxmox.com/pve-docs/pct.conf.5.html)

### 17 · `v2_ct_map`

Sur le nœud Proxmox du CT 420. Le CT est non privilégié. Un fichier créé par root dans le CT apparaît avec un UID élevé vu du nœud.

**Réponse cible.** Le mappage d’UID peut représenter root par un autre UID côté hôte. Vérifier unprivileged dans pct config 420 et consulter /proc/self/uid_map dans le CT avant d’interpréter la propriété.

[pct · unprivileged](https://github.com/proxmox/pve-docs/blob/master/pct.adoc)

### 18 · `v2_ct_os`

Sur le nœud Proxmox du CT 420. La distribution installée dans le CT diffère de la valeur ostype configurée. Les ajustements système au démarrage semblent inadaptés.

**Réponse cible.** Le type déclaré guide les adaptations propres à la distribution. Comparer ostype dans pct config 420 et /etc/os-release dans le CT.

[pct · ostype](https://pve.proxmox.com/pve-docs/pct.conf.5.html)

### 19 · `v2_ct_core_limit`

Sur le nœud Proxmox du CT 420. Le CT voit deux processeurs disponibles alors que le nœud en a douze ; la configuration contient cores: 2.

**Réponse cible.** La restriction à deux cœurs est cohérente avec cette visibilité. Vérifier cores dans pct config 420 et pct cpusets sur le nœud pour confirmer les CPU assignés.

[pct · cores](https://github.com/proxmox/pve-docs/blob/master/pct.adoc)

### 20 · `v2_ct_hook`

Sur le nœud Proxmox du CT 420. Un hook est déclaré pour ce CT. On lui attribue une lenteur de démarrage sans chronologie de la tâche.

**Réponse cible.** La seule présence du hook ne permet pas de lui attribuer le délai. Identifier la référence hookscript avec pct config 420 et comparer les horodatages des phases dans le journal de la tâche.

[pct · hookscript](https://github.com/proxmox/pve-docs/blob/master/pct.adoc)

### 21 · `v2_ct_protected`

Sur le nœud Proxmox du CT 420. La protection du CT est active et la suppression depuis l’interface est refusée.

**Réponse cible.** La protection configurée empêche la suppression. Vérifier protection et l’identifiant avec pct config 420 sans modifier ce réglage.

[pct · protection](https://pve.proxmox.com/pve-docs/pct.conf.5.html)

### 22 · `v2_ct_tty`

Sur le nœud du CT 420, tty vaut 1. Un deuxième terminal virtuel LXC est attendu.

**Réponse cible.** La configuration ne prévoit qu’un terminal tty pour le CT. Vérifier tty dans pct config 420 et le distinguer de la console principale.

[pct · tty](https://pve.proxmox.com/pve-docs/pct.conf.5.html)

## stockage-pve

### 23 · `v2_storage_content`

Sur le nœud Proxmox de laboratoire. Le stockage dir nommé depot accepte seulement iso et vztmpl. L’assistant de création de disque VM ne le propose pas.

**Réponse cible.** Le stockage n’annonce pas le contenu images requis pour les disques VM. Comparer les types de contenu autorisés dans la fiche de depot et la liste issue de pvesm status --content images.

[pvesm · content](https://github.com/proxmox/pve-docs/blob/master/pvesm.adoc)

### 24 · `v2_storage_nodes`

Sur le nœud Proxmox de laboratoire. Le stockage archives est limité au nœud alpha dans la configuration ; l’assistant est ouvert sur beta.

**Réponse cible.** La restriction nodes exclut beta de la sélection. Vérifier la liste de nœuds autorisés dans la fiche du stockage et comparer pvesm status sur alpha et beta.

[pvesm · nodes](https://github.com/proxmox/pve-docs/blob/master/pvesm.adoc)

### 25 · `v2_storage_shared`

Sur deux nœuds Proxmox, le stockage dir projets utilise un répertoire local au même chemin ; seule la case shared a été cochée. Les fichiers diffèrent.

**Réponse cible.** Le drapeau shared déclare un partage existant et ne réplique aucun fichier. Comparer la provenance des montages du chemin sur les deux nœuds et le contenu avec pvesm list projets sur chacun.

[pvesm · shared](https://github.com/proxmox/pve-docs/blob/master/pvesm.adoc)

### 26 · `v2_storage_volid`

Sur le nœud Proxmox de laboratoire. Une tâche référence depot:iso/install.iso ; l’opérateur cherche le fichier relativement au répertoire courant du shell.

**Réponse cible.** Il s’agit d’un identifiant de volume Proxmox. Sur le nœud concerné, consulter pvesm path depot:iso/install.iso pour résoudre le chemin du backend ; un chemin résolu ne prouve pas à lui seul que le fichier est lisible.

[pvesm · Volume Identifiers](https://github.com/proxmox/pve-docs/blob/master/pvesm.adoc)

### 27 · `v2_storage_filter`

Sur le nœud Proxmox de laboratoire, le stockage depot-vm est interrogé avec pvesm list depot-vm --vmid 411 et retourne une liste vide. La VM recherchée dans le ticket porte le numéro 412.

**Réponse cible.** La liste est filtrée sur une autre VM. Comparer pvesm list depot-vm --vmid 412 à l’identifiant de volume dans la fiche de la VM avant de conclure à une perte.

[pvesm · --vmid](https://pve.proxmox.com/pve-docs/pvesm.1.html)

### 28 · `v2_storage_layout`

Sur le nœud Proxmox, le stockage dir medias utilise content-dirs avec un répertoire personnalisé pour iso. L’équipe ne trouve rien dans template/iso.

**Réponse cible.** Le chemin par défaut peut être remplacé pour ce contenu. Lire content-dirs dans la fiche de medias et inventorier les images avec pvesm list medias --content iso.

[pvesm · content-dirs](https://pve.proxmox.com/pve-docs/pvesm.1.html)

### 29 · `v2_storage_alias`

Sur le nœud Proxmox de laboratoire. Deux identifiants de stockage pointent sur le même export et le même répertoire. L’inventaire présente deux noms pour la même image.

**Réponse cible.** Des noms de stockage distincts peuvent référencer les mêmes données. Comparer export, chemin et identifiants des volumes dans les deux fiches avant de compter deux copies indépendantes.

[pvesm · alias](https://github.com/proxmox/pve-docs/blob/master/pvesm.adoc)

### 30 · `v2_storage_format`

Sur le stockage dir images du nœud Proxmox, l’équipe attend des snapshots internes qcow2 pour un disque supposé raw. Aucun format réel n’a été contrôlé.

**Réponse cible.** La possibilité de prendre un snapshot interne qcow2 dépend du format de l’image. Consulter la colonne Format de pvesm list images et les capacités du backend avant de conclure.

[pvesm · qcow2](https://github.com/proxmox/pve-docs/blob/master/pvesm.adoc)

## sauvegarde

### 31 · `v2_backup_ct_pause`

Dans le journal de sauvegarde Proxmox du laboratoire. Pour un CT en mode suspend, deux passes de copie sont visibles avec une suspension entre les deux. On signale deux sauvegardes complètes.

**Réponse cible.** Ce mode effectue une première copie puis synchronise les changements pendant la suspension. Comparer les lignes de début, suspension et fin de la tâche avec la liste des archives effectivement créées.

[vzdump · suspend](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

### 32 · `v2_backup_stop_vm`

Dans le journal de sauvegarde Proxmox du laboratoire. Une VM en fonctionnement subit un arrêt ordonné au début de sa sauvegarde en mode stop puis redémarre avant la fin du transfert.

**Réponse cible.** Cette séquence est compatible avec le mode stop des VM. Comparer les horodatages d’arrêt et de reprise au transfert dans le journal de cette tâche.

[vzdump · stop](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

### 33 · `v2_backup_stopped`

Dans le journal de sauvegarde Proxmox du laboratoire. Une VM initialement arrêtée apparaît brièvement en cours d’exécution pendant la lecture de ses disques pour sauvegarde.

**Réponse cible.** Un processus QEMU de sauvegarde peut lire les disques sans démarrer le système invité. Comparer la fenêtre de la tâche avec les événements de démarrage observés dans l’invité.

[vzdump · background QEMU](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

### 34 · `v2_backup_freeze`

Dans le journal de sauvegarde Proxmox du laboratoire. La VM est sauvegardée à chaud ; l’agent invité était désactivé. Le fichier de sauvegarde est présent. Les applications ont-elles toutes été figées ?

**Réponse cible.** La présence de l’archive ne démontre pas le gel applicatif. Vérifier dans le journal de cette tâche les étapes de gel et dégel, puis les mécanismes de cohérence propres à l’application.

[vzdump · fsfreeze](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

### 35 · `v2_backup_disk_skip`

Dans le journal de sauvegarde Proxmox du laboratoire. Le journal désigne scsi1 comme exclu de la sauvegarde de la VM ; l’option de ce disque indique backup=0.

**Réponse cible.** L’exclusion est configurée pour ce disque. Comparer les identifiants de disques de la VM au détail des disques inclus dans la tâche avant d’évaluer la couverture.

[qm · backup=<boolean>](https://github.com/proxmox/pve-docs/blob/master/qm.adoc)

### 36 · `v2_backup_retention`

Dans le journal de sauvegarde Proxmox du laboratoire. Une politique keep-last=3 est configurée. L’opérateur pense qu’elle garantit trois jours d’historique alors que plusieurs sauvegardes ont lieu chaque jour.

**Réponse cible.** La règle compte des sauvegardes, pas des jours. Comparer la liste datée des sauvegardes du groupe aux règles de rétention effectivement appliquées.

[vzdump · keep-last](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

### 37 · `v2_backup_protect`

Dans le journal de sauvegarde Proxmox du laboratoire. Une ancienne archive protégée reste présente après un élagage réussi qui a supprimé des archives plus récentes.

**Réponse cible.** La protection peut soustraire cette archive à l’élagage. Consulter son indicateur de protection et le rapport d’élagage pour le même groupe.

[vzdump · protected](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

### 38 · `v2_backup_fleece`

Dans le journal de sauvegarde Proxmox du laboratoire. La VM utilise le fleecing. Un espace temporaire augmente sur le stockage de fleecing quand l’invité réécrit des blocs pendant la sauvegarde.

**Réponse cible.** Le fleecing conserve temporairement des blocs nécessaires à la vue sauvegardée. Comparer les périodes d’écriture et la progression de la tâche ; cette croissance seule n’indique pas une seconde archive complète.

[vzdump · fleecing](https://github.com/proxmox/pve-docs/blob/master/vzdump.adoc)

## replication

### 39 · `v2_rep_retry`

Sur le nœud Proxmox source de réplication. Le job prévu toutes les cinq minutes est passé en erreur. La nouvelle tentative annoncée est environ trente minutes plus tard.

**Réponse cible.** Le mécanisme de reprise après erreur peut suspendre provisoirement l’intervalle normal. Lire pvesr status et le dernier journal de ce job pour identifier l’erreur initiale.

[pvesr · 30 minute](https://github.com/proxmox/pve-docs/blob/master/pvesr.adoc)

### 40 · `v2_rep_rpo`

Sur le nœud Proxmox source de réplication. Dernière synchronisation réussie à 10 h. Des opérations dans l’invité ont eu lieu à 10 h 04 ; la source est tombée à 10 h 05.

**Réponse cible.** La copie asynchrone peut manquer les écritures postérieures à 10 h. Confirmer la dernière synchronisation réussie dans pvesr status et comparer les horodatages applicatifs.

[pvesr · data loss](https://github.com/proxmox/pve-docs/blob/master/pvesr.adoc)

### 41 · `v2_rep_direction`

Sur le nœud Proxmox source de réplication. Une VM répliquée de alpha vers beta est migrée vers beta. Le job signale désormais alpha comme cible.

**Réponse cible.** La direction peut s’inverser lorsque la migration aboutit sur la cible de réplication. Comparer le nœud propriétaire actuel à la cible indiquée par pvesr status.

[pvesr · direction](https://github.com/proxmox/pve-docs/blob/master/pvesr.adoc)

### 42 · `v2_rep_increment`

Sur le nœud Proxmox source de réplication. La première synchronisation d’un disque prend longtemps ; les suivantes transfèrent beaucoup moins malgré la même taille virtuelle.

**Réponse cible.** Après la copie initiale, la réplication peut transférer les changements de manière incrémentale. Comparer les volumes transférés et les durées des exécutions dans les journaux du job.

[pvesr · incremental](https://github.com/proxmox/pve-docs/blob/master/pvesr.adoc)

### 43 · `v2_rep_rate`

Sur le nœud Proxmox source de réplication. Le job a une limite de débit et son transfert plafonne près de cette valeur. L’équipe soupçonne une saturation physique du réseau.

**Réponse cible.** La limitation du job est une explication plausible. Vérifier rate avec pvesr list et comparer les mesures réseau pendant le transfert avant de conclure à une saturation.

[pvesr · rate](https://github.com/proxmox/pve-docs/blob/master/pvesr.adoc)

### 44 · `v2_rep_target_id`

Sur le nœud Proxmox source de réplication. Le journal indique que l’identifiant de stockage attendu manque sur la cible alors qu’un pool de même capacité existe sous un autre identifiant.

**Réponse cible.** Une capacité équivalente ne fournit pas l’identifiant attendu par le job. Comparer l’identifiant référencé par le disque et celui déclaré sur le nœud cible, puis relire le journal de réplication.

[pvesr · same storage ID](https://github.com/proxmox/pve-docs/blob/master/pvesr.adoc)

## ha

### 45 · `v2_ha_ignored`

Dans la vue HA du cluster Proxmox de laboratoire. La ressource vm:430 est configurée avec l’état demandé ignored. Une panne de l’invité ne provoque aucune action HA.

**Réponse cible.** Cet état laisse la ressource hors de la gestion active par HA. Comparer sa configuration dans ha-manager config et son état dans ha-manager status.

[ha-manager · ignored](https://github.com/proxmox/pve-docs/blob/master/ha-manager.adoc)

### 46 · `v2_ha_queued`

Dans la vue HA du cluster Proxmox de laboratoire. Juste après l’ajout d’une ressource, la vue montre queued. Aucun échec de démarrage n’est journalisé.

**Réponse cible.** Cet état correspond à une nouvelle ressource encore à prendre en compte par le CRM. Relire ha-manager status après un cycle et comparer la chronologie avant de diagnostiquer un échec.

[ha-manager · queued](https://github.com/proxmox/pve-docs/blob/master/ha-manager.adoc)

### 47 · `v2_ha_error`

Dans la vue HA du cluster Proxmox de laboratoire. Après plusieurs échecs de démarrage, vm:431 est en état error ; la cause applicative est inconnue.

**Réponse cible.** La ressource est passée en erreur de gestion HA. Comparer ha-manager status et le journal du gestionnaire local sur le nœud concerné ; cet état seul ne donne pas la cause des échecs.

[ha-manager · error](https://github.com/proxmox/pve-docs/blob/master/ha-manager.adoc)

### 48 · `v2_ha_restart`

Dans la vue HA du cluster Proxmox de laboratoire. La ressource a max_restart=2. Deux tentatives locales apparaissent avant une tentative sur un autre nœud.

**Réponse cible.** La politique distingue les tentatives locales et la relocalisation. Relire max_restart et max_relocate dans ha-manager config puis vérifier la séquence dans les événements HA.

[ha-manager · max_restart](https://github.com/proxmox/pve-docs/blob/master/ha-manager.adoc)

### 49 · `v2_ha_maintenance`

Dans la vue HA du cluster Proxmox de laboratoire. Un nœud a été mis en maintenance HA. Les ressources sont déplacées alors que le nœud reste joignable.

**Réponse cible.** La maintenance peut déclencher l’évacuation des ressources HA. Vérifier le statut de maintenance et les déplacements dans ha-manager status avant d’inférer une panne matérielle.

[ha-manager · maintenance](https://github.com/proxmox/pve-docs/blob/master/ha-manager.adoc)

### 50 · `v2_ha_freeze`

Dans la vue HA du cluster Proxmox de laboratoire. Pendant le redémarrage du gestionnaire local, une ressource apparaît en état freeze. Aucune mesure n’a été faite dans l’invité.

**Réponse cible.** Cet état décrit la suspension des actions du gestionnaire sur la ressource. Comparer les événements du LRM avec ha-manager status ; le terme freeze ne prouve pas que l’OS invité est bloqué.

[ha-manager · freeze](https://github.com/proxmox/pve-docs/blob/master/ha-manager.adoc)

## ressources

### 51 · `v2_cg_high`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. Pendant la lenteur, high dans memory.events.local augmente et l’usage dépasse memory.high. Aucun événement oom_kill ne progresse.

**Réponse cible.** La limite haute a déclenché du reclaim et de la régulation. Comparer memory.current, memory.high et la variation locale de high sur le même intervalle.

[cgroup · memory.high](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 52 · `v2_cg_weight`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. cpu.weight vaut 200 pour un service et 100 pour son frère. Le premier n’utilise pas constamment deux fois plus de CPU.

**Réponse cible.** Le poids répartit relativement le CPU en situation de concurrence. Comparer cpu.weight et les deltas de cpu.stat des groupes frères sur une période où tous deux demandent du CPU.

[cgroup · cpu.weight](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 53 · `v2_cg_cpuset`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. cpuset.cpus demande 0-7 ; cpuset.cpus.effective indique 2-3. Le service ne tourne que sur ces deux CPU.

**Réponse cible.** Le jeu effectif décrit les CPU effectivement accordés. Lire cpuset.cpus.effective dans le groupe et ses ancêtres pour localiser la restriction.

[cgroup · cpuset.cpus.effective](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 54 · `v2_cg_io_limit`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. io.max contient une limite rbps pour 8:16. Les lectures sont lentes mais le périphérique utilisé par le service n’est pas identifié.

**Réponse cible.** L’attribution reste indéterminée. Comparer les numéros majeur:mineur de io.stat et io.max et les volumes réellement lus pendant la lenteur.

[cgroup · io.max](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 55 · `v2_cg_swap`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. memory.swap.max vaut 0 pour le groupe ; l’hôte dispose pourtant d’un espace de swap libre.

**Réponse cible.** Le groupe ne peut pas augmenter son utilisation du swap au-delà de cette limite. Lire memory.swap.current dans le même cgroup ; l’espace libre global ne lève pas la restriction.

[cgroup · memory.swap.max](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 56 · `v2_cg_frozen`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. cgroup.freeze vaut 1 et cgroup.events indique frozen 1. Le service semble totalement immobile.

**Réponse cible.** Le gel du cgroup est effectif. Vérifier frozen dans cgroup.events et la demande de gel des ancêtres ; ces fichiers ne permettent pas d’identifier l’auteur de la demande.

[cgroup · cgroup.freeze](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 57 · `v2_cg_population`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. cgroup.procs est vide ici, mais populated vaut 1 dans cgroup.events. Le service possède des sous-groupes.

**Réponse cible.** Des processus peuvent se trouver dans les descendants. Comparer cgroup.procs des sous-groupes et populated dans leur cgroup.events avant de conclure à un compteur incohérent.

[cgroup · populated](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 58 · `v2_cg_io_share`

Sur l’hôte Proxmox, dans le cgroup v2 du service concerné. Les poids E/S de deux groupes sont différents. Une unique mesure à faible charge ne montre aucune différence de débit.

**Réponse cible.** Les poids sont relatifs et leur effet dépend du contrôleur et de la concurrence. Comparer io.weight et les variations de io.stat pour le même périphérique sous charge comparable.

[cgroup · io.weight](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 59 · `v2_psi_io`

Dans le système invité Linux de la VM. /proc/pressure/io montre some avg10 élevé et full avg10 faible pendant le ralentissement.

**Réponse cible.** Des tâches attendent des E/S, mais toutes les tâches non inactives ne sont pas bloquées simultanément la plupart du temps. Comparer some et full sur plusieurs intervalles ; PSI seul ne désigne pas le disque.

[psi · some](https://docs.kernel.org/accounting/psi.html)

### 60 · `v2_psi_windows`

Dans le système invité Linux de la VM. Après un pic bref, avg10 dans /proc/pressure/memory a fortement baissé ; avg300 reste élevé. La pénurie est-elle encore sévère ?

**Réponse cible.** Les fenêtres lissent des durées différentes. Suivre avg10 et la progression de total sur deux relevés rapprochés avant de qualifier la pression actuelle.

[psi · avg300](https://docs.kernel.org/accounting/psi.html)

## liaisons

### 61 · `v2_bond_backup`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. Le mode est active-backup. Deux interfaces sont disponibles, mais les octets de trafic ordinaire progressent surtout sur une seule.

**Réponse cible.** Une interface active à la fois est attendue dans ce mode. Consulter le membre actif et l’état des deux membres dans /proc/net/bonding/bond0.

[bond · active-backup](https://docs.kernel.org/networking/bonding.html)

### 62 · `v2_bond_hash`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. En mode 802.3ad, un transfert TCP unique plafonne à la vitesse d’un membre, malgré plusieurs membres dans le même agrégat actif.

**Réponse cible.** Le hachage peut maintenir ce flux sur un seul membre. Lire /sys/class/net/bond0/bonding/xmit_hash_policy et comparer les compteurs par membre pour plusieurs flux distincts.

[bond · xmit_hash_policy](https://docs.kernel.org/networking/bonding.html)

### 63 · `v2_bond_monitor`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. miimon vaut 100. Le pilote rapporte une liaison active alors qu’un service situé plusieurs sauts plus loin ne répond pas.

**Réponse cible.** La surveillance MII porte sur le lien local. Vérifier le type de surveillance et l’état par membre dans /proc/net/bonding/bond0 ; le diagnostic du service distant demande d’autres observations.

[bond · miimon](https://docs.kernel.org/networking/bonding.html)

### 64 · `v2_bond_primary`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. Après le retour du membre primaire, le membre de secours reste actif ; primary_reselect est configuré sur failure.

**Réponse cible.** Cette politique conserve le membre actif tant qu’il fonctionne. Relire primary_reselect et active_slave dans /sys/class/net/bond0/bonding/ pour confirmer le comportement.

[bond · primary_reselect](https://docs.kernel.org/networking/bonding.html)

### 65 · `v2_bond_lacp`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. Le mode est 802.3ad et lacp_rate est slow. Une équipe attend des LACPDU du partenaire chaque seconde.

**Réponse cible.** Le réglage slow demande une cadence lente au partenaire. Vérifier lacp_rate et les informations du partenaire dans /proc/net/bonding/bond0 avant de conclure à des pertes.

[bond · lacp_rate](https://docs.kernel.org/networking/bonding.html)

### 66 · `v2_bond_delays`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. Le lien physique revient. miimon est actif et updelay vaut 5000 ; le membre ne redevient utilisable qu’après plusieurs secondes.

**Réponse cible.** Le délai d’activation configuré peut expliquer l’attente. Lire updelay et miimon sous /sys/class/net/bond0/bonding/ et comparer au délai observé.

[bond · updelay](https://docs.kernel.org/networking/bonding.html)

### 67 · `v2_bond_broadcast`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. Le mode déclaré est broadcast ; les mêmes émissions sont comptées sur plusieurs membres.

**Réponse cible.** Ce mode transmet sur tous les membres. Vérifier mode et slaves sous /sys/class/net/bond0/bonding/ avant d’attribuer les compteurs à une boucle.

[bond · broadcast](https://docs.kernel.org/networking/bonding.html)

### 68 · `v2_bond_aggregator`

Sur l’hôte Proxmox, le bond synthétique est nommé bond0. Le mode est 802.3ad. Deux membres sont UP, mais leurs identifiants d’agrégateur diffèrent. La capacité utilisable est-elle la somme des deux ?

**Réponse cible.** La somme n’est pas établie. Comparer les identifiants des membres à l’agrégateur actif dans /proc/net/bonding/bond0 et contrôler la vue LACP du commutateur.

[bond · ad_select](https://docs.kernel.org/networking/bonding.html)

## zfs

### 69 · `v2_zfs_snapspace`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. Des fichiers ont été effacés. usedbysnapshots reste élevé et des snapshots antérieurs à l’effacement existent.

**Réponse cible.** Des blocs peuvent rester référencés par les snapshots. Comparer zfs get usedbysnapshots,usedbydataset labo/app avec les dates des snapshots avant d’estimer les blocs récupérables.

[zfsprops · usedbysnapshots](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 70 · `v2_zfs_refquota`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. refquota vaut 20 Gio, referenced approche 20 Gio et le pool dispose encore d’espace.

**Réponse cible.** Le dataset approche sa propre limite de données référencées. Comparer zfs get refquota,referenced,available labo/app ; l’espace du pool seul ne décrit pas la marge du dataset.

[zfsprops · refquota](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 71 · `v2_zfs_reserve`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. refreservation est non nulle alors que le dataset contient très peu de données. Le parent comptabilise néanmoins de l’espace utilisé.

**Réponse cible.** Une réservation peut peser sur la comptabilité du parent. Lire zfs get refreservation,usedbyrefreservation labo/app pour quantifier cette contribution.

[zfsprops · refreservation](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 72 · `v2_zfs_mount`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. canmount vaut noauto ; le dataset reste démonté après l’opération de montage automatique globale.

**Réponse cible.** noauto exclut le dataset du montage automatique global. Vérifier zfs get canmount,mounted,mountpoint labo/app avant d’interpréter cet état comme une panne.

[zfsprops · canmount](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 73 · `v2_zfs_inherit`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. La compression du dataset passe à lz4 après un changement sur le parent ; la colonne SOURCE indique inherited.

**Réponse cible.** La propriété est héritée du parent indiqué. Examiner zfs get compression labo/app et la colonne SOURCE pour situer l’origine de la valeur.

[zfsprops · inherited](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 74 · `v2_zfs_atime`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. atime vaut off. Après lecture d’un fichier, sa date de dernier accès reste inchangée.

**Réponse cible.** La mise à jour des dates d’accès est désactivée sur ce dataset. Vérifier zfs get atime labo/app ; cette date ne permet donc pas de conclure que le fichier n’a pas été lu.

[zfsprops · atime](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 75 · `v2_zfs_record`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. recordsize vaut 128K. On en déduit que chaque lecture applicative transporte exactement 128 Kio.

**Réponse cible.** recordsize décrit une taille de bloc suggérée pour les fichiers. Consulter zfs get recordsize labo/app et comparer avec des mesures d’E/S applicatives avant d’identifier une taille de requête.

[zfsprops · recordsize](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 76 · `v2_zfs_sync`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. sync vaut always sur le dataset. Les petites écritures présentent une latence élevée ; aucune latence disque n’est fournie.

**Réponse cible.** Toutes les transactions d’écriture sont traitées de façon synchrone avec cette politique. Vérifier zfs get sync labo/app et comparer les temps des écritures ; la part de latence imputable aux disques reste inconnue.

[zfsprops · sync](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 77 · `v2_zfs_clone`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. origin indique labo/base@initial. Un opérateur présente labo/app comme une copie entièrement indépendante de ce snapshot.

**Réponse cible.** Le dataset est un clone issu de ce snapshot. Vérifier zfs get origin labo/app et la propriété clones du snapshot source pour documenter la dépendance.

[zfsprops · origin](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

### 78 · `v2_zfs_ratio`

Sur le nœud Proxmox hébergeant le dataset ZFS labo/app. compressratio annonce 1.02x alors que compression est activée. On suppose un défaut du compresseur.

**Réponse cible.** Un faible gain peut tenir aux données déjà compressées ou à leur historique. Comparer zfs get compression,compressratio,refcompressratio labo/app ; ces valeurs ne démontrent pas un défaut.

[zfsprops · compressratio](https://openzfs.github.io/openzfs-docs/man/master/7/zfsprops.7.html)

## raid-md

### 79 · `v2_md_resync`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. sync_action indique resync après un arrêt non propre ; tous les membres attendus sont présents.

**Réponse cible.** Une resynchronisation de la redondance est en cours. Suivre sync_action et sync_completed dans /sys/block/md2/md/ ; cette opération seule ne désigne pas un disque défaillant.

[md · resync](https://docs.kernel.org/admin-guide/md.html)

### 80 · `v2_md_recover`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. Un disque de remplacement a été ajouté et sync_action affiche recover.

**Réponse cible.** Le noyau reconstruit un membre à partir des données redondantes. Vérifier sync_completed et les états des membres dans /sys/block/md2/md/ pour suivre la reconstruction.

[md · recover](https://docs.kernel.org/admin-guide/md.html)

### 81 · `v2_md_check`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. À la fin d’un check RAID1, mismatch_cnt est non nul. Quel membre contient la bonne copie ?

**Réponse cible.** Le compteur signale des secteurs discordants sans identifier la copie correcte. Consulter mismatch_cnt et les états par membre sous /sys/block/md2/md/ ; le compteur seul ne tranche pas.

[md · mismatch_cnt](https://docs.kernel.org/admin-guide/md.html)

### 82 · `v2_md_reshape`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. Après extension de la baie, reshape_position est numérique et avance. Les mesures de débit fluctuent.

**Réponse cible.** Une transformation de géométrie progresse. Suivre reshape_position et les anciennes et nouvelles valeurs de géométrie sous /sys/block/md2/md/ avant de comparer le débit à son régime stable.

[md · reshape_position](https://docs.kernel.org/admin-guide/md.html)

### 83 · `v2_md_sync_limit`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. La reconstruction semble lente. sync_speed_max affiche une limite locale inférieure à la limite système.

**Réponse cible.** Le plafond local peut contraindre la reconstruction. Comparer sync_speed et sync_speed_max dans /sys/block/md2/md/ avec la progression observée et la charge applicative.

[md · sync_speed_max](https://docs.kernel.org/admin-guide/md.html)

### 84 · `v2_md_writebehind`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. Sur le miroir md2, un membre est marqué writemostly. Les lectures ordinaires vont surtout à l’autre membre.

**Réponse cible.** Le pilote évite autant que possible de lire le membre marqué. Vérifier les fichiers state des membres sous /sys/block/md2/md/ avant de diagnostiquer une répartition anormale.

[md · writemostly](https://docs.kernel.org/admin-guide/md.html)

### 85 · `v2_md_bitmap`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. bitmap/location indique +8. L’opérateur considère cette valeur comme la progression d’une reconstruction.

**Réponse cible.** Cette valeur décrit l’emplacement du bitmap de suivi des écritures : +8 désigne un décalage en secteurs depuis le début des métadonnées. Lire bitmap/location puis sync_action et sync_completed sous /sys/block/md2/md/ pour distinguer configuration et progression.

[md · bitmap/location](https://docs.kernel.org/admin-guide/md.html)

### 86 · `v2_md_chunk`

Sur le nœud de stockage Linux attaché à Proxmox, baie MD md2. La baie RAID5 a chunk_size=65536. On déduit de ce seul chiffre le débit maximal du volume.

**Réponse cible.** La taille de chunk décrit la géométrie, pas un débit. Lire chunk_size, raid_disks et level dans /sys/block/md2/md/ et demander une mesure temporelle pour quantifier les performances.

[md · chunk_size](https://docs.kernel.org/admin-guide/md.html)

## services-invités

### 87 · `v2_svc_oneshot`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Type=oneshot, RemainAfterExit=yes ; le statut indique active (exited) après succès, sans processus permanent.

**Réponse cible.** Ce type d’unité peut rester active après la fin de sa tâche. Comparer systemctl show lot.service -p Type -p RemainAfterExit -p Result avec le résultat du dernier lancement.

[systemd · RemainAfterExit](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

### 88 · `v2_svc_notify`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Type=notify. Le programme a démarré, mais l’unité reste activating ; aucune notification de disponibilité n’est observée.

**Réponse cible.** Le gestionnaire attend le signal de disponibilité. Vérifier systemctl show lot.service -p Type -p NotifyAccess -p ActiveState et les messages de démarrage avant de conclure que l’application est prête.

[systemd · READY=1](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

### 89 · `v2_svc_onesig`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Type=forking ; le processus parent lancé au démarrage ne se termine pas. Le gestionnaire reste en phase d’activation.

**Réponse cible.** Pour ce type, la fin du parent participe à la détection de fin de démarrage. Comparer systemctl show lot.service -p Type -p ActiveState aux événements du programme.

[systemd · Type=forking](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

### 90 · `v2_svc_restart`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Restart=on-failure ; la tâche sort avec le code 0 sans signal. L’absence de redémarrage surprend l’opérateur.

**Réponse cible.** Une sortie normale ne déclenche pas ce mode de relance. Vérifier systemctl show lot.service -p Restart -p Result -p ExecMainStatus.

[systemd · on-failure](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

### 91 · `v2_svc_post`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Le programme principal paraît prêt, mais une commande ExecStartPost est toujours en cours. Une unité ordonnée après lot attend.

**Réponse cible.** La phase post-démarrage participe à l’ordre de démarrage. Comparer systemctl show lot.service -p SubState -p ActiveState aux horodatages de la dernière activation.

[systemd · ExecStartPost](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

### 92 · `v2_svc_condition`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. ExecCondition sort avec 1 ; le démarrage principal est sauté et l’unité n’est pas marquée failed.

**Réponse cible.** Ce code de condition peut faire ignorer les étapes suivantes sans marquer le service en échec. Vérifier systemctl status lot.service et la ligne relative à ExecCondition.

[systemd · ExecCondition](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)

### 93 · `v2_svc_reload`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Après modification d’un fichier d’unité sur disque, NeedDaemonReload vaut yes. Le comportement courant correspond à l’ancienne définition.

**Réponse cible.** La définition chargée peut différer du fichier sur disque. Comparer systemctl cat lot.service à systemctl show lot.service -p NeedDaemonReload -p Type pour distinguer les deux vues.

[systemctl · daemon-reload](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

### 94 · `v2_svc_dropin`

Dans l’invité Debian d’une VM Proxmox, unité lot.service. Une option de relance affichée avec systemctl show diffère du fichier d’unité principal ; un répertoire lot.service.d existe.

**Réponse cible.** Un fragment complémentaire peut modifier la valeur effective. Lire systemctl cat lot.service et comparer les directives Restart à systemctl show lot.service -p Restart.

[systemctl · drop-in](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

## bloc

### 95 · `v2_blk_alignment`

Dans l’invité Linux, périphérique virtuel vdb. logical_block_size indique 512 et physical_block_size 4096. Le ticket décrit deux disques incompatibles.

**Réponse cible.** Ce sont deux granularités du même périphérique. Comparer ces deux fichiers sous /sys/block/vdb/queue/ ; ils ne suffisent pas à établir un mauvais alignement des partitions.

[queue · physical_block_size](https://docs.kernel.org/5.15/block/queue-sysfs.html)

### 96 · `v2_blk_rotation`

Dans l’invité Linux, périphérique virtuel vdb. rotational vaut 0 dans l’invité. Peut-on certifier que tous les supports du backend sont des SSD ?

**Réponse cible.** La valeur décrit le périphérique présenté à l’invité. Lire /sys/block/vdb/queue/rotational puis consulter l’inventaire du backend pour connaître les supports physiques.

[queue · rotational](https://docs.kernel.org/5.15/block/queue-sysfs.html)

### 97 · `v2_blk_scheduler`

Dans l’invité Linux, périphérique virtuel vdb. Le fichier scheduler affiche « [none] mq-deadline ». Un opérateur lit cela comme deux ordonnanceurs actifs simultanément.

**Réponse cible.** Les crochets identifient l’ordonnanceur sélectionné. Relire /sys/block/vdb/queue/scheduler ; mq-deadline est ici une option disponible.

[queue · scheduler](https://docs.kernel.org/5.15/block/queue-sysfs.html)

### 98 · `v2_blk_maxreq`

Dans l’invité Linux, périphérique virtuel vdb. max_sectors_kb vaut 128 et max_hw_sectors_kb vaut 1024. Des requêtes plus grandes que 128 Kio sont découpées.

**Réponse cible.** La limite logicielle de la file peut être plus basse que la limite matérielle annoncée. Comparer les deux fichiers sous /sys/block/vdb/queue/ avant d’imputer le découpage au support physique.

[queue · max_sectors_kb](https://docs.kernel.org/5.15/block/queue-sysfs.html)

### 99 · `v2_blk_readahead`

Dans l’invité Linux, périphérique virtuel vdb. read_ahead_kb vaut 128. On affirme que chaque lecture aléatoire de 4 Kio provoque exactement 128 Kio de lecture anticipée.

**Réponse cible.** Le réglage définit une limite de lecture anticipée, pas le volume de chaque opération. Relire /sys/block/vdb/queue/read_ahead_kb et comparer avec le profil réel des accès.

[queue · read_ahead_kb](https://docs.kernel.org/5.15/block/queue-sysfs.html)

### 100 · `v2_blk_iostats`

Dans l’invité Linux, périphérique virtuel vdb. iostats vaut 0 pour vdb ; une application lit des fichiers tandis que les statistiques bloc ne progressent pas.

**Réponse cible.** La collecte des statistiques d’E/S de la file est désactivée. Vérifier /sys/block/vdb/queue/iostats et quel périphérique sert réellement les fichiers avant de conclure à une absence d’activité.

[queue · iostats](https://docs.kernel.org/5.15/block/queue-sysfs.html)

For the English audit summary, see [SFT v2 corpus and training pipeline audit](sft-v2-audit.md).
