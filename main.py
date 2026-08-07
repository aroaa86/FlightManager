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
import datetime as dt
from kivymd.theming import ThemeManager
from kivymd.toast import toast
import sqlite3
import time
import os
import platform


class BaseDeDados:

    def __init__(self):
        if App.get_running_app():
            db_path = os.path.join(App.get_running_app().user_data_dir, "missoes.db")
        else:
            db_path = "missoes.db"

        self.conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
        self.cursor = self.conn.cursor()
        self.tbl_voo()

    # Cria a tabela voos, onde serão armazenados os dados do voo, inseridos pelo ‘user’
    def tbl_voo(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS voos(IDVOO integer PRIMARY KEY AUTOINCREMENT,
                                ad_de_partida text, ad_de_chegada text, 
                                nivel_de_voo integer, radial_rumo integer, 
                                altitude_de_transicao integer, nivel_de_transicao integer, 
                                mea integer, msa integer, aeronave text, data text)''')

    # Cria a tabela estimas, onde serão armazenadas as estimas, inseridas pelo ‘user’
    def inserir_tbl_voo(self, partida, destino,
                        nivelDeVoo,radialRumo,
                        altitudeDETransicao, nivelDeTransicao,
                        mea, msa, aeronave, data):
        self.cursor = self.conn.cursor()
        self.cursor.execute('''INSERT INTO voos (
                            ad_de_partida, ad_de_chegada, 
                            nivel_de_voo, radial_rumo, 
                            altitude_de_transicao, nivel_de_transicao, 
                            mea, msa, aeronave, data) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                            (partida, destino, nivelDeVoo,
                            radialRumo, altitudeDETransicao,
                            nivelDeTransicao, mea, msa, aeronave, data))
        self.conn.commit()
        # Capturar o ‘ID’ gerado automaticamente
        id_voo = self.cursor.lastrowid
        self.cursor.close()
        return id_voo

    # Seleciona todos os elementos na tabela voos
    def selecionar_todos_tbl_voo(self):
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                SELECT 
                    voos.IDVOO,
                    voos.ad_de_partida, voos.ad_de_chegada,
                    voos.nivel_de_voo, voos.radial_rumo, 
                    voos.altitude_de_transicao,
                    voos.nivel_de_transicao, voos.mea, 
                    voos.msa, voos.aeronave, voos.data,
                    GROUP_CONCAT(estimas.waypoint_nome || ':' || estimas.waypoint_tempo, ' | '
                        ORDER BY estimas.IDESTIMAS) as waypoints
                FROM voos 
                LEFT JOIN estimas ON voos.IDVOO = estimas.id_voo
                GROUP BY voos.IDVOO;""")
            self.linhas = self.cursor.fetchall()
        except:
            return toast('Sem voos na lista', duration=5)
        #self.conn.commit()
        self.cursor.close()

    # Seleciona um dado específico na tabela voos, com base no 'input' do 'user'
    def selecionar_det_tbl_voo(self, entrada):
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            SELECT 
                voos.IDVOO,
                voos.ad_de_partida, voos.ad_de_chegada,
                voos.nivel_de_voo, voos.radial_rumo, 
                voos.altitude_de_transicao,
                voos.nivel_de_transicao, voos.mea, 
                voos.msa, voos.aeronave, voos.data,
                GROUP_CONCAT(estimas.waypoint_nome || ':' || estimas.waypoint_tempo, ' | '
                    ORDER BY estimas.IDESTIMAS) as waypoints
            FROM voos
            LEFT JOIN estimas ON voos.IDVOO = estimas.id_voo
            WHERE ad_de_partida=? OR ad_de_chegada=? OR aeronave=?
            GROUP BY voos.IDVOO''',
                            (entrada, entrada, entrada))
        self.linhas = self.cursor.fetchall()
        if self.linhas:
            toast('Voo encontrado com sucesso', duration=5)
            for linha in self.linhas:
                print(linha)
        else:
            toast('Voo não encontrado', duration=5)
        self.conn.commit()
        self.cursor.close()
        return self.linhas

    # Atualiza os dados de um específico voo na tabela voos, com base no 'ID' do voo e outros dados
    def actualizar_voo(self, partida, chegada, niv_v, rad, alt_t, niv_t, mea, msa, aeronave, data, id_voo):
        self.cursor = self.conn.cursor()
        try:
            sql = """UPDATE voos SET 
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
                    WHERE IDVOO = ?"""

            valores = (partida, chegada, niv_v, rad, alt_t, niv_t,
                       mea, msa, aeronave, data, id_voo)

            self.cursor.execute(sql, valores)
            self.conn.commit()
            toast('Dados atualizados com sucesso!', duration=5)

        except sqlite3.Error as erro:
            toast('Erro ao atualizar dados!', duration=5)
            self.conn.rollback()

        finally:
            if self.cursor:
                self.cursor.close()

    # Cria tabela das estimas
    def tbl_estimas(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS estimas(
        IDESTIMAS integer PRIMARY KEY AUTOINCREMENT, 
        id_voo integer,
        waypoint_nome text,
        waypoint_tempo integer,
        FOREIGN KEY(id_voo) REFERENCES voos(IDVOO))''')

    # Insere valores na tabela das estimas, waypoint e tempo
    def inserir_tbl_estimas(self, waypoints, id_voo):
        self.cursor = self.conn.cursor()
        try:
            for waypoint_nome, tempo in waypoints.items():
                self.cursor.execute('''INSERT INTO estimas 
                    (id_voo, waypoint_nome, waypoint_tempo) 
                    VALUES (?, ?, ?)''', (id_voo, waypoint_nome, tempo))
            self.conn.commit()
        except sqlite3.Error as erro:
            toast("Erro ao inserir waypoints", duration=5)
            self.conn.rollback()
        finally:
            self.cursor.close()

    # Atualiza as estimas de um voo, com base no 'ID' do voo
    def actualizar_estimas(self, waypoints, id_voo):
        self.cursor = self.conn.cursor()
        try:
            # Remove estimas antigas
            self.cursor.execute("DELETE FROM estimas WHERE id_voo = ?", (id_voo,))

            if isinstance(waypoints, str) and waypoints and waypoints != 'N/A':
                # Primeiro, dividimos pelos espaços para separar os pares
                pares = [p.strip() for p in waypoints.split()]
                for par in pares:
                    # Encontra a posição do último ':'
                    ultima_posicao = par.rfind(':')

                    if ultima_posicao != -1:
                        waypoint_nome = par[:ultima_posicao].strip()
                        tempo = par[ultima_posicao + 1:].strip()

                        self.cursor.execute("""
                            INSERT INTO estimas (id_voo, waypoint_nome, waypoint_tempo)
                            VALUES (?, ?, ?)""",
                                            (id_voo, waypoint_nome, tempo))

            self.conn.commit()
            toast('Waypoints atualizados com sucesso!', duration=8)
            return True

        except sqlite3.Error as error:
            print(f"Erro SQLite: {error}")
            self.conn.rollback()
            toast('Erro ao atualizar waypoints!', duration=8)
            return False

        finally:
            if self.cursor:
                self.cursor.close()

    # Retorna as estimas associadas a um voo específico, com base no 'ID' do voo
    def selecionar_estimas_por_voo(self, id_voo):

        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                SELECT waypoint_nome, waypoint_tempo 
                FROM estimas 
                WHERE id_voo = ? 
                ORDER BY IDESTIMAS""", (id_voo,))
            estimas = self.cursor.fetchall()
            return estimas if estimas else []
        except sqlite3.Error as erro:
            toast("Erro ao selecionar estimas:", duration=5)
            return []
        finally:
            self.cursor.close()

    # Retorna o 'ID' do último voo inserido na base de dados
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

    # Apaga o registro selecionado com base no seu 'ID'
    def apagar_dados(self, id_dados):
        try:
            # Primeiro, apagar registros relacionados na tabela estimas
            self.cursor = self.conn.cursor()
            self.cursor.execute("DELETE FROM estimas WHERE id_voo = ?", (id_dados,))

            # Depois, apagar o registro na tabela voos
            self.cursor.execute("DELETE FROM voos WHERE IDVOO = ?", (id_dados,))

            self.conn.commit()
            toast('Dados apagados com sucesso!', duration=5)

        except sqlite3.Error as error:
            toast('Erro ao apagar dados!', duration=5)
            self.conn.rollback()

