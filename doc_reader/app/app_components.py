import os
from typing import Optional, List, Tuple, Mapping
import subprocess
import re
import json
import warnings
import docx
import fitz
from TTS.api import TTS
from num2words import num2words
from nicegui.events import UploadEventArguments
from doc_reader.app.utils import get_download_folder
import doc_reader.app.config as c


class TextLoader:
    @classmethod
    def _assertions(cls, filename: str, typ: str):
        assert filename.endswith(f'.{typ}'), f'File {filename} must be a .docx file'

    @classmethod
    def load_file(cls, file: UploadEventArguments) -> str:
        if file.name.endswith('docx'):
            return cls.load_from_docx(file)
        elif file.name.endswith('.pdf'):
            return cls.load_from_pdf(file)
        else:
            raise AssertionError(f'Path must be a .docx or .pdf file. Got .{file.name.split(".")[-1]}')

    @classmethod
    def load_from_docx(cls, file: UploadEventArguments) -> str:
        """
        Loads text from .docx file
        :param file: Upload Event from Nice Gui
        :return: str
        """
        cls._assertions(file.name, 'docx')
        doc = docx.Document(file.content)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '. '.join(text)

    @classmethod
    def load_from_pdf(cls, file: UploadEventArguments) -> str:
        """
        Loads text from .pdf file
        :param file: Upload Event from Nice Gui
        :return: str
        """
        cls._assertions(file.name, 'pdf')
        with fitz.open(stream=file.content.read()) as doc:
            text = ""
            for page in doc:
                text += page.get_text().replace('\n', ' ')
        return text


class TextProcessor:
    ROMAN_NUMERALS = {"I": 1,
                      "V": 5,
                      "X": 10,
                      "L": 50,
                      "C": 100,
                      "D": 500,
                      "M": 1000}

    def __init__(self,
                 language: str = c.LANGUAGE,
                 text_conversions_path: str = c.TEXT_CONVERSIONS_PATH):
        self.language = language
        self.txt_conv = {}
        if os.path.exists(text_conversions_path):
            self._get_text_conversions(text_conversions_path=text_conversions_path)
        else:
            warnings.warn(f"Couldn't find text_conversions.json from {text_conversions_path}")

    @staticmethod
    def _standarize_text(text: str):
        return text.lower()

    def _get_text_conversions(self, text_conversions_path: str):
        with open(text_conversions_path, 'r', encoding="utf-8") as f:
            self.txt_conv = json.load(f)

    def update_text_conversions(self, mapping: Mapping):
        self.txt_conv.update(mapping)

    def save_text_conversions(self, text_conversions_path: str):
        with open(text_conversions_path, 'w', encoding='utf8') as f:
            json.dump(self.txt_conv, f, ensure_ascii=False)

    def _apply_text_conversions(self, text: str) -> str:
        self.txt_conv = dict(sorted(self.txt_conv.items(), key=lambda l: len(l[0])))
        pattern = re.compile('|'.join(fr'\b\.*{k}\.*\b' for k in self.txt_conv.keys()))
        return pattern.sub(lambda x: self.txt_conv[x.group()], text)

    def _roman_numeral_to_srtint(self, roman_numeral: str) -> str:
        """
        Given a roman numeral returns its integer as string
        :param roman_numeral: Roman number
        :return: String representation of associated integer.
        """
        if len(roman_numeral) == 0:
            return ""
        int_value = 0
        for i in range(len(roman_numeral)):
            if (
                    (i + 1 < len(roman_numeral)) and
                    (self.ROMAN_NUMERALS[roman_numeral[i]] < self.ROMAN_NUMERALS[roman_numeral[i + 1]])
            ):
                int_value -= self.ROMAN_NUMERALS[roman_numeral[i]]
            else:
                int_value += self.ROMAN_NUMERALS[roman_numeral[i]]
        return str(int_value)

    def _process_number(self,
                        str_number: str,
                        delete_chars: Optional[Tuple[str]] = None,
                        split: Optional[Tuple[Tuple[str, str], ...]] = None) -> str:
        """
        Converts a number to its phoneme representation
        :param str_number: number to convert
        :param delete_chars: tuple of chars to delete
        :param split: tuple of tuples like (split_char, phoneme_repr)
        :return: string representation
        """
        if delete_chars and any(dc in str_number for dc in delete_chars):
            str_number = str_number.translate(str_number.maketrans({k: '' for k in delete_chars}))
        if split and any(sp in str_number for sp in dict(split)):
            str_number = str_number.translate(str_number.maketrans(dict(split)))
            return re.sub(r"\d+", lambda x: self._process_number(x.group(), delete_chars, split),
                          str_number)
        return num2words(number=str_number, ordinal=False, lang=self.language)

    def _numbers2phoneme(self, text):
        """
        Converts all type of numbers to its phoneme representation
        :param text: text with numbers
        :return: text without numbers
        """
        text = text.replace("/", " barra ").replace("%", " porciento")
        # Laws
        text = re.sub(r"\d+/\d+\.*\d+",
                      lambda x: self._process_number(x.group(),
                                                     delete_chars=(',',),
                                                     split=(('.', ' punto '),)),
                      text)
        # Articles
        text = re.sub(r"([aA][rR][tT][ií]*\w*.?\s+)[\d.*]+",
                      lambda x: self._process_number(x.group(),
                                                     delete_chars=(',',),
                                                     split=(('.', ' punto '),)),
                      text)
        # ROMAN NUMBERS
        text = re.sub(r"\bM{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b",
                      lambda x: self._roman_numeral_to_srtint(x.group()), text)
        # Numbers
        text = re.sub(r"\d*[.,]*\d+",
                      lambda x: self._process_number(x.group(),
                                                     delete_chars=('.',),
                                                     split=((',', ' coma '),)), text)
        return text

    def process(self, text: str) -> str:
        return self._standarize_text(self._numbers2phoneme(self._apply_text_conversions(text)))


