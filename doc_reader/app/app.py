import os
from functools import partial
from nicegui import ui, native
from nicegui.events import UploadEventArguments, ValueChangeEventArguments
from doc_reader.app.app_components import TextLoader, TextProcessor, Text2Audio
import doc_reader.app.config as c


class App:
    def __init__(self):
        self.APPNAME = "Lector de temas"
        self.audio = []
        self.velocity = 1.5
        self.speaker = None
        self.name = None
        self.device = c.DEVICE
        self.txt2audio = Text2Audio(device=c.DEVICE)
        self.txt_processor = TextProcessor()

        with ui.expansion("Opciones").classes('w-full'):
            with ui.row().classes("w-full"):
                ui.number(label="Velocidad",
                          placeholder=str(self.velocity),
                          value=1.5,
                          min=0.25, max=4, step=0.25,
                          on_change=self.handle_velocity)
                ui.select(self.txt2audio.get_available_models(language=c.LANGUAGE),
                          label="Modelo TTS", value=c.MODEL_NAMES[0],
                          on_change=self.handle_model)
                ui.select(c.SPEAKERS, value=c.SPEAKERS[0],
                          label="Speakers",
                          on_change=self.handle_speaker)
        with ui.expansion("Conversiones de texto").classes('w-full'):
            with ui.row().classes("w-full"):
                self.key_input = ui.input(label="Original", on_change=self.check_inputs)
                self.value_input = ui.input(label="Transformado", on_change=self.check_inputs)
                self.chip_up = (
                    ui.chip("Actualizar",
                            on_click=partial(self.handle_update_txtconv,  save=False)
                            )
                    .tooltip("Actualiza el par clave: valor para esta sesión")
                )
                self.chip_save = (
                    ui.chip("Actualizar y guardar",
                            on_click=partial(self.handle_update_txtconv, save=True)
                            )
                    .tooltip("Actualiza el par clave: valor para esta sesión y las posteriores")
                )
                self.chip_up.disable()
                self.chip_save.disable()
        ui.upload(multiple=True,
                  on_upload=self.handle_upload,
                  auto_upload=True).classes('w-full')

    def check_inputs(self):
        if self.key_input.value and self.value_input.value:
            self.chip_up.enable()
            self.chip_save.enable()
        else:
            self.chip_up.disable()
            self.chip_save.disable()

    def handle_update_txtconv(self, save: bool = False):
        self.txt_processor.update_text_conversions({self.key_input.value: self.value_input.value})
        self.key_input.value = ""
        self.value_input.value = ""
        if save:
            self.txt_processor.save_text_conversions(c.TEXT_CONVERSIONS_PATH)

    def handle_model(self, model_name: ValueChangeEventArguments):
        self.txt2audio.set_model(model_name=model_name.value)

    def handle_speaker(self, speaker: ValueChangeEventArguments):
        self.speaker = os.path.join(c.SPEAKER_DIR, speaker.value + '.wav')

    def handle_velocity(self, velocity: ValueChangeEventArguments):
        sample_rate = velocity.value * c.MODEL_SAMPLE_RATE_OUT
        self.velocity = velocity.value
        self.txt2audio.sample_rate = sample_rate

    def handle_upload(self, file: UploadEventArguments):
        self.name = file.name
        text = self.txt_processor.process(TextLoader.load_file(file))
        self.txt2audio.text_to_file(text=text,
                                    file_name=self.name.replace(self.name.split(".")[-1],
                                                                "wav"),
                                    speaker_wav_path=self.speaker,
                                    speed=self.velocity)

    def run_app(self):
        ui.run(
            native=True, reload=False, port=native.find_open_port(),
            dark=True, title=self.APPNAME)
