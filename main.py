from kivy.app import App
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.image import Image
from datetime import datetime
from kivy.metrics import dp
import datetime as dt
from kivymd.theming import ThemeManager
import sqlite3
from kivy.utils import platform
import platform


# ==========================================================
# MENSAGENS DA APLICAÇÃO
# Compatível com Windows e Android
# ==========================================================
def mostrar_mensagem(mensagem, duration=3):

    # ======================================================
    # ANDROID
    # ======================================================
    if platform == "android":
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass

            Toast = autoclass("android.widget.Toast")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            if duration >= 4:
                duracao_android = Toast.LENGTH_LONG
            else:
                duracao_android = Toast.LENGTH_SHORT

            @run_on_ui_thread
            def apresentar_toast():
                Toast.makeText(
                    activity,
                    str(mensagem),
                    duracao_android
                ).show()

            apresentar_toast()
            return


        except Exception as erro:

            print("ERRO TOAST ANDROID:", repr(erro))

    # ======================================================
    # WINDOWS / DESKTOP
    # ======================================================
    try:
        from kivymd.toast import toast
        toast(str(mensagem), duration=duration)
    except Exception as erro:
        print("Erro ao apresentar mensagem:", erro)

# ==========================================================
# BASE DE DADOS
# ==========================================================
class BaseDeDados:
    def __init__(self):
        self.conn = sqlite3.connect("missoes.db", check_same_thread=False, timeout=30)
        self.cursor = self.conn.cursor()

    # ======================================================
    # CRIA TABELA DE VOOS
    # ======================================================
    def tbl_voo(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS voos(
                IDVOO INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_de_partida TEXT,
                ad_de_chegada TEXT,
                nivel_de_voo TEXT,
                radial_rumo TEXT,
                altitude_de_transicao TEXT,
                nivel_de_transicao TEXT,
                mea TEXT,
                msa TEXT,
                aeronave TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    # ======================================================
    # INSERE NOVO VOO
    # ======================================================
    def inserir_tbl_voo(self, partida, destino, nivelDeVoo, radialRumo,
                         altitudeDETransicao, nivelDeTransicao, mea, msa,
                         aeronave, data):
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            INSERT INTO voos (
                ad_de_partida,
                ad_de_chegada,
                nivel_de_voo,
                radial_rumo,
                altitude_de_transicao,
                nivel_de_transicao,
                mea,
                msa,
                aeronave,
                data
            )
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (partida, destino, nivelDeVoo, radialRumo, altitudeDETransicao,
              nivelDeTransicao, mea, msa, aeronave, data))

        self.conn.commit()
        id_voo = self.cursor.lastrowid
        self.cursor.close()
        return id_voo

    # ======================================================
    # SELECIONA TODOS OS VOOS
    # ======================================================
    def selecionar_todos_tbl_voo(self):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                SELECT
                    voos.IDVOO,
                    voos.ad_de_partida,
                    voos.ad_de_chegada,
                    voos.nivel_de_voo,
                    voos.radial_rumo,
                    voos.altitude_de_transicao,
                    voos.nivel_de_transicao,
                    voos.mea,
                    voos.msa,
                    voos.aeronave,
                    voos.data,
                    GROUP_CONCAT(estimas.waypoint_nome || ':' || estimas.waypoint_tempo, ' | ' ORDER BY estimas.IDESTIMAS) AS waypoints
                FROM voos
                LEFT JOIN estimas ON voos.IDVOO = estimas.id_voo
                GROUP BY voos.IDVOO
            """)
            self.linhas = self.cursor.fetchall()

        except Exception as erro:
            print("Erro ao selecionar voos:", erro)
            self.linhas = []
            mostrar_mensagem("Sem voos na lista", duration=5)
            return self.linhas
        finally:
            self.cursor.close()
        return self.linhas

    # ======================================================
    # SELECIONA UM VOO ESPECÍFICO
    # ======================================================
    def selecionar_det_tbl_voo(self, entrada):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                SELECT
                    voos.IDVOO,
                    voos.ad_de_partida,
                    voos.ad_de_chegada,
                    voos.nivel_de_voo,
                    voos.radial_rumo,
                    voos.altitude_de_transicao,
                    voos.nivel_de_transicao,
                    voos.mea,
                    voos.msa,
                    voos.aeronave,
                    voos.data,
                    GROUP_CONCAT(estimas.waypoint_nome || ':' || estimas.waypoint_tempo, ' | ' ORDER BY estimas.IDESTIMAS) AS waypoints
                FROM voos
                LEFT JOIN estimas ON voos.IDVOO = estimas.id_voo
                WHERE ad_de_partida=? OR ad_de_chegada=? OR aeronave=?
                GROUP BY voos.IDVOO
            """, (entrada, entrada, entrada))

            self.linhas = self.cursor.fetchall()
            if self.linhas:
                mostrar_mensagem("Voo encontrado com sucesso", duration=5)
                for linha in self.linhas:
                    print(linha)
            else:
                mostrar_mensagem("Voo não encontrado", duration=5)
            return self.linhas
        except sqlite3.Error as erro:
            print("Erro ao procurar voo:", erro)
            self.linhas = []
            mostrar_mensagem("Erro ao procurar voo!", duration=5)
            return self.linhas
        finally:
            self.cursor.close()

    # ======================================================
    # ATUALIZA DADOS DO VOO
    # ======================================================
    def actualizar_voo(self, partida, chegada, niv_v, rad, alt_t,
                       niv_t, mea, msa, aeronave, data, id_voo):
        self.cursor = self.conn.cursor()
        try:
            sql = """
                UPDATE voos SET
                    ad_de_partida = ?,
                    ad_de_chegada = ?,
                    nivel_de_voo = ?,
                    radial_rumo = ?,
                    altitude_de_transicao = ?,
                    nivel_de_transicao = ?,
                    mea = ?,
                    msa = ?,
                    aeronave = ?,
                    data = ?
                WHERE IDVOO = ?
            """
            valores = (partida, chegada, niv_v, rad, alt_t, niv_t, mea,
                       msa, aeronave, data, id_voo)
            self.cursor.execute(sql, valores)
            self.conn.commit()
            mostrar_mensagem("Dados atualizados com sucesso!", duration=5)
        except sqlite3.Error as erro:
            print("Erro SQLite:", erro)
            self.conn.rollback()
            mostrar_mensagem("Erro ao atualizar dados!", duration=5)
        finally:
            self.cursor.close()

    # ======================================================
    # CRIA TABELA DAS ESTIMAS
    # ======================================================
    def tbl_estimas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS estimas(
                IDESTIMAS INTEGER PRIMARY KEY AUTOINCREMENT,
                id_voo INTEGER,
                waypoint_nome TEXT,
                waypoint_tempo INTEGER,
                FOREIGN KEY(id_voo) REFERENCES voos(IDVOO)
            )
        """)
        self.conn.commit()

    # ======================================================
    # INSERE WAYPOINTS
    # ======================================================
    def inserir_tbl_estimas(self, waypoints, id_voo):
        self.cursor = self.conn.cursor()
        try:
            for waypoint_nome, tempo in waypoints.items():
                self.cursor.execute("""
                    INSERT INTO estimas
                    (
                        id_voo,
                        waypoint_nome,
                        waypoint_tempo
                    )
                    VALUES (?, ?, ?)
                """, (id_voo, waypoint_nome, tempo))
            self.conn.commit()
        except sqlite3.Error as erro:
            print("Erro ao inserir waypoints:", erro)
            self.conn.rollback()
            mostrar_mensagem("Erro ao inserir waypoints!", duration=5)
        finally:
            self.cursor.close()

    # ======================================================
    # ATUALIZA WAYPOINTS
    # ======================================================
    def actualizar_estimas(self, waypoints, id_voo):
        self.cursor = self.conn.cursor()
        try:
            # --------------------------------------------------
            # Remove estimas antigas
            # --------------------------------------------------
            self.cursor.execute("DELETE FROM estimas WHERE id_voo = ?", (id_voo,))

            # --------------------------------------------------
            # Insere as novas estimas
            # --------------------------------------------------
            if isinstance(waypoints, str) and waypoints and waypoints != "N/A":
                pares = [p.strip() for p in waypoints.split()]
                for par in pares:
                    ultima_posicao = par.rfind(':')
                    if ultima_posicao != -1:
                        waypoint_nome = par[:ultima_posicao].strip()
                        tempo = par[ultima_posicao + 1:].strip()
                        self.cursor.execute("""
                            INSERT INTO estimas
                            (
                                id_voo,
                                waypoint_nome,
                                waypoint_tempo
                            )
                            VALUES (?, ?, ?)
                        """, (id_voo, waypoint_nome, tempo))
            self.conn.commit()
            mostrar_mensagem("Waypoints atualizados com sucesso!", duration=8)
            return True
        except sqlite3.Error as erro:
            print("Erro SQLite:", erro)
            self.conn.rollback()
            mostrar_mensagem("Erro ao atualizar waypoints!", duration=8)
            return False
        finally:
            self.cursor.close()

    # ======================================================
    # SELECIONA ESTIMAS DE UM VOO
    # ======================================================
    def selecionar_estimas_por_voo(self, id_voo):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                SELECT
                    waypoint_nome,
                    waypoint_tempo
                FROM estimas
                WHERE id_voo = ?
                ORDER BY IDESTIMAS
            """, (id_voo,))
            estimas = self.cursor.fetchall()
            return estimas if estimas else []
        except sqlite3.Error as erro:
            print("Erro ao selecionar estimas:", erro)
            mostrar_mensagem("Erro ao selecionar estimas!", duration=5)
            return []
        finally:
            self.cursor.close()

    # ======================================================
    # OBTÉM ID DO ÚLTIMO VOO
    # ======================================================
    def obter_ultimo_id_voo(self):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("SELECT MAX(IDVOO) FROM voos")
            ultimo_id = self.cursor.fetchone()[0]
            return ultimo_id if ultimo_id else 0
        except sqlite3.Error as erro:
            print("Erro ao obter último ID:", erro)
            return 0
        finally:
            self.cursor.close()

    # ======================================================
    # APAGA DADOS
    # ======================================================
    def apagar_dados(self, id_dados):
        self.cursor = self.conn.cursor()
        try:
            # --------------------------------------------------
            # Primeiro apaga as estimas
            # --------------------------------------------------
            self.cursor.execute("DELETE FROM estimas WHERE id_voo = ?", (id_dados,))

            # --------------------------------------------------
            # Depois apaga o voo
            # --------------------------------------------------
            self.cursor.execute("DELETE FROM voos WHERE IDVOO = ?", (id_dados,))
            self.conn.commit()
            mostrar_mensagem("Dados apagados com sucesso!", duration=5)
        except sqlite3.Error as erro:
            print("Erro ao apagar dados:", erro)
            self.conn.rollback()
            mostrar_mensagem("Erro ao apagar dados!", duration=5)
        finally:
            self.cursor.close()