class Text2Audio:
    def __init__(self,
                 model_name: str = c.MODEL_NAMES[0],
                 language: str = c.LANGUAGE,
                 sample_rate: int = c.MODEL_SAMPLE_RATE_OUT,
                 device: str = c.DEVICE):
        self.speaker = None
        self.model_name = model_name
        self.language = language
        self.sample_rate = sample_rate
        self.device = device
        self.tts = self._initialize_tts(model_name=self.model_name)

    @staticmethod
    def get_available_models(language: Optional[str] = None) -> List[str]:
        model_names = TTS.list_models()
        if language:
            return [mn for mn in model_names if f"/{language}/" in mn]
        return model_names

    def _initialize_tts(self, model_name: str) -> TTS:
        try:
            tts = TTS(model_name).to(self.device)
        except json.decoder.JSONDecodeError:
            subprocess.run("rm -rf ~/.cache/tts")
            tts = TTS(model_name).to(self.device)
        return tts

    def set_model(self, model_name: str):
        self.tts = self._initialize_tts(model_name=model_name)

    def get_tts_speakers(self) -> List[str]:
        return self.tts.speakers

    def get_tts_languages(self) -> List[str]:
        return self.tts.languages

    def text_to_wav(self, text: str,
                    speaker_wav_path: Optional[str] = None):
        if speaker_wav_path and not speaker_wav_path.endswith(".wav"):
            speaker_wav_path += ".wav"
        return self.tts.tts(
            text=text,
            speaker=self.speaker,
            speaker_wav=speaker_wav_path if self.speaker is not None else None,
            language=self.language if self.tts.is_multi_lingual else None
        )

    def text_to_file(self, text: str,
                     file_name: str,
                     speaker_wav_path: Optional[str] = None,
                     speed: Optional[float] = 1.0):

        if speaker_wav_path and not speaker_wav_path.endswith(".wav"):
            speaker_wav_path += ".wav"
        self.tts.tts_to_file(text=text,
                             speaker=self.speaker,
                             speaker_wav=speaker_wav_path if self.speaker is not None else None,
                             language=self.language if self.tts.is_multi_lingual else None,
                             speed=speed,
                             file_path=os.path.join(get_download_folder(), file_name))
