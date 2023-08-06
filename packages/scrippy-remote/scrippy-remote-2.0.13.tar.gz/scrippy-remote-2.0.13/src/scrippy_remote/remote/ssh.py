"""Le module scrippy_remote.remote.ssh implémente la partie cliente du protocole SSH/SFTP sous forme de la classe Ssh."""
import os
import re
import stat
import socket
import logging
import paramiko
from time import sleep
from scrippy_remote import ScrippyRemoteError


def clean_path(path):
  """
  Supprime les éventuels / finaux de path.

  :param path: path à nettoyer
  :return: renvoie path sans le '/' final si présents
  """
  if path[-1:] == "/":
    path = path[:-1]
  return path


def _log_line(line, log_content, log_level):
  if log_content:
    logging.log(log_level, f" '-> {line}")


class Ssh:
  """
  La classe principale permettant la manipulation des hôtes distants via SSH.

  Cette classe permet
  - L'exécution de commandes distantes
  - Le transfert de fichier
  """

  def __init__(self, username, hostname, port=22,
               password=None, key_filename=None):
    """Initialise le client SSH."""
    if not logging.getLogger().level == logging.DEBUG:
      logging.getLogger("paramiko").setLevel(logging.ERROR)
    self.username = username
    self.hostname = hostname
    self.port = port
    self.key_filename = key_filename
    self.password = password
    self.remote = None

  def __enter__(self):
    """Point d'entrée."""
    self.connect()
    return self

  def __exit__(self, type_err, value, traceback):
    """Point de sortie."""
    del type_err, value, traceback
    self.close()

  def connect(self):
    """
    Se connecte à un hôte distant.

    Le chemin vers une clef publique SSH alternative peut être passée à la fonction via l'option key_filename.
    Dans tous les cas le répertoire ~/.ssh de l'utilisateur courant est parcouru afin de trouver le clef SSH adaptée.

    Une erreur est levée et False retourné dans au moins les cas suivants:
    - La clef de l'hôte distant ne se trouve pas dans le fichier ~/.ssh/known_hosts de l'utilisateur courant
    - La clef de l'hôte distant diffère de celle enregistrée dans le fichier ~/.ssh/known_hosts de l'utilisateur courant
    - L'authentification de l'utilisateur a échoué
    - L'hôte distant est injoignable/inconnu
    - La clef SSH n'a pas été trouvée
    - ...
    """
    logging.debug(f"[+] Connecting to {self.username}@{self.hostname}:{self.port}")
    try:
      self.remote = paramiko.SSHClient()
      self.remote.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.remote.load_system_host_keys()
      if self.key_filename:
        logging.debug(f"Using key: {self.key_filename}")
        pkey = paramiko.RSAKey.from_private_key_file(self.key_filename, password=self.password)
        logging.debug("Connection")
        self.remote.connect(hostname=self.hostname,
                            port=self.port,
                            username=self.username,
                            pkey=pkey)
      elif self.password:
        logging.debug(f"Using password: {self.password}")
        self.remote.connect(hostname=self.hostname,
                            port=self.port,
                            username=self.username,
                            password=self.password,
                            allow_agent=False,
                            look_for_keys=False)
      else:
        logging.debug("Using default SSH key")
        self.remote.connect(hostname=self.hostname,
                            port=self.port,
                            username=self.username)
    except paramiko.BadHostKeyException as err:
      err_msg = f"Bad SSH Host Key : [{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err
    except paramiko.AuthenticationException as err:
      err_msg = f"Failed to authenticate: [{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err
    except (paramiko.SSHException,
            socket.gaierror,
            paramiko.ssh_exception.NoValidConnectionsError,
            FileNotFoundError) as err:
      err_msg = f"Connection error: [{err.__class__.__name__}] {err}"
      logging.critical(f" '-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err
    except Exception as err:
      err_msg = f"Unexpected error: [{err.__class__.__name__}] {err}"
      logging.critical(f" +-> {err_msg}")
      raise ScrippyRemoteError(err_msg) from err

  def close(self):
    """ Ferme la connexion passée en argument. """
    logging.debug(f"[+] Closing connection to {self.username}@{self.hostname}")
    if self.remote:
      self.remote.close()

  def exec_command(self, command, return_stdout=False, log_stdout=True, log_stderr=True, strip_stdout=True, strip_stderr=True, **kwargs):
    """
    Exécute une commande sur l'hôte distant et retourne l'exit_code.

    Cette méthode accepte l'ensemble des arguments de http://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.exec_command

    :param bool return_stdout: add list of stdout lines in the returned dict (default ``False``).
    :param bool log_stdout: log stdout in logging Info (default ``True``).
    :param bool log_stderr: log stdout in logging Error (default ``True``).
    :param bool strip_stdout: supprime les caractères blancs (espaces, tabulations, etc) de chacune des lignes de la sortie standard renvoyée par la commande. (default ``True``).
    :param bool strip_stderr: supprime les caractères blancs (espaces, tabulations, etc) de chacune des lignes de l'erreur standard renvoyée par la commande. (default ``True``).

    :return:
        a dict containing ``exit_code`` of the executing command (ex: ``{ "exit_code": 0 }``)
        if return_stdout == True add a key ``stdout`` containing stdout lines as a list of line

    :raises: `SystemExit` -- if the server fails to execute the command
    """
    logging.debug(f"[+] Running command: {command}")
    try:
      exit_code = None
      stdin, stdout, stderr = self.remote.exec_command(command, **kwargs)
      channel = stdout.channel
      stdout_content = []
      while True:
        sleep(0.1)
        while channel.recv_ready():
          line = stdout.readline()
          if strip_stdout:
            line = line.strip()
          _log_line(line, log_stdout, logging.DEBUG)
          if return_stdout:
            stdout_content.append(line)
        while channel.recv_stderr_ready():
          line = stderr.readline()
          if strip_stderr:
            line = line.strip()
          _log_line(line, log_stderr, logging.ERROR)
        if channel.exit_status_ready():
          logging.debug(" '-> exit_status_ready !")
          # Read last lines
          for line in stdout:
            if strip_stdout:
              line = line.strip()
            _log_line(line, log_stdout, logging.DEBUG)
            if return_stdout:
              stdout_content.append(line)
          for line in stderr:
            if strip_stderr:
              line = line.strip()
            _log_line(line, log_stderr, logging.ERROR)
          exit_code = channel.recv_exit_status()
          break
      res = {'exit_code': exit_code}
      if return_stdout:
        res['stdout'] = stdout_content
      return res
    except paramiko.SSHException as err:
      err_msg = f"Error while running command: [{err.__class__.__name__}] {err}"
      logging.critical(err_msg)
      raise ScrippyRemoteError(err_msg) from err

# -- OPEN ----------------------------------------------------------------------

  def open_for_read(self, file):
    sftp = self.remote.open_sftp()
    return sftp.open(file, mode='r')

  def open_for_write(self, file):
    sftp = self.remote.open_sftp()
    return sftp.open(file, mode='w')

# -- PUT -----------------------------------------------------------------------

  def sftp_put(self, local_path, remote_path, pattern='.*', recursive=True, delete=False, exit_on_error=True):
    """
    Envoie les fichiers à l'hôte distant.

    local_path et remote_path doivent être des répertoires.

    Le paramètre pattern permet de définir un motif à rechercher dans les noms des fichiers. Le motif est recherché sur le nom de fichier seul.

    Si recursive est positionnée à True (défaut=True) alors le motif défini par le paramètre pattern est recherché sur l'ensemble des noms des fichiers contenus par le répertoire défini par local_path. Les fichiers dont le noms correspond au motif sont alors transférés dans le répertoire défini par remote_path.

    Si delete est positionnée à True (défaut=False), les fichiers locaux seront supprimés une fois que tous les fichiers auront été transférés sur l'hôte distant.

    Si une erreur est levée pendant le transfert alors les fichiers locaux ne sont pas supprimés y compris si exit_on_error est positionnée à False.

    Si le paramètre optionnel exit_on_error est positionné à True (défaut=True):
    - Le transfert s'interrompt à la première erreur
    - La suppression des fichiers locaux s'interrompt à la première erreur
    - La fonction retourne le nombre d'erreurs constatées lors du traitement du lot.
    Dans le cas contraire (exit_on_error=False):
    - L'erreur est signalée sur le log mais le traitement du lot n'est pas interrompu.
    - La fonction retourne le nombre d'erreurs constatées lors du traitement du lot.
    """
    # On supprime les éventuels / finaux de local_path et remote_path
    local_path = clean_path(local_path)
    remote_path = clean_path(remote_path)
    num_err = 0
    try:
      files = self.find_local_files(local_path, pattern, recursive)
      num_err = self.transfer_local_files(files, remote_path, exit_on_error)
      if num_err == 0 and delete:
        self.delete_local_files(files, exit_on_error)
      elif delete:
        logging.error(f"[+] Encountered errors: {num_err}")
        logging.error(" '-> File deletion aborted")
      return num_err
    except Exception as err:
      msg = "Unrecoverable error"
      if exit_on_error:
        msg = "exit_on_error is set to True"
      logging.error(f"[{err.__class__.__name__}] {err}: Stopping execution")
      logging.error(f" '-> {msg}: Stopping execution")
      if num_err == 0:
        num_err += 1
      return num_err

  def find_local_files(self, local_path, pattern, recursive):
    logging.debug("[+] Getting local files list")
    logging.debug(f" '-> Local folder: {local_path}")
    logging.debug(f" '-> Pattern: {pattern}")
    regex = re.compile(pattern)
    local_files = []
    local_dirs = []
    for fname in os.listdir(local_path):
      fname = os.path.join(local_path, fname)
      if os.path.isdir(fname):
        local_dirs.append(fname)
      else:
        if regex.match(fname) is not None:
          logging.debug(f" '-> {fname}")
          local_files.append(fname)
    if recursive:
      for ldir in local_dirs:
        local_files += self.find_local_files(ldir, pattern, recursive)
    return local_files

  def transfer_local_files(self, local_files, remote_path, exit_on_error):
    num_err = 0
    sftp = self.remote.open_sftp()
    logging.debug(f"[+] File transfert to {self.username}@{self.hostname}:{self.port}:{remote_path}")
    if len(local_files) == 0:
      logging.debug(" '-> No file found")
    for local_file in local_files:
      logging.debug(f" '-> {local_file}")
      remote_fname = os.path.join(remote_path, os.path.basename(local_file))
      try:
        sftp.put(local_file, remote_fname, confirm=True)
      except Exception as err:
        num_err += 1
        logging.warning(f"  '-> [{err.__class__.__name__}] {err}")
        if exit_on_error:
          err_msg = "Transfert error and exit_on_error is set to True: Immediate abortion."
          logging.critical(err_msg)
          raise ScrippyRemoteError(err_msg) from err
    return num_err

  def delete_local_files(self, local_files, exit_on_error):
    num_err = 0
    logging.debug("[+] Local files deletion")
    if len(local_files) == 0:
      logging.debug(" '-> No file found")
    for local_file in local_files:
      logging.debug(f" '-> {local_file}")
      try:
        os.remove(local_file)
      except Exception as err:
        num_err += 1
        logging.warning(f"  '-> [{err.__class__.__name__}] {err}")
        if exit_on_error:
          err_msg = "Error while deleting and exit_on_error is set to True: Immediate abortion."
          logging.critical(err_msg)
          raise ScrippyRemoteError(err_msg) from err
    return num_err

# -- GET -----------------------------------------------------------------------
  def sftp_get(self, remote_path, local_path, pattern='.*', recursive=True, delete=False, exit_on_error=True):
    """
    Récupère les fichiers depuis l'hôte distant.
    local_path et remote_path doivent être des répertoires.

    Le paramètre pattern permet de définir un motif à rechercher dans les noms des fichiers. Le motif est recherché sur le nom de fichier seul.

    Si recursive est positionnée à True (défaut=True) alors le motif défini par le paramètre pattern est recherché sur l'ensemble des noms des fichiers contenus par le répertoire défini par remote_path. Les fichiers dont le noms correspond au motif sont alors transférés dans le répertoire défini par local_path.

    Si delete est positionnée à True (défaut=False), les fichiers distants seront supprimés une fois que tous les fichiers auront été transférés sur l'hôte local.

    Si une erreur de transfert est levée pendant le transfert alors les fichiers locaux ne sont pas supprimés y compris si exit_on_error est positionnée à False.

    Si le paramètre optionnel exit_on_error est positionné à True (défaut=True):
    - Le transfert s'interrompt à la première erreur
    - La suppression des fichiers locaux s'interrompt à la première erreur
    - La fonction retourne le nombre d'erreurs constatées lors du traitement du lot.
    Dans le cas contraire (exit_on_error=False):
    - L'erreur est signalée sur le log mais le traitement du lot n'est pas intérrompu.
    - La fonction retourne le nombre d'erreurs constatées lors du traitement du lot.
    """
    err = 0
    local_path = clean_path(local_path)
    remote_path = clean_path(remote_path)
    remote_files = self.find_remote_files(remote_path,
                                          pattern,
                                          recursive,
                                          exit_on_error)
    err += self.transfer_remote_files(local_path,
                                      remote_files,
                                      exit_on_error)
    if delete and err == 0:
      err += self.delete_remote_files(remote_files, exit_on_error)
    elif delete:
      logging.error(f"[+] Encountered errors: {err}")
      logging.error(" '-> File deletion aborted")
    return err

  def find_remote_files(self, remote_path, pattern, recursive, exit_on_error, sftp=None):
    if sftp is None:
      sftp = self.remote.open_sftp()

    logging.debug("[+] Getting remote files list")
    logging.debug(f" '-> Remote folder: {remote_path}")
    logging.debug(f" '-> Pattern: {pattern}")
    regex = re.compile(pattern)
    remote_files = []
    remote_dirs = []
    try:
      for f in sftp.listdir_attr(remote_path):
        fname = os.path.join(remote_path, f.filename)
        if stat.S_ISDIR(f.st_mode):
          remote_dirs.append(fname)
        else:
          if regex.match(fname) is not None:
            logging.debug(f" '-> {fname}")
            remote_files.append(fname)
      if recursive:
        for directory in remote_dirs:
          remote_files += self.find_remote_files(directory, pattern, recursive, exit_on_error, sftp)
    except Exception as err:
      err_msg = f"Error while getting file list: [{err.__class__.__name__}] {err}"
      logging.warning(err_msg)
      if exit_on_error:
        err_msg = "Error while getting file list and exit_on_error set to True: Immediate abortion."
        logging.critical(err_msg)
        raise ScrippyRemoteError(err_msg) from err
    return remote_files

  def transfer_remote_files(self, local_path, remote_files, exit_on_error):
    num_err = 0
    sftp = self.remote.open_sftp()
    logging.debug(f"[+] File transfert from {self.username}@{self.hostname}:{self.port}")
    if len(remote_files) == 0:
      logging.debug(" '-> No file found")
    for remote_file in remote_files:
      local_fname = os.path.basename(remote_file)
      local_fname = os.path.join(local_path, local_fname)
      logging.debug(f" '-> {remote_file}")
      logging.debug(f" '-> {local_fname}")
      try:
        sftp.get(remote_file, local_fname)
      except Exception as err:
        num_err += 1
        err_msg = f"[{err.__class__.__name__}] {err}"
        logging.warning(err_msg)
        if exit_on_error:
          err_msg = "Error while transfering and exit_on_error set to True: Immediate abortion."
          logging.critical(err_msg)
          raise ScrippyRemoteError(err_msg) from err
    return num_err

  def delete_remote_files(self, remote_files, exit_on_error):
    num_err = 0
    sftp = self.remote.open_sftp()
    logging.debug("[+] Remote files deletion")
    if len(remote_files) == 0:
      logging.debug(" '-> No file found")
    for remote_file in remote_files:
      try:
        logging.debug(f" '-> {remote_file}")
        sftp.remove(remote_file)
      except Exception as err:
        num_err += 1
        err_msg = f"[{err.__class__.__name__}] {err}"
        logging.warning(err_msg)
        if exit_on_error:
          err_msg = "Error while deleting and exit_on_error set to True: Immediate abortion."
          logging.critical(err_msg)
          raise ScrippyRemoteError(err_msg) from err
    return num_err

# -- DELETE --------------------------------------------------------------------
  def sftp_delete(self, remote_path, pattern, recursive, exit_on_error):
    remote_files = self.find_remote_files(remote_path,
                                          pattern,
                                          recursive,
                                          exit_on_error)
    return self.delete_remote_files(remote_files, exit_on_error)

# -- LIST ----------------------------------------------------------------------
  def sftp_list(self, remote_path, pattern, recursive, exit_on_error):
    return self.find_remote_files(remote_path,
                                  pattern,
                                  recursive,
                                  exit_on_error)

# -- STAT ----------------------------------------------------------------------
  def sftp_stat(self, remote_path, pattern, recursive, exit_on_error):
    """
    Retourne un dict {'file_path': stat}
    Voir http://docs.paramiko.org/en/stable/api/sftp.html#paramiko.sftp_client.SFTPClient.stat
    """
    remote_files_stats = {}
    remote_files = self.sftp_list(remote_path,
                                  pattern,
                                  recursive,
                                  exit_on_error)
    sftp = self.remote.open_sftp()
    for file_name in remote_files:
      file_stat = sftp.stat(file_name)
      remote_files_stats[file_name] = file_stat
    return remote_files_stats

  def sftp_file_exist(self, remote_filename):
    sftp = self.remote.open_sftp()
    try:
      if stat.S_ISDIR(sftp.stat(remote_filename).st_mode):
        raise ScrippyRemoteError(f"{remote_filename} exists and is a directory")
      return True
    except IOError:
      return False

# -- UTIL ----------------------------------------------------------------------
  def sftp_mkdir_p(self, remote_path):
    """
    Créé sur l'hôte distant l'arborescence de répertoires correspondant à remote_path.
    Cette méthode est récursive et, en plus du chemin à créer, à besoin de la connexion sftp en argument.
    """
    sftp = self.remote.open_sftp()
    if remote_path == '':
      remote_path = './'
    try:
      sftp.chdir(remote_path)
    except IOError:
      dirname, basename = os.path.split(remote_path.rstrip('/'))
      self.sftp_mkdir_p(dirname)
      sftp.mkdir(basename)
      sftp.chdir(basename)
    except Exception as err:
      err_msg = f"[{err.__class__.__name__}] {err}"
      logging.error(err_msg)
      raise ScrippyRemoteError(err_msg) from err
    return True