# ==========================================================
# BASE DE DADOS PRINCIPAL
# ==========================================================
# bd = BaseDeDados()

# ==========================================================
# MAIN WINDOW
# ==========================================================
class MainWindow(Screen):

    def on_pre_enter(self):
        Window.bind(on_request_close=self.sair)

    def sair(self, *args, **kwargs):
        self.card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        self.botao = BoxLayout(padding=dp(10), spacing=dp(12), size_hint_y=None, height=dp(55))
        self.pop = Popup(title='Você deseja mesmo sair?', title_color=[0, 1, 0, 1], content=self.card, size_hint=(0.72, 0.42))
        self.imagem = Image(source='alerta1.jpg')
        self.continua = Button(text='Não', size_hint=(0.5, 0.60), on_release=self.pop.dismiss)
        self.botao.add_widget(Button(text='Sim', size_hint=(0.5, 0.60), on_release=MDApp.get_running_app().stop))
        self.botao.add_widget(self.continua)
        self.card.add_widget(self.imagem)
        self.card.add_widget(self.botao)
        self.animar = Animation(size=(360, 210), duration=0.2, t='out_back')
        self.animar.start(self.pop)
        self.pop.open()
        return True

# ==========================================================
# SECOND WINDOW
# Página para inserir os dados do plano de voo
# ==========================================================
class SecondWindow(Screen):
    partida = ObjectProperty(None)
    destino = ObjectProperty(None)
    nivelDeVoo = ObjectProperty(None)
    radialRumo = ObjectProperty(None)
    altitudeDeTransicao = ObjectProperty(None)
    nivelDeTransicao = ObjectProperty(None)
    mea = ObjectProperty(None)
    msa = ObjectProperty(None)
    aeronave = ObjectProperty(None)

    voo = {}
    voa = {}
    id_voo = None

    def avancar(self):
        self.t1 = dt.datetime.now()
        self.data_voo = self.t1.strftime("%d/%m/%y")
        self.ad_partida = self.partida.text
        self.ad_chegada = self.destino.text
        self.voa = {
            'AD/Partida': self.ad_partida.upper(),
            'AD/Chegada': self.ad_chegada.upper(),
            'Nível de voo': self.nivelDeVoo.text,
            'Radial/Rumo': self.radialRumo.text + 'º',
            'Altitude de transição': self.altitudeDeTransicao.text,
            'Nível de transição': self.nivelDeTransicao.text,
            'MEA': self.mea.text,
            'MSA': self.msa.text,
            'Aeronave': self.aeronave.text,
            'waypoints': ''
        }
        self.novo = BaseDeDados()
        self.novo.tbl_voo()

        SecondWindow.id_voo = self.novo.inserir_tbl_voo(
            self.ad_partida.upper(),
            self.ad_chegada.upper(),
            self.nivelDeVoo.text,
            self.radialRumo.text + 'º',
            self.altitudeDeTransicao.text,
            self.nivelDeTransicao.text,
            self.mea.text,
            self.msa.text,
            self.aeronave.text.upper(),
            self.data_voo
        )

        self.partida.text = ''
        self.destino.text = ''
        self.nivelDeVoo.text = ''
        self.radialRumo.text = ''
        self.altitudeDeTransicao.text = ''
        self.nivelDeTransicao.text = ''
        self.mea.text = ''
        self.msa.text = ''
        self.aeronave.text = ''


