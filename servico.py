class Missao:
    def __init__(self, ad_de_partida, ad_de_chegada, niv_de_voo, radial_rumo, alt_transicao, niv_transicao,
                 min_en_alt, min_sec_alt, aeronave, waypoint, estima, start,
                 descolagem, aterragem, corte, hora_bloco, hora_de_voo):
        self.ad_de_partida = ad_de_partida
        self.ad_de_chegada = ad_de_chegada
        self.niv_de_voo = niv_de_voo
        self.radial_rumo = radial_rumo
        self.alt_transicao = alt_transicao
        self.niv_transicao = niv_transicao
        self.min_en_alt = min_en_alt
        self.min_sec_alt = min_sec_alt
        self.aeronave = aeronave
        self.waypoint = waypoint
        self.estima = estima
        self.start = start
        self.descolagem = descolagem
        self.aterragem = aterragem
        self.corte = corte
        self.hora_bloco = hora_bloco
        self.hora_de_voo = hora_de_voo

    @property
    def ad_de_partida(self):
        return self._ad_de_partida

    @property
    def ad_de_chegada(self):
        return self._ad_de_chegada

    @property
    def niv_de_voo(self):
        return self._niv_de_voo

    @property
    def radial_rumo(self):
        return self._radial_rumo

    @property
    def alt_transicao(self):
        return self._alt_transicao

    @property
    def niv_transicao(self):
        return self._niv_transicao

    @property
    def min_en_alt(self):
        return self._min_en_alt

    @property
    def min_sec_alt(self):
        return self._min_sec_alt

    @property
    def aeronave(self):
        return self._aeronave

    @property
    def waypoint(self):
        return self._waypoint

    @property
    def estima(self):
        return self._estima

    @property
    def start(self):
        return self._start

    @property
    def descolagem(self):
        return self._descolagem

    @property
    def aterragem(self):
        return self._aterragem

    @property
    def corte(self):
        return self._corte

    @property
    def hora_bloco(self):
        return self._hora_bloco

    @property
    def hora_de_voo(self):
        return self._hora_de_voo

    @ad_de_partida.setter
    def ad_de_partida(self, item):
        self._ad_de_partida = item

    @ad_de_chegada.setter
    def ad_de_chegada(self, item):
        self._ad_de_chegada = item

    @niv_de_voo.setter
    def niv_de_voo(self, item):
        self._niv_de_voo = item

    @radial_rumo.setter
    def radial_rumo(self, item):
        self._radial_rumo = item

    @alt_transicao.setter
    def alt_transicao(self, item):
        self._alt_transicao = item

    @niv_transicao.setter
    def niv_transicao(self, item):
        self._niv_transicao = item

    @min_en_alt.setter
    def min_en_alt(self, item):
        self._min_en_alt = item

    @min_sec_alt.setter
    def min_sec_alt(self, item):
        self._min_sec_alt = item

    @aeronave.setter
    def aeronave(self, item):
        self._aeronave = item

    @waypoint.setter
    def waypoint(self, item):
        self._waypoint = item

    @estima.setter
    def estima(self, item):
        self._estima = item

    @start.setter
    def start(self, item):
        self._start = item

    @descolagem.setter
    def descolagem(self, item):
        self._descolagem = item

    @aterragem.setter
    def aterragem(self, item):
        self._aterragem = item

    @corte.setter
    def corte(self, item):
        self._corte = item

    @hora_bloco.setter
    def hora_bloco(self, item):
        self._hora_bloco = item

    @hora_de_voo.setter
    def hora_de_voo(self, item):
        self._hora_de_voo = item
