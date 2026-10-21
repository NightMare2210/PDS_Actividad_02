package edu.universidad.asistencia.adapter;

import edu.universidad.asistencia.adaptee.Marcacion;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("AdaptadorAsistencia - Patrón Adapter")
class AdaptadorAsistenciaTest {

    private BibliotecaBiometricaFake bibliotecaFake;
    private AdaptadorAsistencia adaptador;
    private Date fecha;

    @BeforeEach
    void setUp() {
        bibliotecaFake = new BibliotecaBiometricaFake();
        adaptador = new AdaptadorAsistencia(bibliotecaFake);
        fecha = Date.from(LocalDate.of(2024, 1, 15)
                .atStartOfDay(ZoneId.systemDefault()).toInstant());
    }

    @Test
    @DisplayName("El adaptador implementa la interfaz objetivo (Target)")
    void implementaInterfazTarget() {
        assertTrue(adaptador instanceof AsistenciaTarget);
    }

    @Test
    @DisplayName("Devuelve un RegistroAsistencia no nulo aunque el Adaptee no devuelva nada")
    void devuelveRegistroNoNulo() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        assertNotNull(adaptador.obtenerRegistro("100", fecha));
    }

    @Test
    @DisplayName("Conserva el ID y la fecha recibidos del cliente")
    void conservaIdYFecha() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertEquals("100", r.getIdColaborador());
        assertEquals(fecha, r.getFecha());
    }

    @Test
    @DisplayName("Extrae la hora de ingreso más temprana entre varias ENTRADAS")
    void extraeHoraIngresoMasTemprana() {
        Date entrada1 = crearFecha(2024, 1, 15, 8, 15);
        Date entrada2 = crearFecha(2024, 1, 15, 7, 45);
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, entrada1, "ENTRADA"),
                new Marcacion(100, entrada2, "ENTRADA")
        ));

        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertEquals(entrada2, r.getHoraIngreso());
    }

    @Test
    @DisplayName("Extrae la hora de salida más tardía entre varias SALIDAS")
    void extraeHoraSalidaMasTardia() {
        Date salida1 = crearFecha(2024, 1, 15, 17, 0);
        Date salida2 = crearFecha(2024, 1, 15, 18, 30);
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, salida1, "SALIDA"),
                new Marcacion(100, salida2, "SALIDA")
        ));

        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertEquals(salida2, r.getHoraSalida());
    }

    @Test
    @DisplayName("Devuelve null en ingreso/salida cuando no hay marcaciones")
    void sinMarcacionesDevuelveNulls() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertNull(r.getHoraIngreso());
        assertNull(r.getHoraSalida());
    }

    @Test
    @DisplayName("Ignora marcaciones con tipo distinto a ENTRADA/SALIDA")
    void ignoraTiposDesconocidos() {
        Date ts = crearFecha(2024, 1, 15, 10, 0);
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, ts, "DESCONOCIDO")
        ));

        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertNull(r.getHoraIngreso());
        assertNull(r.getHoraSalida());
    }

    @Test
    @DisplayName("El tipo de marcación es case-insensitive")
    void tipoCaseInsensitive() {
        Date entrada = crearFecha(2024, 1, 15, 8, 0);
        Date salida = crearFecha(2024, 1, 15, 17, 0);
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, entrada, "entrada"),
                new Marcacion(100, salida, "Salida")
        ));

        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertEquals(entrada, r.getHoraIngreso());
        assertEquals(salida, r.getHoraSalida());
    }

    @Test
    @DisplayName("Convierte el ID de String a long antes de llamar al Adaptee")
    void convierteIdALong() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        adaptador.obtenerRegistro("12345", fecha);
        assertEquals(12345L, bibliotecaFake.getLastEmpleadoId());
    }

    @Test
    @DisplayName("Calcula el rango del día completo (00:00:00.000 a 23:59:59.999)")
    void calculaRangoDelDia() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        adaptador.obtenerRegistro("100", fecha);

        Calendar c = Calendar.getInstance();

        c.setTime(bibliotecaFake.getLastDesde());
        assertEquals(0, c.get(Calendar.HOUR_OF_DAY));
        assertEquals(0, c.get(Calendar.MINUTE));
        assertEquals(0, c.get(Calendar.SECOND));
        assertEquals(0, c.get(Calendar.MILLISECOND));

        c.setTime(bibliotecaFake.getLastHasta());
        assertEquals(23, c.get(Calendar.HOUR_OF_DAY));
        assertEquals(59, c.get(Calendar.MINUTE));
        assertEquals(59, c.get(Calendar.SECOND));
        assertEquals(999, c.get(Calendar.MILLISECOND));
    }

    @Test
    @DisplayName("Lanza NumberFormatException con un ID no numérico")
    void idInvalidoLanzaExcepcion() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        assertThrows(NumberFormatException.class,
                () -> adaptador.obtenerRegistro("abc", fecha));
    }

    @Test
    @DisplayName("Invoca al Adaptee exactamente una vez por consulta")
    void llamaAlAdapteeUnaVez() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        adaptador.obtenerRegistro("100", fecha);
        assertEquals(1, bibliotecaFake.getLlamadas());
    }

    @Test
    @DisplayName("Extrae entrada y salida correctamente en la misma consulta")
    void extraeEntradaYSalida() {
        Date entrada = crearFecha(2024, 1, 15, 8, 0);
        Date salida = crearFecha(2024, 1, 15, 17, 0);
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, entrada, "ENTRADA"),
                new Marcacion(100, salida, "SALIDA")
        ));

        RegistroAsistencia r = adaptador.obtenerRegistro("100", fecha);
        assertEquals(entrada, r.getHoraIngreso());
        assertEquals(salida, r.getHoraSalida());
    }

    private static Date crearFecha(int year, int month, int day, int hour, int minute) {
        Calendar c = Calendar.getInstance();
        c.clear();
        c.set(year, month - 1, day, hour, minute, 0);
        return c.getTime();
    }
}