# ==========================================================
# THIRD WINDOW
# Página para inserir os waypoints e tempos
# ==========================================================
class ThirdWindow(Screen):
    rotas = {}
    lista_rotas = {}

    wypt = ObjectProperty(None)
    estima = ObjectProperty(None)
    lista = ObjectProperty(None)
    label = ObjectProperty(None)

    def add_waypoint(self):
        self.ids.box.add_widget(Rota(self.wypt.text, self.ids.estima.text))
        self.rotas = {self.wypt.text: self.ids.estima.text}
        self.lista_rotas.update(self.rotas)
        self.wypt.text = ''
        self.estima.text = ''

    def remover_waypoint(self, waypoint):
        self.chave = waypoint.ids.label.text
        self.ids.box.remove_widget(waypoint)
        if self.chave in self.lista_rotas:
            del self.lista_rotas[self.chave]

    def avancar(self):
        id_voo = SecondWindow.id_voo
        self.novo = BaseDeDados()
        self.novo.tbl_estimas()
        self.novo.inserir_tbl_estimas(self.lista_rotas, id_voo)
        self.lista_rotas.clear()
        for k in range(len(self.ids.box.children)):
            self.ids.box.remove_widget(self.ids.box.children[0])


# ==========================================================
# FOURTH WINDOW
# Página para uso do plano inserido
# ==========================================================
class FourthWindow(Screen):
    rota = ObjectProperty(None)
    min_enrout = ObjectProperty(None)
    flt_level = ObjectProperty(None)
    min_sec = ObjectProperty(None)
    hdg = ObjectProperty(None)
    alt_trans = ObjectProperty(None)
    via = ObjectProperty(None)
    niv_trans = ObjectProperty(None)
    data = ''

    horas = {
        'START': None,
        'DESCOLAGEM': None,
        'ATERRAGEM': None,
        'CORTE': None
    }

    arranque = ObjectProperty(None)
    descolagem = ObjectProperty(None)
    aterragem = ObjectProperty(None)
    corte = ObjectProperty(None)
    fltime = ObjectProperty(None)
    blktime = ObjectProperty(None)
    hora_bloco = ObjectProperty(None)

    mostrar = BaseDeDados()
    t = ''

    sms1 = 'Você já descolou.'
    sms2 = 'Você ainda não deu start.'
    sms3 = 'Você ainda não descolou.'
    sms4 = 'Você ainda não aterrou.'

    def on_pre_enter(self):
        self.entrada()

    def on_pre_leave(self, *args):
        self.saida()

    def entrada(self):

        try:
            self.mostrar.selecionar_todos_tbl_voo()
            id_do_voo = self.mostrar.obter_ultimo_id_voo()
            self.eet = self.mostrar.selecionar_estimas_por_voo(id_do_voo)
            self.rota.text = self.mostrar.linhas[-1][1] + ' / ' + self.mostrar.linhas[-1][2]
            self.min_enrout.text = 'MEA - ' + str(self.mostrar.linhas[-1][7])
            self.flt_level.text = 'FL - ' + str(self.mostrar.linhas[-1][3])
            self.min_sec.text = 'MSA - ' + str(self.mostrar.linhas[-1][8]) + "'"
            self.hdg.text = 'Rumo/Radial - ' + str(self.mostrar.linhas[-1][4])
            self.alt_trans.text = 'Alt/trans - ' + str(self.mostrar.linhas[-1][5]) + "'"
            self.via.text = 'Via - ' + str(self.eet[0][0])
            self.niv_trans.text = 'Niv/trans - ' + str(self.mostrar.linhas[-1][6])

        except AttributeError:
            self.via.text = 'N/A'
        except IndexError:
            self.via.text = 'N/A'

        for i in range(len(self.eet)):
            self.ids.cx.add_widget(Relogio(text=str(self.eet[i][0])))
        self.fltime.text = "- HORA DE VOO - "
        self.blktime.text = "- HORA BLOCO - "
        self.horas = {
            'START': None,
            'DESCOLAGEM': None,
            'ATERRAGEM': None,
            'CORTE': None
        }

    def mensagem(self, msg):
        self.card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.texto = Label(text=msg)
        self.botao = BoxLayout(size_hint_y=None, height=dp(50))
        self.pop = Popup(title='Operação invalida.', title_color=[1, 0, 0, 1], content=self.card, size_hint=(0.72, 0.32))
        self.pop.open()
        self.sair = Button(text='SAIR', size_hint=(0.5, 0.7), size=(60, 30), on_release=self.pop.dismiss)
        self.botao.add_widget(self.sair)
        self.card.add_widget(self.texto)
        self.card.add_widget(self.botao)
        self.animar = Animation(size=(350, 200), duration=0.2, t='out_back')
        self.animar.start(self.pop)

    def saida(self):
        for i in range(len(self.eet)):
            self.ids.cx.remove_widget(Relogio(str(self.eet[i][0])))

    def hora_start(self):
        if self.horas[self.ids.descolagem.text] is None:
            if self.horas[self.ids.arranque.text] is None:
                self.t1 = dt.datetime.now()
                self.data_start = self.t1.strftime("%H:%M:%S")
                self.ids.box2.add_widget(Relogio(self.data_start))
                self.horas[self.ids.arranque.text] = self.data_start
            elif self.horas[self.ids.arranque.text] is not None:
                self.ids.box2.clear_widgets(children=None)
                self.horas[self.ids.arranque.text] = None
                self.hora_start()
        else:
            self.mensagem(self.sms1)

    def hora_descolagem(self):
        if self.horas[self.ids.arranque.text] is not None:
            if self.horas[self.ids.descolagem.text] is None:
                self.t2 = dt.datetime.now()
                self.data_desc = self.t2.strftime("%H:%M:%S")
                self.ids.box2_1.add_widget(Relogio(self.data_desc))
                self.ids.cx.clear_widgets(children=None)
                self.dar_estima()
                self.horas[self.ids.descolagem.text] = self.data_desc
            elif self.horas[self.ids.descolagem.text] is not None:
                if self.horas[self.ids.aterragem.text] is None:
                    self.ids.box2_1.clear_widgets(children=None)
                    self.horas[self.ids.descolagem.text] = None
                    self.hora_descolagem()
        else:
            self.mensagem(self.sms2)

    def hora_aterragem(self):
        if self.horas[self.ids.descolagem.text] is not None:
            if self.horas[self.ids.aterragem.text] is None:
                self.t3 = dt.datetime.now()
                self.data_aterr = self.t3.strftime("%H:%M:%S")
                self.ids.box2_2.add_widget(Relogio(self.data_aterr))
                self.horas[self.ids.aterragem.text] = self.data_aterr
                self.hora_de_voo = (datetime.strptime(self.data_aterr, "%H:%M:%S") - datetime.strptime(self.data_desc, "%H:%M:%S"))
                self.fltime.text = "- HORA DE VOO -\n\n       " + str(self.hora_de_voo)
            elif self.horas[self.ids.aterragem.text] is not None:
                if self.horas[self.ids.corte.text] is None:
                    self.ids.box2_2.clear_widgets(children=None)
                    self.horas[self.ids.aterragem.text] = None
                    self.hora_aterragem()
        else:
            self.mensagem(self.sms3)

    def hora_corte(self):
        if self.horas[self.ids.aterragem.text] is not None:
            if self.horas[self.ids.corte.text] is None:
                self.t4 = dt.datetime.now()
                self.data_corte = self.t4.strftime("%H:%M:%S")
                self.ids.box2_3.add_widget(Relogio(self.data_corte))
                self.horas[self.ids.corte.text] = self.data_corte
                self.hora_bloco = (datetime.strptime(self.data_corte, "%H:%M:%S") - datetime.strptime(self.data_desc, "%H:%M:%S"))
                self.blktime.text = "- HORA BLOCO -\n\n       " + str(self.hora_bloco)
            elif self.horas[self.ids.corte.text] is not None:
                self.ids.box2_3.clear_widgets(children=None)
                self.horas[self.ids.corte.text] = None
                self.hora_corte()
        else:
            self.mensagem(self.sms4)

    def dar_estima(self):
        for i in range(len(self.eet)):
            if i >= 1:
                self.t2 = datetime.strptime(self.estima, "%H:%M")
            self.estima = self.t2 + dt.timedelta(minutes=int(str(self.eet[i][1])))
            self.estima = self.estima.strftime("%H:%M")
            self.ids.cx.add_widget(Pontos(text=str(self.eet[i][0]), text2=self.estima))


