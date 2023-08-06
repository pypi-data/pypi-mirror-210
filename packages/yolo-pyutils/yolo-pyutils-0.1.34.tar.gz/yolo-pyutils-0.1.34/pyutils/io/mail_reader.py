from imapclient import IMAPClient


class MailReader:

    def __init__(self, imap_server, imap_port, user, pwd, charset='UTF-8', ssl=True):
        self.__imap_server = imap_server
        self.__imap_port = imap_port
        self.__user = user
        self.__pwd = pwd
        self.__charset = charset
        self.__ssl = ssl
        self.__client = None

    def start(self):
        self.__client = IMAPClient(self.__imap_server, ssl=self.__ssl, port=self.__imap_port)
        self.__client.login(self.__user, self.__pwd)
        self.__client.id_({"name": "IMAPClient", "version": "2.1.0"})

    def stop(self):
        self.__client.logout()

    # return mails and error if exception occurred
    def get_mails(self, folder, criteria, search_key_alias):
        mails = list()
        err = None
        try:
            self.__client.select_folder(folder)
            messages = self.__client.search(criteria=criteria, charset=self.__charset)
            if len(messages) > 0:
                for mail_id, data in self.__client.fetch(messages, search_key_alias.keys()).items():
                    mail = dict()
                    for key, alias in search_key_alias.items():
                        mail[alias] = data[bytes(key, self.__charset)].decode(self.__charset)
                    mails.append(mail)
        except Exception as ex:
            err = ex
        return mails, err
