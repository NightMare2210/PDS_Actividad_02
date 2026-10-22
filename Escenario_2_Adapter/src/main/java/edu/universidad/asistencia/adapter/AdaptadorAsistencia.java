package edu.universidad.asistencia.adapter;

import edu.universidad.asistencia.adaptee.BibliotecaBiometrica;
import edu.universidad.asistencia.adaptee.Marcacion;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;
import java.util.Optional;

/**
 * ADAPTER (Object Adapter): implementa el Target y compone el Adaptee.
 * Traduce llamadas y transforma datos entre ambos modelos: la biblioteca del
 * fabricante usa java.util.Date; el sistema institucional usa java.time.
 */
public class AdaptadorAsistencia implements AsistenciaTarget {

    private static final String ENTRADA = "ENTRADA";
    private static final String SALIDA = "SALIDA";

    private final BibliotecaBiometrica biblioteca;
    private final ZoneId zona;

    public AdaptadorAsistencia(BibliotecaBiometrica biblioteca) {
        this(biblioteca, ZoneId.systemDefault());
    }

    public AdaptadorAsistencia(BibliotecaBiometrica biblioteca, ZoneId zona) {
        this.biblioteca = biblioteca;
        this.zona = zona;
    }

    @Override
    public Optional<RegistroAsistencia> obtenerRegistro(String idColaborador, LocalDate fecha) {
        // 1. Conversión de tipos: String -> long
        long empleadoId = Long.parseLong(idColaborador);

        // 2. Rango del día completo: LocalDate -> [desde, hasta] en java.util.Date
        Date desde = Date.from(fecha.atStartOfDay(zona).toInstant());
        Date hasta = Date.from(fecha.atTime(LocalTime.MAX).atZone(zona).toInstant()); // 23:59:59.999

        // 3. Delegación al Adaptee
        List<Marcacion> marcaciones = biblioteca.getMarcaciones(empleadoId, desde, hasta);

        // 4. Transformación de datos: List<Marcacion> -> RegistroAsistencia
        LocalTime horaIngreso = null;
        LocalTime horaSalida = null;
        for (Marcacion m : marcaciones) {
            LocalTime hora = m.getTimestamp().toInstant().atZone(zona).toLocalTime();
            if (ENTRADA.equalsIgnoreCase(m.getTipo())) {
                if (horaIngreso == null || hora.isBefore(horaIngreso)) horaIngreso = hora;
            } else if (SALIDA.equalsIgnoreCase(m.getTipo())) {
                if (horaSalida == null || hora.isAfter(horaSalida)) horaSalida = hora;
            }
        }

        // 5. Sin marcaciones reconocidas no hay registro
        if (horaIngreso == null && horaSalida == null) {
            return Optional.empty();
        }
        return Optional.of(new RegistroAsistencia(idColaborador, fecha, horaIngreso, horaSalida));
    }
}