bd = BaseDeDados()


class MainWindow(Screen):

    def on_pre_enter(self):
        Window.bind(on_request_close=self.sair)

    def sair(self, *args, **kwargs):
        self.card = BoxLayout(orientation='vertical')  # contem a imagem
        self.botao = BoxLayout(padding=(25, 5), spacing=10)  # contem os botões

        self.pop = Popup(title='Você deseja mesmo sair?', title_color=[0, 1, 0, 1], content=self.card, size_hint=(None, None), size=(100, 80))

        self.imagem = Image(source='alerta1.jpg')
        self.continua = Button(text='Não', size_hint=(0.5, 0.60), on_release=self.pop.dismiss)
        self.botao.add_widget(Button(text='Sim', size_hint=(0.5, 0.60), on_release=MDApp.get_running_app().stop))

        self.botao.add_widget(self.continua)

        self.card.add_widget(self.imagem)
        self.card.add_widget(self.botao)

        self.animar = Animation(size=(350, 200), duration=0.2, t='out_back')
        self.animar.start(self.pop)
        self.pop.open()
        return True


class SecondWindow(Screen): # Página para inserir os dados do plano de voo

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
    t = time.localtime()  # provavelmente deve ser apagado (variável sem efeito)

    def avancar(self):
        self.t1 = dt.datetime.now()
        self.data_voo = self.t1.strftime("%d/%m/%y") # Captura automaticamente a data do sistema (considerar mudar para dados vindo do utilizador)
        self.ad_partida = self.partida.text
        self.ad_chegada = self.destino.text
        self.voa = {'AD/Partida': self.ad_partida.upper(), 'AD/Chegada': self.ad_chegada.upper(),
                    'Nível de voo': self.nivelDeVoo.text, 'Radial/Rumo': self.radialRumo.text+'º',
                    'Altitude de transição': self.altitudeDeTransicao.text,
                    'Nível de transição': self.nivelDeTransicao.text, 'MEA': self.mea.text, 'MSA':
                    self.msa.text, 'Aeronave': self.aeronave.text, 'waypoints': ''}

        self.novo = bd
        self.novo.tbl_voo()

        SecondWindow.id_voo = self.novo.inserir_tbl_voo(
            self.ad_partida.upper(), self.ad_chegada.upper(),
            self.nivelDeVoo.text, self.radialRumo.text + 'º',
            self.altitudeDeTransicao.text, self.nivelDeTransicao.text,
            self.mea.text, self.msa.text, self.aeronave.text.upper(), self.data_voo
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


class ThirdWindow(Screen): # Página p inserir os waypoints e tempos

    rotas = {}
    lista_rotas = {}
    wypt = ObjectProperty(None)
    estima = ObjectProperty(None)
    lista = ObjectProperty(None)
    label = ObjectProperty(None)

    def add_waypoint(self):
        self.ids.box.add_widget(Rota(self.wypt.text, self.ids.estima.text))
        self.rotas = {self.wypt.text: self.estima.text}
        self.lista_rotas.update(self.rotas)
        self.wypt.text = ''
        self.estima.text = ''

    def remover_waypoint(self, waypoint):
        self.imp = SecondWindow()
        self.imp.load_data()
        self.chave = waypoint.ids.label.text
        self.ids.box.remove_widget(waypoint)
        del self.lista_rotas[self.chave]

    def avancar(self):
        id_voo = SecondWindow.id_voo
        self.imp = SecondWindow()
        self.novo = bd
        self.novo.tbl_estimas()
        self.novo.inserir_tbl_estimas(self.lista_rotas, id_voo)
        self.lista_rotas.clear()
        for k in range(len(self.ids.box.children)):
            self.ids.box.remove_widget(self.ids.box.children[0])


class FourthWindow(Screen): # Página para uso do plano inserido (botão iniciar)

    rota = ObjectProperty(None)
    min_enrout = ObjectProperty(None)
    flt_level = ObjectProperty(None)
    min_sec = ObjectProperty(None)
    hdg = ObjectProperty(None)
    alt_trans = ObjectProperty(None)
    via = ObjectProperty(None)
    niv_trans = ObjectProperty(None)
    data = ''
    horas = {'START': None, 'DESCOLAGEM': None, 'ATERRAGEM': None, 'CORTE': None}
    arranque = ObjectProperty(None)
    descolagem = ObjectProperty(None)
    aterragem = ObjectProperty(None)
    corte = ObjectProperty(None)
    fltime = ObjectProperty(None)
    blktime = ObjectProperty(None)
    hora_bloco = ObjectProperty(None)
    mostrar = bd

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
            """self.wndw = SecondWindow()
            self.wndw.load_data()"""
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
        self.horas = {'START': None, 'DESCOLAGEM': None, 'ATERRAGEM': None, 'CORTE': None}

    def mensagem(self, msg):
        self.card = BoxLayout(orientation='vertical')
        self.texto = Label(text=msg)
        self.botao = BoxLayout(padding=(25, 5))

        self.pop = Popup(title='Operação invalida.', title_color=[1, 0, 0, 1], content=self.card, size_hint=(None, None), size=(100, 80))
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
                self.hora_de_voo = datetime.strptime(self.data_aterr, "%H:%M:%S") - datetime.strptime(self.data_desc, "%H:%M:%S")
                self.fltime.text = "- HORA DE VOO - \n\n" + "       "+str(self.hora_de_voo)
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
                self.hora_bloco = datetime.strptime(self.data_corte, "%H:%M:%S") - datetime.strptime(self.data_desc, "%H:%M:%S")
                self.blktime.text = "- HORA BLOCO - \n\n" + "       " + str(self.hora_bloco)
            elif self.horas[self.ids.corte.text] is not None:
                self.ids.box2_3.clear_widgets(children=None)
                self.horas[self.ids.corte.text] = None
                self.hora_corte()
                # Aqui não salvamos apenas atualizamos o mesmo voo
        else:
            self.mensagem(self.sms4)

    def dar_estima(self):
        for i in range(len(self.eet)):
            if i >= 1:
                self.t2 = datetime.strptime(self.estima, "%H:%M")
            self.estima = self.t2 + dt.timedelta(minutes=int(str(self.eet[i][1])))
            self.estima = self.estima.strftime("%H:%M")
            self.ids.cx.add_widget(Pontos(text=str(self.eet[i][0]), text2=self.estima))


class FifthWindow(Screen): # janela para procurar um voo (botão procurar)
    posicao = ObjectProperty(None)
    recebe = bd
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
            self.ids.bx.add_widget(ListaProcura(self.data, self.acft, self.dep, self.arr,
                                                self.fl, self.rad, self.alt_trans,
                                                self.niv_trans, self.min_enrout, self.min_safe,
                                                self.estimas))
        for i in range(len(self.recebe.linhas)):
            self.ids.bx.add_widget(MostraProcura(self.recebe.linhas[i][1], self.recebe.linhas[i][2],
                                                     self.recebe.linhas[i][3], self.recebe.linhas[i][4],
                                                     self.recebe.linhas[i][5], self.recebe.linhas[i][6],
                                                     self.recebe.linhas[i][7], self.recebe.linhas[i][8],
                                                     self.recebe.linhas[i][9], self.recebe.linhas[i][10],
                                                     self.recebe.linhas[i][11], self.recebe.linhas[i][0]))

    def procura_detalhada(self):
        self.ad = self.posicao.text
        # A função abaixo recebe o parâmetro vindo do utilizador (TextInput)
        self.recebe.selecionar_det_tbl_voo(self.ad.upper().strip())
        self.posicao.text = ''
        if len(self.recebe.linhas) >= 1:
            if self.ids.bx.children:
                pass
            else:
                self.ids.bx.add_widget(ListaProcura(self.data, self.acft, self.dep, self.arr,
                                                      self.fl, self.rad, self.alt_trans,
                                                      self.niv_trans, self.min_enrout, self.min_safe,
                                                      self.estimas))
            for i in range(len(self.recebe.linhas)):
                self.ids.bx.add_widget(MostraProcura(self.recebe.linhas[i][1], self.recebe.linhas[i][2],
                                                     self.recebe.linhas[i][3], self.recebe.linhas[i][4],
                                                     self.recebe.linhas[i][5], self.recebe.linhas[i][6],
                                                     self.recebe.linhas[i][7], self.recebe.linhas[i][8],
                                                     self.recebe.linhas[i][9], self.recebe.linhas[i][10],
                                                     self.recebe.linhas[i][11], self.recebe.linhas[i][0]))


class Rota(BoxLayout):
    label = ObjectProperty(None)
    eta = ObjectProperty(None)

    def __init__(self, text='', text2='', **kwargs):
        super(Rota, self).__init__(**kwargs)
        self.ids.label.text = text
        self.ids.eta.text = text2


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

    def __init__(self, text='', text2='', text3='',
                 text4='', text5='', text6='',
                 text7='', text8='', text9='',
                 text10='',text11='',text12='', **kwargs):
        super(MostraProcura, self).__init__(**kwargs)
        self.ids.partida.text = str(text)
        self.ids.chegada.text = str(text2)
        self.ids.radial.text = str(text3)
        self.ids.nivel_v.text = str(text4)
        self.ids.nivel_t.text = str(text5)
        self.ids.alt_t.text = str(text6)
        self.ids.msa.text = str(text7)
        self.ids.mea.text = str(text8)
        self.ids.aeronave.text = str(text9)
        self.ids.data.text = str(text10)
        self.ids.est.text = str(text11) if text11 else 'N/A'
        self.ids.id_voo.text = str(text12)
        self.bd = bd

    def editar_dados(self):
        # Layout principal vertical
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Lista de campos e seus labels
        campos = [
            ('Data ', self.ids.data.text),
            ('Aeronave ', self.ids.aeronave.text),
            ('Partida ', self.ids.partida.text),
            ('Chegada ', self.ids.chegada.text),
            ('Radial ', self.ids.radial.text),
            ('Nível de Voo ', self.ids.nivel_v.text),
            ('Nível de Transição ', self.ids.nivel_t.text),
            ('Altitude de Transição ', self.ids.alt_t.text),
            ('MSA ', self.ids.msa.text),
            ('MEA ', self.ids.mea.text),
            ('Estimas ', self.ids.est.text)]

        # Dicionário para armazenar os TextInputs
        self.campos_edicao = {}

        # Criar os layouts horizontais para cada campo
        for label_texto, valor in campos:
            # Layout horizontal para cada par label/input
            linha = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

            # Label do campo (lado esquerdo)
            label = Label(text=label_texto, size_hint_x=0.4, halign='right', valign='middle')
            label.bind(size=label.setter('text_size'))

            # Campo de entrada (lado direito)
            text_input = TextInput(text=valor if valor else '', multiline=False, size_hint_x=0.6, height=30, padding=[10, 5, 10, 5])

            # Armazenar referência ao TextInput
            self.campos_edicao[label_texto] = text_input

            # Adicionar widgets ao layout horizontal
            linha.add_widget(label)
            linha.add_widget(text_input)

            # Adicionar linha ao layout principal
            content.add_widget(linha)

        # Criar e mostrar o popup
        self.popup = Popup(title='Editar Dados do Voo', content=content, size_hint=(None, None), size=(500, 700))

        # Botões de ação
        botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=20, padding=[10, 10])

        # Botão Salvar
        btn_salvar = Button(text='Salvar', size_hint=(0.2, 1), on_release=self.salvar_edicao)
        # Botão eliminar
        btn_eliminar = Button(text='Eliminar', size_hint=(0.2, 1), on_release=lambda x: self.apagar_edicao(self.ids.id_voo.text))
        # Botão ativar
        btn_activar = Button(text='Ativar', size_hint=(0.2, 1), on_release=self.ativar_voo)
        # Botão Cancelar
        btn_cancelar = Button(text='Cancelar', size_hint=(0.2, 1), on_release=self.popup.dismiss)

        botoes.add_widget(btn_salvar)
        botoes.add_widget(btn_eliminar)
        botoes.add_widget(btn_activar)
        botoes.add_widget(btn_cancelar)
        content.add_widget(botoes)

        self.popup.open()

    def salvar_edicao(self, *args):
        # Atualizar os valores dos campos
        self.ids.data.text = self.campos_edicao['Data '].text
        self.ids.aeronave.text = self.campos_edicao['Aeronave '].text
        self.ids.partida.text = self.campos_edicao['Partida '].text
        self.ids.chegada.text = self.campos_edicao['Chegada '].text
        self.ids.radial.text = self.campos_edicao['Radial '].text
        self.ids.nivel_v.text = self.campos_edicao['Nível de Voo '].text
        self.ids.nivel_t.text = self.campos_edicao['Nível de Transição '].text
        self.ids.alt_t.text = self.campos_edicao['Altitude de Transição '].text
        self.ids.msa.text = self.campos_edicao['MSA '].text
        self.ids.mea.text = self.campos_edicao['MEA '].text
        self.ids.est.text = self.campos_edicao['Estimas '].text
        self.id_voo_est = self.ids.id_voo.text

        self.bd.actualizar_voo(self.ids.partida.text, self.ids.chegada.text,
                               self.ids.nivel_v.text, self.ids.radial.text,
                               self.ids.alt_t.text, self.ids.nivel_t.text,
                               self.ids.mea.text, self.ids.msa.text,
                               self.ids.aeronave.text, self.ids.data.text, self.ids.id_voo.text)

        self.bd.actualizar_estimas(self.ids.est.text, self.ids.id_voo.text)

        self.popup.dismiss()

    def apagar_edicao(self, id_voo):
        def confirmar_exclusao(instance):
            self.bd.apagar_dados(id_voo)
            # Remover o widget da lista
            parent = self.parent
            if parent:
                parent.remove_widget(self)
            # Fechar os popups
            popup_confirmacao.dismiss()  # Fecha o popup de confirmação
            if hasattr(self, 'popup'):
                self.popup.dismiss()  # Fecha o popup de edição
            # Feedback visual
            toast('Registro excluído com sucesso', duration=3)

        # Criar popup de confirmação
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Tem certeza que deseja apagar este registro?'))

        botoes = BoxLayout(orientation='horizontal', spacing=10)
        btn_sim = Button(text='Sim', size_hint=(0.5, None), height=40)
        btn_sim.bind(on_release=confirmar_exclusao)
        btn_nao = Button(text='Não', size_hint=(0.5, None), height=40)

        botoes.add_widget(btn_sim)
        botoes.add_widget(btn_nao)
        content.add_widget(botoes)

        popup_confirmacao = Popup(title='Confirmar exclusão',
                                  title_color=(1, 0, 0, 1),
                                  content=content,
                                  size_hint=(None, None),
                                  size=(500, 250))

        btn_nao.bind(on_release=popup_confirmacao.dismiss)
        popup_confirmacao.open()

    def ativar_voo(self, *args):
        # Armazenar os novos dados na base de dados, na tabela voos
        self.t1 = dt.datetime.now()
        self.data_ativar_voo = self.t1.strftime("%d/%m/%y") # Captura automaticamente a data do sistema (considerar mudar)
        self.bd.inserir_tbl_voo(self.ids.partida.text, self.ids.chegada.text,
                               self.ids.radial.text, self.ids.nivel_v.text,
                               self.ids.nivel_t.text, self.ids.alt_t.text,
                               self.ids.msa.text, self.ids.mea.text,
                               self.ids.aeronave.text, self.data_ativar_voo)

        # Recebe o 'id' do último voo gravado na base de dados
        self.id_ativar_voo = self.bd.obter_ultimo_id_voo()

        # Armazenar os novos dados na base de dados, na tabela estimas
        self.bd.actualizar_estimas(self.ids.est.text, self.id_ativar_voo)
        # Avançar para a 4.ª janela (onde será realiza o voo)
        App.get_running_app().root.current = 'voo'
        # Liberar o popup
        self.popup.dismiss()


