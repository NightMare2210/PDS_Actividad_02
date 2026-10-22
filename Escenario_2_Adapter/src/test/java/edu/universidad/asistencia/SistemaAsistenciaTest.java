package edu.universidad.asistencia;

import edu.universidad.asistencia.adapter.AdaptadorAsistencia;
import edu.universidad.asistencia.adapter.BibliotecaBiometricaFake;
import edu.universidad.asistencia.adaptee.Marcacion;
import edu.universidad.asistencia.dispositivo.DispositivoProveedorActual;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("SistemaAsistencia - varios proveedores detrás del mismo Target")
class SistemaAsistenciaTest {

    private static final ZoneId ZONA = ZoneId.of("America/Guayaquil");
    private static final LocalDate FECHA = LocalDate.of(2024, 1, 15);

    private DispositivoProveedorActual proveedorActual;
    private BibliotecaBiometricaFake bibliotecaFake;

    @BeforeEach
    void setUp() {
        proveedorActual = new DispositivoProveedorActual();
        proveedorActual.registrar(new RegistroAsistencia("200", FECHA, LocalTime.of(7, 45), LocalTime.of(16, 30)));
        bibliotecaFake = new BibliotecaBiometricaFake();
        bibliotecaFake.configurarRespuesta(List.of(
                new Marcacion(300, Date.from(FECHA.atTime(8, 0).atZone(ZONA).toInstant()), "ENTRADA")));
    }

    @Test
    @DisplayName("Resuelve con el proveedor actual sin tocar al nuevo")
    void usaProveedorActual() {
        SistemaAsistencia sistema = new SistemaAsistencia(
                List.of(proveedorActual, new AdaptadorAsistencia(bibliotecaFake, ZONA)));
        assertEquals(LocalTime.of(7, 45), sistema.obtenerRegistro("200", FECHA).orElseThrow().getHoraIngreso());
        assertEquals(0, bibliotecaFake.getLlamadas());
    }

    @Test
    @DisplayName("Si el proveedor actual no lo conoce, consulta al nuevo mediante el adaptador")
    void usaNuevoProveedor() {
        SistemaAsistencia sistema = new SistemaAsistencia(
                List.of(proveedorActual, new AdaptadorAsistencia(bibliotecaFake, ZONA)));
        assertEquals(LocalTime.of(8, 0), sistema.obtenerRegistro("300", FECHA).orElseThrow().getHoraIngreso());
    }

    @Test
    @DisplayName("Devuelve vacío si ningún dispositivo tiene marcaciones")
    void ningunoTieneMarcaciones() {
        assertTrue(new SistemaAsistencia(Collections.singletonList(proveedorActual))
                .obtenerRegistro("999", FECHA).isEmpty());
    }

    @Test
    @DisplayName("Un tercer proveedor se incorpora sin modificar el sistema")
    void tercerProveedor() {
        AsistenciaTarget futuro = (id, fecha) ->
                Optional.of(new RegistroAsistencia(id, fecha, LocalTime.of(6, 0), null));
        SistemaAsistencia sistema = new SistemaAsistencia(List.of(proveedorActual, futuro));
        assertEquals(LocalTime.of(6, 0), sistema.obtenerRegistro("777", FECHA).orElseThrow().getHoraIngreso());
    }
}
