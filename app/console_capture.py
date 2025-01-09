import sys
import threading
from queue import Queue
import re

class ConsoleCapture:
    def __init__(self):
        self.output_queue = Queue()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self._lock = threading.Lock()
        self._line_buffer = ""
        self.active = False
        # Pattern pro veškeré ANSI a speciální znaky
        self.clean_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-9;]*[ -/]*[@-~])|[\x00-\x1F\x7F-\x9F]')

    def clean_text(self, text):
        """Odstraní všechny ANSI a kontrolní znaky"""
        return self.clean_pattern.sub('', text)
        #return text

    def start(self):
        with self._lock:
            sys.stdout = self
            sys.stderr = self
            self.active = True

    def stop(self):
        with self._lock:
            if self.active:
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
                if self._line_buffer:
                    cleaned_text = self.clean_text(self._line_buffer)
                    if cleaned_text:
                        self.output_queue.put(cleaned_text)
                    self._line_buffer = ""
                self.active = False

    def write(self, text):
        with self._lock:
            if self.active:
                self.original_stdout.write(text)
                self._line_buffer += text
                
                while '\n' in self._line_buffer:
                    line, self._line_buffer = self._line_buffer.split('\n', 1)
                    if line:
                        cleaned_line = self.clean_text(line)
                        if cleaned_line:
                            self.output_queue.put(cleaned_line)
                
                self.original_stdout.flush()

    def flush(self):
        with self._lock:
            if self.active:
                self.original_stdout.flush()

    def get_output(self):
        messages = []
        with self._lock:
            while not self.output_queue.empty():
                messages.append(self.output_queue.get_nowait())
        return messages