class ListaProcura(BoxLayout):
    data = ObjectProperty(None)
    acft = ObjectProperty(None)
    dep = ObjectProperty(None)
    arr = ObjectProperty(None)
    fl  = ObjectProperty(None)
    rad = ObjectProperty(None)
    alt_trans = ObjectProperty(None)
    niv_trans = ObjectProperty(None)
    min_enrout = ObjectProperty(None)
    min_safe = ObjectProperty(None)
    estimas = ObjectProperty(None)

    def __init__(self, text='', text2='',
                 text3='', text4='', text5='',
                 text6='', text7='', text8='',
                 text9='', text10='', text11='',
                 **kwargs):
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


class Pontos(BoxLayout):
    pto = ObjectProperty(None)
    temp = ObjectProperty(None)

    def __init__(self, text='', text2='', **kwargs):
        super(Pontos, self).__init__(**kwargs)
        self.ids.pto.text = text
        self.ids.temp.text = text2


class Relogio(GridLayout):
    # Para cronometrar o tempo os tempos: start, taxi, T\O e LDG
    # Adicionado na FourthWindow
    cronometro = ObjectProperty(None)

    def __init__(self, text='', **kwargs):
        super(Relogio, self).__init__(**kwargs)
        self.ids.cronometro.text = text


class Arredonda(Button):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("my.kv")


class FlightManager(MDApp):
    theme_cls = ThemeManager()
    title = 'flightPlan'

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        return kv


if __name__ == "__main__":
    FlightManager().run()
