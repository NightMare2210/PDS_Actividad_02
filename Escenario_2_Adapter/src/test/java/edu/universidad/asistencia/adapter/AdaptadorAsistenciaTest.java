package edu.universidad.asistencia.adapter;

import edu.universidad.asistencia.adaptee.Marcacion;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("AdaptadorAsistencia - Patrón Adapter")
class AdaptadorAsistenciaTest {

    private static final ZoneId ZONA = ZoneId.of("America/Guayaquil");
    private static final LocalDate FECHA = LocalDate.of(2024, 1, 15);

    private BibliotecaBiometricaFake bibliotecaFake;
    private AdaptadorAsistencia adaptador;

    @BeforeEach
    void setUp() {
        bibliotecaFake = new BibliotecaBiometricaFake();
        adaptador = new AdaptadorAsistencia(bibliotecaFake, ZONA);
    }

    @Test
    @DisplayName("El adaptador implementa la interfaz objetivo (Target)")
    void implementaInterfazTarget() {
        assertTrue(adaptador instanceof AsistenciaTarget);
    }

    @Test
    @DisplayName("Devuelve Optional vacío cuando el Adaptee no devuelve marcaciones")
    void sinMarcacionesDevuelveVacio() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        assertTrue(adaptador.obtenerRegistro("100", FECHA).isEmpty());
    }

    @Test
    @DisplayName("Conserva el ID y la fecha recibidos del cliente")
    void conservaIdYFecha() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(new Marcacion(100, fecha(8, 0), "ENTRADA")));
        RegistroAsistencia r = adaptador.obtenerRegistro("100", FECHA).orElseThrow();
        assertEquals("100", r.getIdColaborador());
        assertEquals(FECHA, r.getFecha());
    }

    @Test
    @DisplayName("Extrae la hora de ingreso más temprana entre varias ENTRADAS")
    void extraeHoraIngresoMasTemprana() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, fecha(8, 15), "ENTRADA"),
                new Marcacion(100, fecha(7, 45), "ENTRADA")
        ));
        RegistroAsistencia r = adaptador.obtenerRegistro("100", FECHA).orElseThrow();
        assertEquals(LocalTime.of(7, 45), r.getHoraIngreso());
    }

    @Test
    @DisplayName("Extrae la hora de salida más tardía entre varias SALIDAS")
    void extraeHoraSalidaMasTardia() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, fecha(17, 0), "SALIDA"),
                new Marcacion(100, fecha(18, 30), "SALIDA")
        ));
        RegistroAsistencia r = adaptador.obtenerRegistro("100", FECHA).orElseThrow();
        assertEquals(LocalTime.of(18, 30), r.getHoraSalida());
        assertNull(r.getHoraIngreso());
    }

    @Test
    @DisplayName("Una entrada sin salida deja la hora de salida en null")
    void entradaSinSalida() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(new Marcacion(100, fecha(9, 0), "ENTRADA")));
        RegistroAsistencia r = adaptador.obtenerRegistro("100", FECHA).orElseThrow();
        assertEquals(LocalTime.of(9, 0), r.getHoraIngreso());
        assertNull(r.getHoraSalida());
    }

    @Test
    @DisplayName("Ignora marcaciones con tipo distinto a ENTRADA/SALIDA")
    void ignoraTiposDesconocidos() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(new Marcacion(100, fecha(10, 0), "DESCONOCIDO")));
        assertTrue(adaptador.obtenerRegistro("100", FECHA).isEmpty());
    }

    @Test
    @DisplayName("El tipo de marcación es case-insensitive")
    void tipoCaseInsensitive() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, fecha(8, 0), "entrada"),
                new Marcacion(100, fecha(17, 0), "Salida")
        ));
        RegistroAsistencia r = adaptador.obtenerRegistro("100", FECHA).orElseThrow();
        assertEquals(LocalTime.of(8, 0), r.getHoraIngreso());
        assertEquals(LocalTime.of(17, 0), r.getHoraSalida());
    }

    @Test
    @DisplayName("Convierte el ID de String a long antes de llamar al Adaptee")
    void convierteIdALong() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        adaptador.obtenerRegistro("12345", FECHA);
        assertEquals(12345L, bibliotecaFake.getLastEmpleadoId());
    }

    @Test
    @DisplayName("Calcula el rango del día completo (00:00:00.000 a 23:59:59.999)")
    void calculaRangoDelDia() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        adaptador.obtenerRegistro("100", FECHA);

        LocalDateTime desde = LocalDateTime.ofInstant(bibliotecaFake.getLastDesde().toInstant(), ZONA);
        LocalDateTime hasta = LocalDateTime.ofInstant(bibliotecaFake.getLastHasta().toInstant(), ZONA);
        assertEquals(FECHA.atStartOfDay(), desde);
        assertEquals(FECHA.atTime(23, 59, 59, 999_000_000), hasta);
    }

    @Test
    @DisplayName("Lanza NumberFormatException con un ID no numérico")
    void idInvalidoLanzaExcepcion() {
        assertThrows(NumberFormatException.class, () -> adaptador.obtenerRegistro("abc", FECHA));
        assertEquals(0, bibliotecaFake.getLlamadas());
    }

    @Test
    @DisplayName("Invoca al Adaptee exactamente una vez por consulta")
    void llamaAlAdapteeUnaVez() {
        bibliotecaFake.configurarRespuesta(Collections.emptyList());
        adaptador.obtenerRegistro("100", FECHA);
        assertEquals(1, bibliotecaFake.getLlamadas());
    }

    @Test
    @DisplayName("Extrae entrada y salida correctamente en la misma consulta")
    void extraeEntradaYSalida() {
        bibliotecaFake.configurarRespuesta(Arrays.asList(
                new Marcacion(100, fecha(8, 0), "ENTRADA"),
                new Marcacion(100, fecha(17, 0), "SALIDA")
        ));
        Optional<RegistroAsistencia> r = adaptador.obtenerRegistro("100", FECHA);
        assertEquals(LocalTime.of(8, 0), r.orElseThrow().getHoraIngreso());
        assertEquals(LocalTime.of(17, 0), r.orElseThrow().getHoraSalida());
    }

    private static Date fecha(int hora, int minuto) {
        return Date.from(FECHA.atTime(hora, minuto).atZone(ZONA).toInstant());
    }
}
