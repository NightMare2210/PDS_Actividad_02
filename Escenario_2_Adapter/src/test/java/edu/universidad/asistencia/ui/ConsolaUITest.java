package edu.universidad.asistencia.ui;

import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.util.Date;
import java.util.Scanner;

import static org.junit.jupiter.api.Assertions.assertTrue;

@DisplayName("ConsolaUI - Interfaz de consola")
class ConsolaUITest {

    @Test
    @DisplayName("Muestra el registro tras una consulta exitosa")
    void muestraRegistroTrasConsulta() {
        // Fake de AsistenciaTarget mediante lambda (interfaz funcional)
        AsistenciaTarget servicioFake = (id, fecha) ->
                new RegistroAsistencia(id, fecha, new Date(0), null);

        String entrada = "100\n2024-01-15\nsalir\n";
        Scanner scanner = new Scanner(entrada);
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PrintStream out = new PrintStream(baos);

        ConsolaUI ui = new ConsolaUI(servicioFake, scanner, out);
        ui.iniciar();

        String salida = baos.toString();
        assertTrue(salida.contains("ID Colaborador : 100"));
        assertTrue(salida.contains("Fecha          : 2024-01-15"));
        assertTrue(salida.contains("Hora Ingreso   : 00:00:00"));
        assertTrue(salida.contains("Hora Salida    : Sin registro"));
    }

    @Test
    @DisplayName("Termina correctamente al escribir 'salir'")
    void terminaConSalir() {
        String entrada = "salir\n";
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ConsolaUI ui = new ConsolaUI(
                (id, fecha) -> new RegistroAsistencia(id, fecha, null, null),
                new Scanner(entrada),
                new PrintStream(baos)
        );
        ui.iniciar();
        assertTrue(baos.toString().contains("Hasta luego."));
    }

    @Test
    @DisplayName("Informa error si el ID no es numérico")
    void informaErrorIdNoNumerico() {
        AsistenciaTarget servicioReal = (id, fecha) -> {
            Long.parseLong(id); // provoca NumberFormatException
            return null;
        };
        String entrada = "abc\n2024-01-15\nsalir\n";
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ConsolaUI ui = new ConsolaUI(servicioReal, new Scanner(entrada), new PrintStream(baos));
        ui.iniciar();
        assertTrue(baos.toString().contains("el ID debe ser numérico"));
    }
}