
class Actions(object):
    HOME = 1
    NEUBLOC = 2

    ext = {
        'OS': 'Start from Neubloc',
        'OK': 'End from Neubloc',
        'DS': 'Start from home',
        'DK': 'End from home',
    }

    @staticmethod
    def get(client):
        if client == Actions.HOME:
            return { 'start': 'Start dom', 
                     'stop': 'Koniec dom' }       

        elif client == Actions.NEUBLOC:
            return { 'start': 'Start Neubloc', 
                     'stop': 'Koniec Neubloc' } 
        else:
            raise "Client error"