# ==========================================================
# FIFTH WINDOW
# Janela para procurar um voo
# ==========================================================
class FifthWindow(Screen):
    posicao = ObjectProperty(None)
    recebe = BaseDeDados()

    data = 'Data'
    acft = 'Aeronave'
    dep = 'Partida'
    arr = 'Chegada'
    fl = 'FL'
    rad = 'Radial'
    alt_trans = 'Alt/T'
    niv_trans = 'Niv/T'
    min_enrout = 'MEA'
    min_safe = 'MSA'
    estimas = 'Estimas'

    def procurar_todos(self):
        self.recebe.selecionar_todos_tbl_voo()
        if self.ids.bx.children:
            pass
        else:
            self.ids.bx.add_widget(
                ListaProcura(
                    self.data, self.acft, self.dep, self.arr,
                    self.fl, self.rad, self.alt_trans,
                    self.niv_trans, self.min_enrout,
                    self.min_safe, self.estimas
                )
            )
        for i in range(len(self.recebe.linhas)):
            self.ids.bx.add_widget(
                MostraProcura(
                    self.recebe.linhas[i][1],
                    self.recebe.linhas[i][2],
                    self.recebe.linhas[i][3],
                    self.recebe.linhas[i][4],
                    self.recebe.linhas[i][5],
                    self.recebe.linhas[i][6],
                    self.recebe.linhas[i][7],
                    self.recebe.linhas[i][8],
                    self.recebe.linhas[i][9],
                    self.recebe.linhas[i][10],
                    self.recebe.linhas[i][11],
                    self.recebe.linhas[i][0]
                )
            )

    def procura_detalhada(self):
        self.ad = self.posicao.text
        self.recebe.selecionar_det_tbl_voo(self.ad.upper().strip())
        self.posicao.text = ''
        if len(self.recebe.linhas) >= 1:
            if self.ids.bx.children:
                pass
            else:
                self.ids.bx.add_widget(
                    ListaProcura(
                        self.data, self.acft, self.dep, self.arr,
                        self.fl, self.rad, self.alt_trans,
                        self.niv_trans, self.min_enrout,
                        self.min_safe, self.estimas
                    )
                )
            for i in range(len(self.recebe.linhas)):
                self.ids.bx.add_widget(
                    MostraProcura(
                        self.recebe.linhas[i][1],
                        self.recebe.linhas[i][2],
                        self.recebe.linhas[i][3],
                        self.recebe.linhas[i][4],
                        self.recebe.linhas[i][5],
                        self.recebe.linhas[i][6],
                        self.recebe.linhas[i][7],
                        self.recebe.linhas[i][8],
                        self.recebe.linhas[i][9],
                        self.recebe.linhas[i][10],
                        self.recebe.linhas[i][11],
                        self.recebe.linhas[i][0]
                    )
                )


