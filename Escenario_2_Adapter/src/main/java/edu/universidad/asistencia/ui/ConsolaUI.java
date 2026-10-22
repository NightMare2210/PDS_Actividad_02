package edu.universidad.asistencia.ui;


import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;

import java.io.PrintStream;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.LocalTime;
import java.util.Optional;
import java.util.Scanner;

/**
 * CLIENTE (interfaz de usuario de consola).
 * Solo depende de la abstracción Target, nunca del Adaptee.
 */
public class ConsolaUI {

    private final AsistenciaTarget servicio;
    private final Scanner scanner;
    private final PrintStream out;
    private final DateTimeFormatter formatoHora = DateTimeFormatter.ofPattern("HH:mm:ss");

    public ConsolaUI(AsistenciaTarget servicio, Scanner scanner, PrintStream out) {
        this.servicio = servicio;
        this.scanner = scanner;
        this.out = out;
    }

    public void iniciar() {
        out.println("============================================");
        out.println("  Sistema de Consulta de Asistencia");
        out.println("============================================");

        while (true) {
            out.print("ID del colaborador (o 'salir' para terminar): ");
            String id = scanner.nextLine().trim();

            if ("salir".equalsIgnoreCase(id)) {
                out.println("Hasta luego.");
                return;
            }
            if (id.isEmpty()) {
                out.println("El ID no puede estar vacío.");
                continue;
            }

            out.print("Fecha (yyyy-MM-dd) [Enter = hoy]: ");
            String fechaStr = scanner.nextLine().trim();

            LocalDate fecha;
            try {
                fecha = fechaStr.isEmpty()
                        ? LocalDate.now()
                        : LocalDate.parse(fechaStr, DateTimeFormatter.ISO_LOCAL_DATE);
            } catch (DateTimeParseException e) {
                out.println("Formato de fecha inválido. Use yyyy-MM-dd.");
                continue;
            }

            try {
                Optional<RegistroAsistencia> registro = servicio.obtenerRegistro(id, fecha);
                if (registro.isPresent()) {
                    imprimir(registro.get());
                } else {
                    out.println("Sin marcaciones para el colaborador " + id + " el " + fecha + ".");
                }
            } catch (NumberFormatException e) {
                out.println("Error: el ID debe ser numérico.");
            } catch (Exception e) {
                out.println("Error al consultar: " + e.getMessage());
            }
        }
    }

    private void imprimir(RegistroAsistencia r) {
        out.println();
        out.println("--- Registro de Asistencia ---");
        out.println("ID Colaborador : " + r.getIdColaborador());
        out.println("Fecha          : " + r.getFecha());
        out.println("Hora Ingreso   : " + formatearHora(r.getHoraIngreso()));
        out.println("Hora Salida    : " + formatearHora(r.getHoraSalida()));
        out.println("------------------------------");
        out.println();
    }

    private String formatearHora(LocalTime hora) {
        return hora == null ? "Sin registro" : formatoHora.format(hora);
    }
}
