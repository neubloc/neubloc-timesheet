import gnomekeyring as gk


class Keyring(object):

    ring = ''

    def __init__(self, keyring_plain_password = ''):
        self.ring = gk.get_default_keyring_sync()
        gk.unlock_sync(None, keyring_plain_password);


    def set(self, key, password):
        gk.item_create_sync(self.ring, gk.ITEM_GENERIC_SECRET, key, {}, password, True)

    def get(self, key):
        password = None

        for id in gk.list_item_ids_sync(self.ring):
            item = gk.item_get_info_sync(self.ring, id)
            if item.get_display_name() == key:
                password = item.get_secret()

        if not password:
            raise "Cant find password in keyring"

        return password
