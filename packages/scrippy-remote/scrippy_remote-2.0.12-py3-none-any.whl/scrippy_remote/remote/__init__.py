"""
Ce module offre l'ensemble des objets, méthodes et fonctions permettant les opérations sur les hotes distants accessibles via SSH/SFTP et FTP.

- Exécution de comande sur hôte distant
- Copie de répertoires/fichiers sur hôte distant
- Suppression de répertoires/fichiers sur hôte distant
- Copie de fichiers entre hôtes distants (la machine locale agissant comme tampon)
- ...
"""

from scrippy_remote.remote.ssh import Ssh
from scrippy_remote.remote.ftp import Ftp
from scrippy_remote.remote.cifs import Cifs
