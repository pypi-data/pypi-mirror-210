"""Le module scrippy_remote.remote.ftp implémente la partie cliente du protocole FTP sous forme de la classe Ftp."""
import os
import re
import ssl
import logging
from scrippy_remote.remote.scrippy_ftp import FtpSimple, Ftps, Ftpes
from scrippy_remote import ScrippyRemoteError


class Ftp:
  """La classe principale permettant la manipulation des hotes distants via FTP."""

  def __init__(self, hostname, port=21,
               username="anonymous", password="",
               tls=True, explicit=True, ssl_verify=True,
               ssl_version=ssl.PROTOCOL_TLSv1_2):
    """Initialise le client FTP."""
    logging.debug("[+] Connection initialization:")
    self.hostname = hostname
    self.port = port
    self.username = username
    self.password = password
    self.tls = tls
    self.explicit = explicit
    self.ssl_verify = ssl_verify
    self.ssl_version = ssl_version
    if self.tls:
      if explicit:
        self.remote = Ftpes(self.hostname,
                            self.port,
                            self.username,
                            self.password,
                            self.ssl_verify,
                            self.ssl_version)
      else:
        self.remote = Ftps(self.hostname,
                           self.port,
                           self.username,
                           self.password,
                           self.ssl_verify,
                           self.ssl_version)
    else:
      self.remote = FtpSimple(self.hostname,
                              self.port,
                              self.username,
                              self.password)

  def __enter__(self):
    """Point d'entrée."""
    self.connect()
    return self

  def __exit__(self, type_err, value, traceback):
    """Point de sortie."""
    del type_err, value, traceback
    self.close()

  def connect(self):
    """Se connecte au serveur FTP distant."""
    connected = False
    logging.debug(f"[+] Connecting to {self.username}@{self.hostname}:{self.port}")
    try:
      connected = self.remote.connect()
      if connected:
        self.remote.login()
    except Exception as err:
      logging.critical(f" +-> Unexpected error: [{err.__class__.__name__}] {err}")
    finally:
      return connected

  def close(self):
    """Ferme la connexion."""
    logging.debug(f"[+] Closing connection to {self.username}@{self.hostname}")
    if self.remote:
      self.remote.close()

  def get_file(self, remote_file, local_dir, create_dir=False):
    """
    Recupere le fichier distant 'filepath' et le copie dans 'local_dir'.
    Si create_dir est positionne a True alors l'arborescence distante est recree localement dans le repertoire 'local_dir'.

    ex: get_file(remote_file='/dead/parrot/parrot.txt',
                 local_dir='/home/luiggi.vercotti',
                 create_dir=True)
    créera l'arborescence locale: '/home/luiggi.vercotti/dead/parrot'
    et y copiera le fichier distant '/dead/parrot/parrot.txt' tel que
    '/home/luiggi.vercotti/dead/parrot/parrot.txt'
    """
    local_fname = os.path.join(local_dir, remote_file)
    if create_dir:
      self.create_local_dirs(remote_file, local_dir)
    logging.debug(f"[+] Downloading file: {remote_file}")
    logging.debug(f" '-> {local_fname}")
    try:
      self.remote.retrbinary(f"RETR {remote_file}",
                             open(local_fname, 'wb').write)
    except Exception as err:
      err_msg = f"[{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err

  def put_file(self, local_file, remote_dir='/', create_dir=False):
    """
    Depose le fichier local 'local_file' sur le serveur distant dans le repertoire 'remote_dir'.
    Si 'create_dir' est positionnee a True alors l'arborescence de 'remote_dir' sera recree sur le serveur distant.

    ex: put_file(local_file='/home/luiggi.vercotti/dead/parrot/parrot.txt',
                 remote_dir='/spannish/inquisition',
                 create_dir=True)
    crééra l'arborescence distante: '/spannish/inquisition'
    et déposera le fichier distant:  '/spannish/inquisition/parrot.txt'
    """
    if remote_dir[0] == "/":
      remote_dir = remote_dir[1:]
    remote_file = os.path.basename(local_file)
    remote_fname = os.path.join(remote_dir, remote_file)
    if create_dir:
      self.create_remote_dirs(remote_dir=remote_dir)
      remote_fname = os.path.join(remote_dir, remote_file)
    logging.debug(f"[+] Uploading file: {remote_file}")
    logging.debug(f" '-> {remote_fname}")
    try:
      self.remote.storbinary(f"STOR {remote_fname}", open(local_file, "rb"))
    except Exception as err:
      err_msg = f"Error while transferring file: [{err.__class__.__name__}]: {err}"
      logging.critical(err_msg)
      raise ScrippyRemoteError(err_msg) from err

  def create_local_dirs(self, remote_file, local_dir):
    """
    Creation de l'arborescence de 'remote_file' dans le repertoire 'local_dir'.
    La derniere composante de 'remote_file' est consideree comme un fichier.

    ex: create_local_dirs('/dead/parrot/dead_parrot.txt', '/home/luiggi.vercotti')
    créera l'arborescence locale: '/home/luiggi.vercotti/dead/parrot/'.
    """
    hierarchy = os.path.join(*remote_file.split('/')[:-1])
    hierarchy = os.path.join(local_dir, hierarchy)
    logging.debug("[+] Local file hierarchy creation:")
    logging.debug(f" '-> {hierarchy}")
    try:
      os.makedirs(hierarchy, exist_ok=True)
    except Exception as err:
      err_msg = f"[{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err

  def create_remote_dirs(self, remote_dir):
    """
    Creation de l'arborescence 'remote_dirs' sur l'hote distant.
    """
    hierarchy = remote_dir.split('/')
    logging.debug("[+] Remote file hierarchy creation:")
    r_dir = ""
    for component in hierarchy:
      r_dir = os.path.join(r_dir, component)
      logging.debug(f" '-> {r_dir}")
      try:
        self.remote.mkd(r_dir)
      except Exception as err:
        err_msg = f"[{err.__class__.__name__}] {err}"
        logging.critical(f" '-> {err_msg}")
        raise ScrippyRemoteError(err_msg) from err

  def delete_remote_file(self, remote_file):
    """Supprime le fichier distant dont le chemin complet est passe en argument."""
    try:
      self.remote.delete(remote_file)
    except Exception as err:
      err_msg = f"[{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err

  def delete_remote_dir(self, remote_dir):
    """Supprime le repertoire distant dont le chemin complet est passe en argument."""
    try:
      self.remote.rmd(remote_dir)
    except Exception as err:
      err_msg = f"[{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err

  def list(self, remote_dir, file_type='f', pattern='.*'):
    """
    Renvoie la liste des fichiers presents dans le repertoire remote_dir.

    L'argument file_type permet de selectionner le type de fichier liste (f=file (valeur par defaut), d=directory).
    """
    content = []
    logging.debug(f"[+] Getting remote content from folder: {remote_dir}")
    try:
      self.remote.retrlines(f"LIST {remote_dir}", content.append)
      if file_type == 'f':
        reg = re.compile("^-.*")
      elif file_type == 'd':
        reg = re.compile("^d.*")
      content = [os.path.join(remote_dir, f.split()[-1]) for f in content if re.match(reg, f)]
      reg = re.compile(pattern)
      return [f.split()[-1] for f in content if re.match(reg, f)]
    except Exception as err:
      err_msg = f"[{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err
