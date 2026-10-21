package edu.universidad.asistencia.adapter;

import edu.universidad.asistencia.adaptee.BibliotecaBiometrica;
import edu.universidad.asistencia.adaptee.Marcacion;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;

import java.util.Calendar;
import java.util.Date;
import java.util.List;

/**
 * ADAPTER (Object Adapter): implementa el Target y compone el Adaptee.
 * Traduce llamadas y transforma datos entre ambos modelos.
 */
public class AdaptadorAsistencia implements AsistenciaTarget {

    private final BibliotecaBiometrica biblioteca;

    public AdaptadorAsistencia(BibliotecaBiometrica biblioteca) {
        this.biblioteca = biblioteca;
    }

    @Override
    public RegistroAsistencia obtenerRegistro(String idColaborador, Date fecha) {
        // 1. Conversión de tipos: String -> long
        long empleadoId = Long.parseLong(idColaborador);

        // 2. Cálculo del rango del día completo
        Calendar cal = Calendar.getInstance();
        cal.setTime(fecha);
        cal.set(Calendar.HOUR_OF_DAY, 0);
        cal.set(Calendar.MINUTE, 0);
        cal.set(Calendar.SECOND, 0);
        cal.set(Calendar.MILLISECOND, 0);
        Date desde = cal.getTime();

        cal.set(Calendar.HOUR_OF_DAY, 23);
        cal.set(Calendar.MINUTE, 59);
        cal.set(Calendar.SECOND, 59);
        cal.set(Calendar.MILLISECOND, 999);
        Date hasta = cal.getTime();

        // 3. Delegación al Adaptee
        List<Marcacion> marcaciones = biblioteca.getMarcaciones(empleadoId, desde, hasta);

        // 4. Transformación de datos: List<Marcacion> -> RegistroAsistencia
        Date horaIngreso = null;
        Date horaSalida = null;

        for (Marcacion m : marcaciones) {
            if ("ENTRADA".equalsIgnoreCase(m.getTipo())) {
                if (horaIngreso == null || m.getTimestamp().before(horaIngreso)) {
                    horaIngreso = m.getTimestamp();
                }
            } else if ("SALIDA".equalsIgnoreCase(m.getTipo())) {
                if (horaSalida == null || m.getTimestamp().after(horaSalida)) {
                    horaSalida = m.getTimestamp();
                }
            }
        }

        // 5. Devolución del objeto normalizado que espera el cliente
        return new RegistroAsistencia(idColaborador, fecha, horaIngreso, horaSalida);
    }
}