# ==========================================================
# ROTA
# ==========================================================
class Rota(BoxLayout):
    label = ObjectProperty(None)
    eta = ObjectProperty(None)

    def __init__(self, text='', text2='', **kwargs):
        super(Rota, self).__init__(**kwargs)
        self.ids.label.text = text
        self.ids.eta.text = text2


# ==========================================================
# MOSTRA PROCURA
# ==========================================================
class MostraProcura(BoxLayout):
    data = ObjectProperty(None)
    aeronave = ObjectProperty(None)
    partida = ObjectProperty(None)
    chegada = ObjectProperty(None)
    radial = ObjectProperty(None)
    nivel_v = ObjectProperty(None)
    nivel_t = ObjectProperty(None)
    alt_t = ObjectProperty(None)
    msa = ObjectProperty(None)
    mea = ObjectProperty(None)
    est = ObjectProperty(None)
    id_voo = ObjectProperty(None)

    def __init__(self, text='', text2='', text3='', text4='', text5='',
                 text6='', text7='', text8='', text9='', text10='',
                 text11='', text12='', **kwargs):
        super(MostraProcura, self).__init__(**kwargs)
        self.ids.partida.text = str(text)
        self.ids.chegada.text = str(text2)
        self.ids.nivel_v.text = str(text4)
        self.ids.radial.text = str(text3)
        self.ids.nivel_t.text = str(text5)
        self.ids.alt_t.text = str(text6)
        self.ids.msa.text = str(text7)
        self.ids.mea.text = str(text8)
        self.ids.aeronave.text = str(text9)
        self.ids.data.text = str(text10)
        self.ids.est.text = str(text11) if text11 else 'N/A'
        self.ids.id_voo.text = str(text12)

        self.bd = BaseDeDados()

    def editar_dados(self):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        campos = [
            ('Data ', self.ids.data.text),
            ('Aeronave ', self.ids.aeronave.text),
            ('Partida ', self.ids.partida.text),
            ('Chegada ', self.ids.chegada.text),
            ('Nível de Voo ', self.ids.nivel_v.text),
            ('Radial ', self.ids.radial.text),
            ('Nível de Transição ', self.ids.nivel_t.text),
            ('Altitude de Transição ', self.ids.alt_t.text),
            ('MSA ', self.ids.msa.text),
            ('MEA ', self.ids.mea.text),
            ('Estimas ', self.ids.est.text)
        ]
        self.campos_edicao = {}
        for label_texto, valor in campos:
            linha = BoxLayout(orientation='horizontal', height=dp(48), spacing=dp(8))
            label = Label(text=label_texto, size_hint_x=0.38, halign='right', valign='middle')
            label.bind(size=label.setter('text_size'))
            text_input = TextInput(text=valor if valor else '', multiline=False, size_hint_x=0.62, height=30, padding=[dp(10), dp(5), dp(10), dp(5)])
            self.campos_edicao[label_texto] = text_input

            linha.add_widget(label)
            linha.add_widget(text_input)

            content.add_widget(linha)

        self.popup = Popup(title='Editar Dados do Voo', content=content, size_hint=(0.70, 1))

        # ==================================================
        # BOTÕES DE AÇÃO
        # Mantidos na mesma linha
        # ==================================================
        botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(58), spacing=dp(8), padding=dp(4))
        btn_salvar = Button(text='Salvar', size_hint=(0.2, 1), on_release=self.salvar_edicao)
        btn_eliminar = Button(text='Eliminar', size_hint=(0.2, 1), on_release=lambda x: self.apagar_edicao(self.ids.id_voo.text))
        btn_activar = Button(text='Ativar', size_hint=(0.2, 1), on_release=self.ativar_voo)
        btn_cancelar = Button(text='Cancelar', size_hint=(0.2, 1), on_release=self.popup.dismiss)

        botoes.add_widget(btn_salvar)
        botoes.add_widget(btn_eliminar)
        botoes.add_widget(btn_activar)
        botoes.add_widget(btn_cancelar)

        content.add_widget(botoes)
        self.popup.open()

    def salvar_edicao(self, *args):
        self.ids.data.text = self.campos_edicao['Data '].text
        self.ids.aeronave.text = self.campos_edicao['Aeronave '].text
        self.ids.partida.text = self.campos_edicao['Partida '].text
        self.ids.chegada.text = self.campos_edicao['Chegada '].text
        self.ids.nivel_v.text = self.campos_edicao['Nível de Voo '].text
        self.ids.radial.text = self.campos_edicao['Radial '].text
        self.ids.nivel_t.text = self.campos_edicao['Nível de Transição '].text
        self.ids.alt_t.text = self.campos_edicao['Altitude de Transição '].text
        self.ids.msa.text = self.campos_edicao['MSA '].text
        self.ids.mea.text = self.campos_edicao['MEA '].text
        self.ids.est.text = self.campos_edicao['Estimas '].text
        self.id_voo_est = self.ids.id_voo.text
        self.bd.actualizar_voo(
            self.ids.partida.text,
            self.ids.chegada.text,
            self.ids.nivel_v.text,
            self.ids.radial.text,
            self.ids.alt_t.text,
            self.ids.nivel_t.text,
            self.ids.mea.text,
            self.ids.msa.text,
            self.ids.aeronave.text,
            self.ids.data.text,
            self.ids.id_voo.text
        )
        self.bd.actualizar_estimas(self.ids.est.text, self.ids.id_voo.text)
        self.popup.dismiss()

    def apagar_edicao(self, id_voo):

        def confirmar_exclusao(instance):
            self.bd.apagar_dados(id_voo)
            parent = self.parent
            if parent:
                parent.remove_widget(self)
            popup_confirmacao.dismiss()

            if hasattr(self, 'popup'):
                self.popup.dismiss()

            mostrar_mensagem('Registro excluído com sucesso')

        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        content.add_widget(Label(text='Tem certeza que deseja apagar este registro?', halign='center', valign='middle'))
        botoes = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(55))
        btn_sim = Button(text='Sim')
        btn_nao = Button(text='Não')
        btn_sim.bind(on_release=confirmar_exclusao)

        botoes.add_widget(btn_sim)
        botoes.add_widget(btn_nao)

        content.add_widget(botoes)

        popup_confirmacao = Popup(title='Confirmar exclusão', title_color=(1, 0, 0, 1), content=content, size_hint=(0.82, 0.30))
        btn_nao.bind(on_release=popup_confirmacao.dismiss)

        popup_confirmacao.open()

    def ativar_voo(self, *args):
        self.t1 = dt.datetime.now()
        self.data_ativar_voo = self.t1.strftime("%d/%m/%y")
        self.bd.inserir_tbl_voo(
            self.ids.partida.text,
            self.ids.chegada.text,
            self.ids.nivel_v.text,
            self.ids.radial.text,
            self.ids.nivel_t.text,
            self.ids.alt_t.text,
            self.ids.msa.text,
            self.ids.mea.text,
            self.ids.aeronave.text,
            self.data_ativar_voo
        )
        self.id_ativar_voo = self.bd.obter_ultimo_id_voo()
        self.bd.actualizar_estimas(self.ids.est.text, self.id_ativar_voo)
        App.get_running_app().root.current = 'voo'
        self.popup.dismiss()


