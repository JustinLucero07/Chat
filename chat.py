import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import asyncio
import websockets

clientes_tcp = []
clientes_ws = set()
loop_asyncio = None  # Para guardar el loop asyncio principal

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

        self.iniciar_servidor_tcp()

    def iniciar_servidor_tcp(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(5)

        self.escribir_en_historial("Servidor TCP escuchando en puerto 12345...")

        threading.Thread(target=self.aceptar_clientes_tcp, daemon=True).start()

    def aceptar_clientes_tcp(self):
        while True:
            cliente_socket, addr = self.server_socket.accept()
            clientes_tcp.append(cliente_socket)
            self.escribir_en_historial(f"Cliente TCP conectado desde {addr}")
            threading.Thread(target=self.manejar_cliente_tcp, args=(cliente_socket,), daemon=True).start()

    def manejar_cliente_tcp(self, cliente_socket):
        while True:
            try:
                data = cliente_socket.recv(1024).decode()
                if not data:
                    break
                self.escribir_en_historial(f"TCP: {data}")
                self.reenviar_a_todos(f"TCP: {data}", origen=cliente_socket)
            except Exception as e:
                # Podrías loguear e si quieres: print("Error TCP:", e)
                break
        cliente_socket.close()
        if cliente_socket in clientes_tcp:
            clientes_tcp.remove(cliente_socket)
        self.escribir_en_historial("Cliente TCP desconectado.")

    def reenviar_a_todos(self, mensaje, origen=None):
        # Reenviar a clientes TCP
        for cliente in clientes_tcp:
            try:
                if cliente != origen:
                    cliente.send(mensaje.encode())
            except:
                pass

        # Reenviar a clientes WebSocket
        async def enviar_ws():
            for ws in list(clientes_ws):
                try:
                    if ws != origen:
                        await ws.send(mensaje)
                except:
                    pass

        if loop_asyncio:
            asyncio.run_coroutine_threadsafe(enviar_ws(), loop_asyncio)

    def enviar_a_todos(self):
        mensaje = self.entrada_mensaje.get()
        if mensaje:
            mensaje_completo = f"Servidor: {mensaje}"
            self.escribir_en_historial(mensaje_completo)
            self.reenviar_a_todos(mensaje_completo)
            self.entrada_mensaje.delete(0, tk.END)

    def escribir_en_historial(self, mensaje):
        def append():
            self.historial.config(state='normal')
            self.historial.insert(tk.END, mensaje + "\n")
            self.historial.config(state='disabled')
            self.historial.yview(tk.END)
        self.master.after(0, append)

# ============ WEBSOCKET SERVER ============

async def websocket_handler(websocket):
    clientes_ws.add(websocket)
    app.escribir_en_historial("Cliente WebSocket conectado.")
    try:
        async for mensaje in websocket:
            app.escribir_en_historial(f"WebSocket: {mensaje}")
            # Al reenviar, prefijo para que TCP también lo muestre con claridad
            app.reenviar_a_todos(f"WebSocket: {mensaje}", origen=websocket)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clientes_ws.discard(websocket)
        app.escribir_en_historial("Cliente WebSocket desconectado.")

async def iniciar_servidor_websocket():
    async with websockets.serve(websocket_handler, "localhost", 8765):
        app.escribir_en_historial("Servidor WebSocket activo en ws://localhost:8765")
        await asyncio.Future()  # Espera infinita para mantener activo

def iniciar_event_loop():
    global loop_asyncio
    loop_asyncio = asyncio.new_event_loop()
    asyncio.set_event_loop(loop_asyncio)
    loop_asyncio.run_until_complete(iniciar_servidor_websocket())

# ============ MAIN ============

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorChat(root)

    threading.Thread(target=iniciar_event_loop, daemon=True).start()

    root.mainloop()
