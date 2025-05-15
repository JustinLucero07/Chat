import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

clientes = []

class ServidorChat:
    def __init__(self, master):
        self.master = master
        self.master.title("Servidor Chat")
        self.master.geometry("500x400")

        self.historial = ScrolledText(master, state='disabled')
        self.historial.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entrada_mensaje = tk.Entry(master)
        self.entrada_mensaje.pack(fill=tk.X, padx=10, pady=5)

        self.boton_enviar = tk.Button(master, text="Enviar a todos", command=self.enviar_a_todos)
        self.boton_enviar.pack(pady=5)

        self.iniciar_servidor()

    def iniciar_servidor(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(5)

        self.escribir_en_historial("Servidor escuchando en puerto 12345...")

        threading.Thread(target=self.aceptar_clientes, daemon=True).start()

    def aceptar_clientes(self):
        while True:
            cliente_socket, addr = self.server_socket.accept()
            clientes.append(cliente_socket)
            self.escribir_en_historial(f"Cliente conectado desde {addr}")
            threading.Thread(target=self.manejar_cliente, args=(cliente_socket,), daemon=True).start()

    def manejar_cliente(self, cliente_socket):
        while True:
            try:
                data = cliente_socket.recv(1024).decode()
                if not data:
                    break
                self.escribir_en_historial(data)
                self.reenviar_a_todos(data, cliente_socket)
            except:
                break
        cliente_socket.close()
        clientes.remove(cliente_socket)
        self.escribir_en_historial("Un cliente se ha desconectado.")

    def reenviar_a_todos(self, mensaje, origen):
        for cliente in clientes:
            if cliente != origen:
                try:
                    cliente.send(mensaje.encode())
                except:
                    pass  # Cliente caído

    def enviar_a_todos(self):
        mensaje = self.entrada_mensaje.get()
        if mensaje:
            mensaje_completo = f"Servidor: {mensaje}"
            self.escribir_en_historial(mensaje_completo)
            for cliente in clientes:
                try:
                    cliente.send(mensaje_completo.encode())
                except:
                    pass
            self.entrada_mensaje.delete(0, tk.END)

    def escribir_en_historial(self, mensaje):
        self.historial.config(state='normal')
        self.historial.insert(tk.END, mensaje + "\n")
        self.historial.config(state='disabled')
        self.historial.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorChat(root)
    root.mainloop()
