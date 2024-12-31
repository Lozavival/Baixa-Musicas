import sys
from typing import Any, Tuple

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from pathvalidate import sanitize_filename
from PIL import Image, ImageTk
from pytubefix.exceptions import RegexMatchError

import download

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

FONT16 = ("Inter", 16)
FONT18 = ("Inter", 18)
FONT20 = ("Inter", 20)
PADX = 10

ASSETS_PATH = "assets\\" if sys.platform.startswith('win32') else "assets/"


class MyImage(ctk.CTkLabel):
    def __init__(self, master: Any, path: str, rotation: float = 0, size: Tuple[int, int] = (20, 20), **kwargs):
        super().__init__(master, text="", **kwargs)

        img = Image.open(path).rotate(rotation)
        self.configure(image=ctk.CTkImage(dark_image=img, size=size))


class MyLabel(ctk.CTkLabel):
    def __init__(self, master: Any, text: str, font: Tuple[str, int] = FONT18, **kwargs):
        super().__init__(master, text=text, font=font, **kwargs)
    
    def configure(self, **kwargs):
        super().configure(**kwargs)
        self.update()


class App(ctk.CTk):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.title("Baixa-Músicas")
        self.iconphoto(False, ImageTk.PhotoImage(Image.open(ASSETS_PATH + "icon.ico")))
        self.resizable(False, False)
        self.folder = ""

        # Link input
        self.link_listener = ctk.StringVar()
        self.link_listener.trace_add("write", self.toggle_resolution_selection)

        self.link_label = ctk.CTkLabel(master=self,
                                       text="Insira o link da música no Youtube:",
                                       font=FONT20)
        self.link_label.grid(row=0, column=0, columnspan=3,
                             padx=PADX, pady=10, sticky="w")

        self.link_entry = ctk.CTkEntry(self, width=750, font=FONT16, textvariable=self.link_listener)
        self.link_entry.bind("<Control-a>", self.select_all)
        self.link_entry.bind("<Return>", self.download_music)
        self.link_entry.grid(row=1, column=0, columnspan=3,
                             padx=PADX, pady=(0, 20))

        # Audio/video selection
        self.only_audio = ctk.IntVar(self, value=1)
        self.type_select = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_btn_audio = ctk.CTkRadioButton(
            master=self.type_select,
            text="Baixar apenas áudio",
            font=FONT16,
            value=1,
            variable=self.only_audio,
            command=self.toggle_resolution_selection)
        self.radio_btn_both = ctk.CTkRadioButton(
            master=self.type_select,
            text="Baixar áudio e vídeo",
            font=FONT16,
            value=0,
            variable=self.only_audio,
            command=self.toggle_resolution_selection)
        self.radio_btn_audio.pack(pady=(0,7.5))
        self.radio_btn_both.pack()
        self.type_select.grid(row=2, column=0, padx=PADX, pady=(10, 20), sticky="w")

        # Video resolution selection
        self.resolution_select = ctk.CTkFrame(self, fg_color="transparent")
        self.resolution_label = MyLabel(master=self.resolution_select,
                                             text="Selecione a resolução do vídeo:",
                                             font=FONT18)
        self.resolution_box = ctk.CTkComboBox(master=self.resolution_select, values=[], state="readonly", font=FONT16)
        self.resolution_label.pack(anchor="e")

        # Folder selection
        self.folder_button = ctk.CTkButton(master=self,
                                           text="Escolher pasta",
                                           font=FONT20,
                                           command=self.select_folder)
        self.folder_button.grid(row=3, column=0,
                                padx=PADX, pady=10, sticky="w")

        self.folder_label = MyLabel(master=self,
                                    text="<nenhuma pasta selecionada>",
                                    font=FONT18)
        self.folder_label.grid(row=4, column=0, columnspan=3,
                               padx=PADX, pady=(0, 20), sticky="w")

        # Clean inputs button
        self.clear_button = ctk.CTkButton(master=self,
                                          text="Limpar",
                                          font=FONT20,
                                          command=self.clean_inputs)
        self.clear_button.grid(row=3, column=2, padx=PADX, pady=10, sticky="e")

        # Start download and status
        self.download_button = ctk.CTkButton(master=self,
                                             text="Baixar",
                                             font=FONT20,
                                             command=self.download_music)
        self.download_button.grid(row=6, column=1, padx=PADX)

        self.download_status = MyLabel(master=self, text="", font=FONT18)
        self.download_status.grid(row=7, column=0, columnspan=3, padx=PADX, pady=10)

        # GUI decoration
        img1 = MyImage(self, ASSETS_PATH + "nota-musical-dupla.png", size=(75, 75))
        img1.grid(row=5, column=0, rowspan=2)

        img2 = MyImage(self, ASSETS_PATH + "nota-musical.png", -15, (64, 64))
        img2.grid(row=5, column=2, rowspan=2)
    
    def toggle_resolution_selection(self, *args) -> None:
        # Check if the user inserted a valid link
        try:
            yt = download.YTDownload(self.link_entry.get())
        except RegexMatchError:
            return

        # Show resolution selection
        if not self.only_audio.get():
            self.resolution_select.grid(row=2, column=1, columnspan=2, padx=PADX, sticky="ne")
            self.resolution_label.configure(text="Buscando resoluções...")

            # TODO: solve delay
            resolutions = yt.get_all_resolutions()
            self.resolution_box.configure(values=resolutions)
            self.resolution_box.set(resolutions[0])

            self.resolution_label.configure(text="Selecione a resolução do vídeo:")
            self.resolution_box.pack(anchor="e")
        else:
            self.resolution_box.pack_forget()
            self.resolution_select.grid_forget()
    
    def select_all(self, event):
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')
        return 'break'

    def select_folder(self) -> None:
        self.folder = ctk.filedialog.askdirectory()
        self.folder_label.configure(text=f'Pasta selecionada: "{self.folder}"')

    def clean_inputs(self) -> None:
        self.link_entry.delete(0, ctk.END)
        self.download_status.configure(text="")

    def download_music(self, event=None) -> None:
        # Check if the user filled all information
        if not (link := self.link_entry.get()):
            self.download_status.configure(
                text="Nenhum link foi inserido, insira o link do vídeo!")
            return
        if not self.folder:
            self.download_status.configure(
                text="Nenhuma pasta foi selecionada, selecione a pasta de destino!")
            return

        # Get user settings
        only_audio = self.only_audio.get()
        resolution = self.resolution_box.get()

        # Check if the user inserted a valid link
        try:
            yt = download.YTDownload(link)
        except RegexMatchError:
            self.download_status.configure(text="Erro no download: Não foi possível encontrar o vídeo!")
            return

        # Ask for filename confirmation
        filename = ctk.filedialog.asksaveasfilename(
            confirmoverwrite=True,
            initialfile=sanitize_filename(yt.title),
            initialdir=self.folder,
            filetypes=[("Arquivo de áudio", "*.mp3")] if only_audio else [("Arquivo de vídeo", "*.mp4")],
        )
        if not filename:
            CTkMessagebox(
                title="Download cancelado",
                message="Download cancelado!",
                icon="info",
                font=FONT16
            )
            return

        # Download and convert the video
        self.download_status.configure(text="Baixando...")
        if only_audio:
            filepath = yt.download_audio(filename, overwrite=True)
            self.download_status.configure(text="Download concluído\nConvertendo arquivo...")
            if yt.convert_to_mp3(filepath):
                self.download_status.configure(text="Conversão concluída\nArquivo baixado com sucesso!")
            else:                
                self.download_status.configure(text="Falha na conversão, tente novamente!")
        else:
            yt.download_video(filename, resolution, overwrite=True)
            self.download_status.configure(text="Download concluído\nArquivo baixado com sucesso!")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
