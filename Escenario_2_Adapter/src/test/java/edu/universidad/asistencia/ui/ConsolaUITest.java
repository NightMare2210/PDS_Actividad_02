package edu.universidad.asistencia.ui;

import edu.universidad.asistencia.adapter.AdaptadorAsistencia;
import edu.universidad.asistencia.adapter.BibliotecaBiometricaFake;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.time.LocalTime;
import java.util.Collections;
import java.util.Optional;
import java.util.Scanner;

import static org.junit.jupiter.api.Assertions.assertTrue;

@DisplayName("ConsolaUI - Interfaz de consola")
class ConsolaUITest {

    private static String ejecutar(AsistenciaTarget servicio, String entrada) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        new ConsolaUI(servicio, new Scanner(entrada), new PrintStream(baos)).iniciar();
        return baos.toString();
    }

    @Test
    @DisplayName("Muestra el registro tras una consulta exitosa")
    void muestraRegistroTrasConsulta() {
        // Fake de AsistenciaTarget mediante lambda (interfaz funcional)
        AsistenciaTarget servicioFake = (id, fecha) ->
                Optional.of(new RegistroAsistencia(id, fecha, LocalTime.MIDNIGHT, null));

        String salida = ejecutar(servicioFake, "100\n2024-01-15\nsalir\n");

        assertTrue(salida.contains("ID Colaborador : 100"));
        assertTrue(salida.contains("Fecha          : 2024-01-15"));
        assertTrue(salida.contains("Hora Ingreso   : 00:00:00"));
        assertTrue(salida.contains("Hora Salida    : Sin registro"));
    }

    @Test
    @DisplayName("Informa cuando no hay marcaciones")
    void informaSinMarcaciones() {
        String salida = ejecutar((id, fecha) -> Optional.empty(), "100\n2024-01-15\nsalir\n");
        assertTrue(salida.contains("Sin marcaciones para el colaborador 100"));
    }

    @Test
    @DisplayName("Termina correctamente al escribir 'salir'")
    void terminaConSalir() {
        assertTrue(ejecutar((id, fecha) -> Optional.empty(), "salir\n").contains("Hasta luego."));
    }

    @Test
    @DisplayName("Informa error si el ID no es numérico (con el adaptador real)")
    void informaErrorIdNoNumerico() {
        BibliotecaBiometricaFake fake = new BibliotecaBiometricaFake();
        fake.configurarRespuesta(Collections.emptyList());
        String salida = ejecutar(new AdaptadorAsistencia(fake), "abc\n2024-01-15\nsalir\n");
        assertTrue(salida.contains("el ID debe ser numérico"));
    }

    @Test
    @DisplayName("Informa error si la fecha tiene formato inválido")
    void informaFechaInvalida() {
        String salida = ejecutar((id, fecha) -> Optional.empty(), "100\n15/01/2024\nsalir\n");
        assertTrue(salida.contains("Formato de fecha inválido"));
    }
}
