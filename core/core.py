import subprocess
import os
import threading

class VideoConverter:
    def __init__(self, log_callback=None, status_callback=None):
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.process = None
        self.running = False

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def update_status(self, status):
        if self.status_callback:
            self.status_callback(status)

    def check_ffmpeg_installed(self):
        try:
            subprocess.run(["ffmpeg", "-version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except FileNotFoundError:
            self.log("Error: FFmpeg no está instalado en el sistema.")
            return False

    def convert_video(self, input_path, output_path, output_format):  # quality
        if not self.check_ffmpeg_installed():
            return False

        # ============================================================
        # No pude hacer que los parámetros de calidad afecten la conversión
        #
        # quality_settings = {
        #     "muy alta": {"crf": "18", "preset": "slow"},
        #     "alta": {"crf": "23", "preset": "medium"},
        #     "media": {"crf": "28", "preset": "fast"},
        #     "baja": {"crf": "35", "preset": "veryfast"}
        # }
        #
        # crf = quality_settings.get(quality, {}).get("crf", "23")
        # preset = quality_settings.get(quality, {}).get("preset", "medium")
        #
        # se produce un error. dejar comentado hasta resolverlo
        # =============================================================

        self.running = True
        self.update_status("Iniciando conversión...")
        self.log(f"Convirtiendo: {os.path.basename(input_path)}")
        self.log(f"Formato destino: {output_format.upper()}")

        try:
            command = [
                "ffmpeg",
                "-i", input_path,
                "-c:v", "libx264",
                # "-crf", "23",    #  no funciona
                # "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "192k",
                "-y",  # Sobrescribir
                output_path
            ]
            
            # FFmpeg
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            
            for line in self.process.stdout:
                if not self.running:
                    break
                self.log(line.strip())
            
           
            self.process.wait()
            
            if self.process.returncode == 0:
                self.log("Conversión completada con éxito!")
                self.update_status("Conversión completada")
                return True
            else:
                self.log(f"Error en la conversión (código {self.process.returncode})")
                self.update_status("Error en la conversión")
                return False
        
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.update_status("Error en la conversión")
            return False
        finally:
            self.running = False

