/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.chat;

/**
 *
 * @author Justin7
 */
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.net.*;

public class ClienteChat extends JFrame {
    private JTextArea areaMensajes;
    private JTextField campoTexto;
    private JButton botonEnviar;
    private BufferedWriter salida;
    private BufferedReader entrada;
    private Socket socket;
    private String nombreCliente;

    public ClienteChat(String nombreCliente) {
        this.nombreCliente = nombreCliente;
        configurarInterfaz();
        conectarAlServidor();
        recibirMensajes();
    }

    private void configurarInterfaz() {
        setTitle("Cliente: " + nombreCliente);
        setSize(400, 300);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        areaMensajes = new JTextArea();
        areaMensajes.setEditable(false);
        add(new JScrollPane(areaMensajes), BorderLayout.CENTER);

        JPanel panelInferior = new JPanel();
        campoTexto = new JTextField(20);
        botonEnviar = new JButton("Enviar");

        panelInferior.add(campoTexto);
        panelInferior.add(botonEnviar);
        add(panelInferior, BorderLayout.SOUTH);

        botonEnviar.addActionListener(e -> enviarMensaje());
        campoTexto.addActionListener(e -> enviarMensaje());

        setVisible(true);
    }

    private void conectarAlServidor() {
        try {
            socket = new Socket("localhost", 12345);
            salida = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
            entrada = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            areaMensajes.append("Conectado al servidor\n");
        } catch (IOException e) {
            mostrarError("No se pudo conectar al servidor.");
        }
    }

    private void enviarMensaje() {
        String mensaje = campoTexto.getText();
        if (!mensaje.isEmpty()) {
            try {
                salida.write(nombreCliente + ": " + mensaje);
                salida.newLine();
                salida.flush();
                campoTexto.setText("");
            } catch (IOException e) {
                mostrarError("Error al enviar el mensaje.");
            }
        }
    }

    private void recibirMensajes() {
        Thread hilo = new Thread(() -> {
            String mensaje;
            try {
                while ((mensaje = entrada.readLine()) != null) {
                    areaMensajes.append(mensaje + "\n");
                }
            } catch (IOException e) {
                mostrarError("Conexión cerrada.");
            }
        });
        hilo.start();
    }

    private void mostrarError(String mensaje) {
        JOptionPane.showMessageDialog(this, mensaje, "Error", JOptionPane.ERROR_MESSAGE);
    }
}

