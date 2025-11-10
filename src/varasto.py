class Varasto:

    def __init__(self, tilavuus, alku_saldo=0.0):
        self.tilavuus = tilavuus if tilavuus > 0 else 0.0
        self.saldo = self._alkusaldo(alku_saldo)

    def _alkusaldo(self, alku_saldo):
        if alku_saldo < 0:
            return 0.0
        if alku_saldo > self.tilavuus:
            return self.tilavuus
        return alku_saldo

    def paljonko_mahtuu(self):
        return self.tilavuus - self.saldo

    def lisaa_varastoon(self, maara):
        if maara < 0:
            return
        self.saldo = min(self.tilavuus, self.saldo + maara)

    def ota_varastosta(self, maara):
        if maara < 0:
            return 0.0
        otettava = min(maara, self.saldo)
        self.saldo -= otettava
        return otettava

    def __str__(self):
        return (
            f"saldo = {self.saldo}, "
            f"vielä tilaa {self.paljonko_mahtuu()}"
        )
