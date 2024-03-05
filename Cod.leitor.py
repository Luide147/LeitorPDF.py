import fitz  # PyMuPDF
import pyttsx3
import tkinter as tk
from tkinter import filedialog
from threading import Thread, Lock

class PDFReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor de PDF")
        self.root.geometry("450x400")  # Define o tamanho inicial da janela

        # Inicialização do leitor de PDF
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 300)  # Define a velocidade de leitura padrão
        self.is_playing = False
        self.is_paused = False
        self.current_page = 0
        self.total_pages = 0
        self.doc = None
        self.doc_lock = Lock()
        self.text_window = None  # Janela para exibir o texto
        self.thread = None  # Inicializa o atributo thread

        # Interface gráfica
        self.create_widgets()

    def create_widgets(self):
        # Labels
        self.label = tk.Label(self.root, text="Bem-vindo ao Leitor de PDF", font=("Arial", 14))
        self.label.pack(pady=10)

        self.speed_label = tk.Label(self.root, text="Velocidade de Leitura:", font=("Arial", 12))
        self.speed_label.pack(pady=5)

        # Barra de velocidade
        self.speed_scale = tk.Scale(self.root, from_=50, to=500, orient=tk.HORIZONTAL, resolution=50, command=self.update_speed)
        self.speed_scale.set(300)  # Define a velocidade inicial
        self.speed_scale.pack(pady=5)

        # Botões
        self.select_button = tk.Button(self.root, text="Selecionar PDF", command=self.select_pdf, font=("Arial", 12))
        self.select_button.pack(pady=5)

        self.play_button = tk.Button(self.root, text="Play", command=self.play_pdf, font=("Arial", 12), state=tk.DISABLED)
        self.play_button.pack(pady=5)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_pdf, font=("Arial", 12), state=tk.DISABLED)
        self.pause_button.pack(pady=5)

        self.next_button = tk.Button(self.root, text="Próxima Página", command=self.next_page, font=("Arial", 12), state=tk.DISABLED)
        self.next_button.pack(pady=5)

        self.prev_button = tk.Button(self.root, text="Página Anterior", command=self.prev_page, font=("Arial", 12))
        self.prev_button.pack(pady=5)

    def update_speed(self, speed):
        self.engine.setProperty('rate', int(speed))

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.file_path = file_path
            self.play_button.config(state=tk.NORMAL)
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)

            # Atualiza o nome do arquivo na janela
            file_name = file_path.split("/")[-1]  # Extrai apenas o nome do arquivo
            self.label.config(text=f"Arquivo selecionado: {file_name}")

    def play_pdf(self):
        self.play_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.is_playing = True
        self.is_paused = False  # Garante que não haja pausa ao iniciar a leitura
        self.open_text_window()  # Abre a janela para exibir o texto
        if not self.thread or not self.thread.is_alive():  # Verifica se não há uma thread em execução
            self.thread = Thread(target=self.read_pdf)
            self.thread.start()

    def pause_pdf(self):
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.is_playing = False
        self.is_paused = True

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.read_page()

    def next_page(self):
        if self.doc and self.current_page < self.total_pages - 1:
            self.current_page += 1
            if self.current_page == self.total_pages - 1:
                self.next_button.config(state=tk.DISABLED)  # Desabilita o botão quando estiver na última página
            self.read_page()

    def open_text_window(self):
        if not self.text_window:  # Verifica se a janela ainda não foi criada
            self.text_window = tk.Toplevel(self.root)
            self.text_window.title("Texto do PDF")
            self.text_window.geometry("600x400")
            self.text_area = tk.Text(self.text_window, wrap="word")
            self.text_area.pack(expand=True, fill="both")

    def read_page(self):
        with self.doc_lock:
            if self.doc:
                page = self.doc.load_page(self.current_page)
            text = page.get_text()
            print("Texto da página:", text)  # Adiciona um log para depuração
            self.text_area.delete('1.0', tk.END)  # Limpa o conteúdo anterior
            self.text_area.insert(tk.END, text)  # Insere o texto na janela

    def read_pdf(self):
        try:
            # Abre o arquivo PDF
            with self.doc_lock:
                self.doc = fitz.open(self.file_path)
                self.total_pages = len(self.doc)
        
            # Lê o texto de cada página
            while self.current_page < self.total_pages:
                if not self.is_playing:
                    break
                if self.is_paused:  # Verifica se a leitura está pausada
                    continue  # Se estiver pausada, pula para a próxima iteração do loop
                self.read_page()
                page = self.doc.load_page(self.current_page)
                text = page.get_text()
                print("Texto da página:", text)  # Adiciona um log para depuração
                self.engine.say(text)
                self.engine.runAndWait()
                self.current_page += 1

        except Exception as e:
            print("Ocorreu um erro:", e)

        finally:
            with self.doc_lock:
                if self.doc:
                    self.doc.close()

# Cria uma janela Tkinter
root = tk.Tk()

app = PDFReader(root)

# Inicia o loop da interface gráfica
root.mainloop()