# ==========================================================
# LISTA PROCURA
# ==========================================================
class ListaProcura(BoxLayout):
    data = ObjectProperty(None)
    acft = ObjectProperty(None)
    dep = ObjectProperty(None)
    arr = ObjectProperty(None)
    fl = ObjectProperty(None)
    rad = ObjectProperty(None)
    alt_trans = ObjectProperty(None)
    niv_trans = ObjectProperty(None)
    min_enrout = ObjectProperty(None)
    min_safe = ObjectProperty(None)
    estimas = ObjectProperty(None)

    def __init__(self, text='', text2='', text3='', text4='', text5='',
                 text6='', text7='', text8='', text9='', text10='',
                 text11='', **kwargs):
        super(ListaProcura, self).__init__(**kwargs)
        self.ids.data.text = text
        self.ids.acft.text = text2
        self.ids.dep.text = text3
        self.ids.arr.text = text4
        self.ids.fl.text = text5
        self.ids.rad.text = text6
        self.ids.alt_trans.text = text7
        self.ids.niv_trans.text = text8
        self.ids.min_enrout.text = text9
        self.ids.min_safe.text = text10
        self.ids.estimas.text = text11


# ==========================================================
# PONTOS
# ==========================================================
class Pontos(BoxLayout):
    pto = ObjectProperty(None)
    temp = ObjectProperty(None)

    def __init__(self, text='', text2='', **kwargs):
        super(Pontos, self).__init__(**kwargs)
        self.ids.pto.text = text
        self.ids.temp.text = text2


# ==========================================================
# RELOGIO
# ==========================================================

class Relogio(GridLayout):
    # Para cronometrar os tempos:
    # START, TAXI, T/O e LDG
    cronometro = ObjectProperty(None)

    def __init__(self, text='', **kwargs):
        super(Relogio, self).__init__(**kwargs)
        self.ids.cronometro.text = text


# ==========================================================
# BOTÃO ARREDONDA
# ==========================================================
class Arredonda(Button):
    pass


# ==========================================================
# WINDOW MANAGER
# ==========================================================
class WindowManager(ScreenManager):
    pass


# ==========================================================
# CARREGA KV
# ==========================================================
kv = Builder.load_file("my.kv")

# ==========================================================
# APLICAÇÃO PRINCIPAL
# ==========================================================
class FlightManager(MDApp):
    theme_cls = ThemeManager()
    title = 'flightPlan'

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return kv

# ==========================================================
# EXECUÇÃO
# ==========================================================
if __name__ == "__main__":
    FlightManager().run()