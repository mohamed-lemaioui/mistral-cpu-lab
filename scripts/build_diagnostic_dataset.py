"""Small, manually authored synthetic pilot; scenario-disjoint splits."""
import json
from pathlib import Path
CASES = [
("train","storage","thin_data","pvesm status: local-lvm active 99% used; lvs: Data% 99.1, Meta% 12","Le thin pool est presque saturé en données.","lvs -a -o lv_name,data_percent,metadata_percent; pvesm status","Ne pas supprimer de volume sans inventaire."),
("train","storage","thin_meta","lvs: Data% 40, Meta% 98.7","Les métadonnées du thin pool sont presque saturées.","lvs -a -o lv_name,data_percent,metadata_percent","Ne pas confondre saturation des données et des métadonnées."),
("train","network","bridge_link","ip link: vmbr0 UP; eno1 NO-CARRIER","La liaison physique eno1 est indisponible.","ip -br link; bridge link","Vérifier le lien et le câblage avant toute modification."),
("train","network","vlan_mismatch","VM tag=30; bridge vlan show: port invité VLAN 30; uplink VLAN 10 uniquement","Le VLAN 30 semble absent du chemin montant.","bridge vlan show; ip -d link show","Confirmer la configuration du commutateur."),
("train","lxc","memory_limit","memory.max=1073741824; memory.events: oom_kill 4","Des processus ont subi des OOM dans le cgroup.","cat memory.events; cat memory.max","Vérifier les événements et la consommation avant de changer le quota."),
("train","lxc","rootfs_full","df -h /: 100%; df -i /: 12%","Le système de fichiers racine manque d'espace, pas d'inodes.","df -h; df -i; du -x -h --max-depth=1 /","Ne pas effacer de fichiers automatiquement."),
("train","vm","boot_order","qm config: boot order=net0; scsi0 present; console PXE","L'ordre de démarrage privilégie uniquement le réseau.","qm config 901","Vérifier le disque et l'ordre souhaité avant modification."),
("train","vm","missing_iso","task log: volume local:iso/lab.iso does not exist","Le média ISO référencé est introuvable.","qm config 902; pvesm list local --content iso","Confirmer la référence du média."),
("train","backup","backup_space","vzdump log: No space left on device; backup target df 100%","La destination de sauvegarde manque d'espace.","pvesm status; df -h","Ne pas supprimer les sauvegardes sans politique de rétention."),
("train","backup","backup_permission","vzdump log: Permission denied creating archive; NFS mounted","Un problème de permissions sur la destination est probable.","findmnt; ls -ld /mnt/backup","Vérifier les droits et le mapping NFS."),
("train","services","proxy_down","systemctl is-active pveproxy: inactive; port 8006 absent","Le service d'interface HTTPS est arrêté.","systemctl status pveproxy; journalctl -u pveproxy -n 50","Identifier la cause avant redémarrage."),
("train","services","quorum","pvecm status: Quorate: No; Expected votes: 3; Total votes: 1","Le cluster n'a pas le quorum.","pvecm status; corosync-quorumtool -s","Ne pas forcer le quorum."),
("validation","storage","inode_full","df -h /: 35%; df -i /: 100%; touch: No space left on device","Les inodes du système de fichiers sont épuisés.","df -i; df -h","Identifier les répertoires contenant beaucoup de fichiers."),
("validation","network","duplicate_ip","arping duplicate address detection reports replies","Une adresse IP dupliquée est probable.","ip neigh show; ip addr show","Confirmer le conflit avant de modifier les adresses."),
("validation","lxc","pid_limit","pids.current=128; pids.max=128; fork: Resource temporarily unavailable","La limite de processus du cgroup est atteinte.","cat pids.current; cat pids.max; cat pids.events","Identifier les processus responsables."),
("validation","services","api_unclear","Interface Web inaccessible; aucune autre mesure","Les éléments sont insuffisants pour identifier la cause.","systemctl status pveproxy; ss -lnt; journalctl -u pveproxy -n 50","Ne pas conclure que le service est arrêté sans mesure."),
("test","storage","storage_offline","pvesm status: archive inactive; local active; mountpoint absent","Le stockage archive est indisponible; sa cause reste à établir.","pvesm status; findmnt; cat /etc/pve/storage.cfg","Ne pas monter ou recréer le stockage automatiquement."),
("test","network","missing_gateway","ip route: connected subnet only, no default route; local access works","Une route par défaut manque pour les destinations externes.","ip route show; ip addr show","Confirmer la passerelle attendue."),
("test","vm","lock","qm start task: VM is locked (backup); backup status unknown","Un verrou de sauvegarde bloque le démarrage.","qm config 903; pvesh get /cluster/tasks","Vérifier si la sauvegarde est active avant toute suppression de verrou."),
("test","backup","backup_unknown","Dernière sauvegarde signalée en échec, aucun journal disponible","Les informations sont insuffisantes pour diagnostiquer l'échec.","pvesh get /cluster/tasks; pvesm status","Consulter le journal de la tâche, ne pas inventer la cause."),
("test","lxc","read_only","journal: EXT4-fs error; mount flags ro; write fails","Le système de fichiers est en lecture seule après une erreur possible.","findmnt; journalctl -k -n 50","Ne pas remonter en écriture avant diagnostic."),
("test","services","certificate","Client HTTPS: certificate has expired; pveproxy active","Le certificat présenté semble expiré.","openssl s_client -connect localhost:8006 </dev/null | openssl x509 -noout -dates","Vérifier également l'heure système."),
]
def main():
    root=Path(__file__).resolve().parents[1]/"data"
    root.mkdir(exist_ok=True)
    assert len({r[2] for r in CASES})==len(CASES)
    for split in ("train","validation","test"):
        rows=[dict(id=key,domain=domain,observations=obs,diagnosis=diag,checks=checks,caution=caution) for sp,domain,key,obs,diag,checks,caution in CASES if sp==split]
        (root/f"proxmox_{split}.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows))
        print(split,len(rows))
if __name__=="__main__":
    main()
