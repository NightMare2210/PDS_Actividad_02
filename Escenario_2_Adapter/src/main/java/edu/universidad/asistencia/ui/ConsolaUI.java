package edu.universidad.asistencia.ui;


import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;

import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Date;
import java.util.Scanner;

/**
 * CLIENTE (interfaz de usuario de consola).
 * Solo depende de la abstracción Target, nunca del Adaptee.
 */
public class ConsolaUI {

    private final AsistenciaTarget servicio;
    private final Scanner scanner;
    private final PrintStream out;
    private final SimpleDateFormat sdfHora = new SimpleDateFormat("HH:mm:ss");
    private final SimpleDateFormat sdfFecha = new SimpleDateFormat("yyyy-MM-dd");

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

            Date fecha;
            try {
                LocalDate localDate = fechaStr.isEmpty()
                        ? LocalDate.now()
                        : LocalDate.parse(fechaStr, DateTimeFormatter.ISO_LOCAL_DATE);
                fecha = Date.from(localDate.atStartOfDay(ZoneId.systemDefault()).toInstant());
            } catch (DateTimeParseException e) {
                out.println("Formato de fecha inválido. Use yyyy-MM-dd.");
                continue;
            }

            try {
                RegistroAsistencia registro = servicio.obtenerRegistro(id, fecha);
                imprimir(registro);
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
        out.println("Fecha          : " + sdfFecha.format(r.getFecha()));
        out.println("Hora Ingreso   : " + formatearHora(r.getHoraIngreso()));
        out.println("Hora Salida    : " + formatearHora(r.getHoraSalida()));
        out.println("------------------------------");
        out.println();
    }

    private String formatearHora(Date hora) {
        return hora == null ? "Sin registro" : sdfHora.format(hora);
    }
}
