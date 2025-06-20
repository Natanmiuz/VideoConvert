import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.core import VideoConverter
import threading
import os

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        root.title("Convertidor de Video")
        root.geometry("600x400")  
        root.configure(bg="#f5f5f5")
        root.resizable(False, False)
        
        
        self.input_file = ""
        self.output_format = tk.StringVar(value="mp4")
        self.conversion_in_progress = False
        self.status_text = tk.StringVar(value="Listo para comenzar")
        
        #  estilos
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", foreground="#333", font=("Segoe UI", 9))
        self.style.configure("TButton", font=("Segoe UI", 9), padding=6)
        self.style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"))
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c6fbb")
        self.style.configure("TCombobox", padding=5)
        self.style.map("Accent.TButton", background=[("active", "#1a5a9a")])
        self.style.configure("Accent.TButton", background="#2c6fbb", foreground="white")
        
        self.create_widgets()
        
        
        self.converter = VideoConverter(
            log_callback=self.log,
            status_callback=self.update_status_text
        )
    
    def create_widgets(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
           
        title_label = ttk.Label(main_frame, text="CONVERTIDOR DE VIDEO", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
    
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 15))
  
        file_button = ttk.Button(
            file_frame, 
            text="SELECCIONAR VIDEO", 
            command=self.select_file, 
            style="Accent.TButton",
            width=20
        )
        file_button.pack(side=tk.LEFT, padx=(0, 15))

        self.file_label = ttk.Label(
            file_frame, 
            text="Ningún archivo seleccionado",
            wraplength=300,
            style="Bold.TLabel"
        )
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        format_frame = ttk.LabelFrame(main_frame, text="Formato de salida", padding=10)
        format_frame.pack(fill=tk.X, pady=(0, 10))

        formats = ["mp4", "avi", "mov", "mkv"] #Se pueden agregar más formatos si se desea
        for i, fmt in enumerate(formats):
            rb = ttk.Radiobutton(
                format_frame, 
                text=fmt.upper(), 
                variable=self.output_format, 
                value=fmt
            )
            rb.grid(row=0, column=i, padx=10, sticky="w")
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 5))
        
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_text,
            style="Bold.TLabel",
            anchor=tk.CENTER
        )
        self.status_label.pack(fill=tk.X)
        
        #CONVERT 
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        self.convert_button = ttk.Button(
            button_frame, 
            text="CONVERTIR", 
            command=self.start_conversion, 
            style="Accent.TButton",
            width=20
        )
        self.convert_button.pack(pady=10)
        
      
    
        
        self.log_text = tk.Text(
       #     log_frame, 
            height=8, 
            bg="#f8f8f8", 
            fg="#333", 
            font=("Segoe UI", 8),
            relief="flat",
            padx=5,
            pady=5
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    
       # scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
      #  scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
     #   self.log_text.config(yscrollcommand=scrollbar.set)
        
       
        status_bar = ttk.Frame(self.root, height=20)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(
            status_bar, 
            text="Convertidor de Video v1.2", 
            anchor=tk.W,
            font=("Segoe UI", 7),
            foreground="#777"
        ).pack(side=tk.LEFT, padx=10)
    
    def select_file(self):
        if self.conversion_in_progress:
            return
            
        file_path = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=(
                ("Archivos de video", "*.mp4 *.avi *.mov *.mkv *.webm *.flv"),
            )
        )
        
        if file_path:
            self.input_file = file_path
            file_name = os.path.basename(file_path)
            self.file_label.config(text=file_name)
    
    def start_conversion(self):
        if not self.input_file:
            messagebox.showwarning("Seleccione un archivo", "Por favor seleccione un video primero")
            return
            
        if self.conversion_in_progress:
            return
            
        #  nombre dde salida
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        output_ext = self.output_format.get()
        output_dir = os.path.dirname(self.input_file)
        output_path = os.path.join(output_dir, f"{base_name}_convertido.{output_ext}")
        
        # Comprobar si ya existe
        if os.path.exists(output_path):
            overwrite = messagebox.askyesno(
                "Archivo existente",
                f"El archivo '{os.path.basename(output_path)}' ya existe. ¿Desea reemplazarlo?"
            )
            if not overwrite:
                return
        
        #  conversión 
        self.conversion_in_progress = True
        self.convert_button.config(state=tk.DISABLED)
        self.status_text.set("Convirtiendo...")
        
      
        self.log_text.delete(1.0, tk.END)
        self.log(f"Iniciando conversión a {output_ext.upper()}...")
        
       
        thread = threading.Thread(
            target=self.run_conversion, 
            args=(self.input_file, output_path, output_ext),
            daemon=True
        )
        thread.start()
    
    def run_conversion(self, input_path, output_path, output_format):
        success = self.converter.convert_video(
            input_path, 
            output_path, 
            output_format
        )
        self.conversion_in_progress = False
        
        
        self.root.after(0, self.on_conversion_finished, success, output_path)
    
    def on_conversion_finished(self, success, output_path):
        self.convert_button.config(state=tk.NORMAL)
        
        if success:
            self.status_text.set("¡Conversión completada!")
            self.log(f"Archivo convertido: {os.path.basename(output_path)}")
            self.log("Proceso finalizado con éxito")
        else:
            self.status_text.set("Error en la conversión")
    
    def update_status_text(self, status):
        self.status_text.set(status)

    def log(self, message):
        """Agregar un mensaje al registro de salida"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()