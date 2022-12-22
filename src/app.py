import customtkinter as ctk
from pytube.exceptions import RegexMatchError

import download

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

FONT16 = ("Inter", 16)
FONT18 = ("Inter", 18)
FONT20 = ("Inter", 20)
PADX = 10


class App(ctk.CTk):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.title("Baixa-Músicas")
        # self.geometry("x")
        self.resizable(False, False)
        self.folder = ""

        # Link input
        self.link_label = ctk.CTkLabel(master=self,
                                       text="Insira o link da música no Youtube:",
                                       font=FONT20)
        self.link_label.grid(row=0, column=0, padx=PADX, pady=10, sticky="w")

        self.link_entry = ctk.CTkEntry(self, width=750, font=FONT16)
        self.link_entry.grid(row=1, column=0, padx=PADX, pady=(0, 20))

        # Folder selection
        self.folder_button = ctk.CTkButton(master=self,
                                           text="Escolher pasta",
                                           font=FONT20,
                                           command=self.select_folder)
        self.folder_button.grid(row=2, column=0, padx=PADX, pady=10, sticky="w")

        self.folder_label = ctk.CTkLabel(master=self,
                                         text="Pasta selecionada:",
                                         font=FONT18)
        self.folder_label.grid(row=3, column=0, padx=PADX,
                               pady=(0, 20), sticky="w")

        # Start download and status
        self.download_button = ctk.CTkButton(master=self,
                                             text="Baixar",
                                             font=FONT20,
                                             command=self.download_music)
        self.download_button.grid(row=5, column=0, padx=PADX)

        self.download_status = ctk.CTkLabel(master=self, text="", font=FONT18)
        self.download_status.grid(row=6, column=0, padx=PADX, pady=10)

    def select_folder(self) -> None:
        self.folder = ctk.filedialog.askdirectory()
        self.folder_label.configure(text=f'Pasta selecionada: "{self.folder}"')

    def download_music(self) -> None:
        # Check if the user filled all information
        if not (link := self.link_entry.get()):
            self.download_status.configure(text="Nenhum link foi inserido, insira o link do vídeo!")
            return
        if not self.folder:
            self.download_status.configure(text="Nenhuma pasta foi selecionada, selecione a pasta de destino!")
            return
        
        # Download and convert the video
        self.download_status.configure(text="Baixando...")
        try:
            title = download.download(link, self.folder)
        except RegexMatchError:
            self.download_status.configure(text="Erro no download: Não foi possível encontrar o vídeo!")
            return
        
        self.download_status.configure(text="Convertendo arquivo...")
        if download.convert_to_mp3(self.folder, title):
            self.download_status.configure(text="Conversão concluída\nArquivo baixado com sucesso!")
        else:
            self.download_status.configure(text="Falha na conversão, tente novamente!")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
