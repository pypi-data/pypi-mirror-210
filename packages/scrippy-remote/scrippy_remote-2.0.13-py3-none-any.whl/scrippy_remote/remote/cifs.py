"""Le module scrippy_remote.remote.cifs implémente la partie cliente du protocole CIFS sous forme de la classe Cifs."""
import socket
import logging
import tempfile
from smb.SMBConnection import SMBConnection


class Cifs:

  def __init__(self, hostname, shared_folder, username, password, port=445, use_ntlm_v2=True, is_direct_tcp=True):
    """Initialise le client CIFS."""
    logging.debug("[+] Connection initialization:")
    self.username = username
    self.hostname = hostname
    self.port = port
    self.shared_folder = shared_folder

    self.connection = SMBConnection(username=username,
                                    password=password,
                                    my_name=socket.gethostname(),
                                    remote_name=hostname,
                                    use_ntlm_v2=use_ntlm_v2,
                                    is_direct_tcp=is_direct_tcp)

  def __enter__(self):
    """Point d'entrée."""
    logging.debug("[+] Connecting to {}@{}:{}".format(self.username, self.hostname, self.port))
    self.connection.connect(self.hostname, self.port)
    return self

  def __exit__(self, type_err, value, traceback):
    """Point de sortie."""
    del type_err, value, traceback
    logging.debug("[+] Closing connection to {}@{}".format(self.username, self.hostname))
    self.connection.close()

  def create_directory(self, path):
    logging.debug("[+] Creating folder {}".format(path))
    self.connection.createDirectory(self.shared_folder, path)

  def get_file(self, remote_filepath, local_filepath):
    logging.debug("[+] Downloading file {} in {}".format(remote_filepath, local_filepath))
    with open(local_filepath, 'wb') as file_obj:
      self.connection.retrieveFile(self.shared_folder, remote_filepath, file_obj)

  def put_file(self, local_filepath, remote_filepath):
    logging.debug("[+] Uploading file {} to {}".format(local_filepath, remote_filepath))
    with open(local_filepath, 'rb') as file_obj:
      self.connection.storeFile(self.shared_folder, remote_filepath, file_obj)

  def delete_directory_content(self, path):
    logging.debug("[+] Deleting all content at path '{}'".format(path))
    entries = self.connection.listPath(self.shared_folder, path)
    for entry in entries:
      if entry.filename not in (".", ".."):
        if entry.isDirectory:
          self.delete_directory_content(path + '/' + entry.filename)
          logging.debug("[+] Delete directory {}".format(path + '/' + entry.filename))
          self.connection.deleteDirectory(self.shared_folder, path + '/' + entry.filename)
        else:
          logging.debug("[+] Delete file {}".format(path + '/' + entry.filename))
          self.connection.deleteFiles(self.shared_folder, path + '/' + entry.filename)

  def open_for_write(self, file):
    return _CifsFileWritter(self.connection, self.shared_folder, file)

  def open_for_read(self, file):
    file_obj = tempfile.TemporaryFile()
    self.connection.retrieveFile(self.shared_folder, file, file_obj)
    file_obj.seek(0)
    return file_obj


class _CifsFileWritter:
  def __init__(self, connection, shared_folder, file_path):
    self.connection = connection
    self.shared_folder = shared_folder
    self.file_path = file_path
    self.file_obj = tempfile.TemporaryFile()

  def __enter__(self):
    self.file_obj.__enter__()
    return self.file_obj

  def __exit__(self, type_err, value, traceback):
    if type_err is None:
      self.write_file()
    self.file_obj.__exit__(type_err, value, traceback)

  def write_file(self):
    logging.debug("[+] Writing file {}".format(self.file_path))
    self.file_obj.seek(0)
    self.connection.storeFile(self.shared_folder, self.file_path, self.file_obj)
