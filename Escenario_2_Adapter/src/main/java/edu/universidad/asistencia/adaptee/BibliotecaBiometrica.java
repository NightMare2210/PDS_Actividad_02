package edu.universidad.asistencia.adaptee;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

/**
 * ADAPTEE: Biblioteca del fabricante (no modificable).
 * Su interfaz NO coincide con la que espera el sistema institucional.
 */
public class BibliotecaBiometrica {

    public List<Marcacion> getMarcaciones(long empleadoId, Date desde, Date hasta) {
        // Simulación de datos. En un caso real se consulta el hardware o su SDK.
        List<Marcacion> marcaciones = new ArrayList<>();
        Calendar cal = Calendar.getInstance();
        cal.setTime(desde);
        cal.set(Calendar.HOUR_OF_DAY, 8);
        cal.set(Calendar.MINUTE, 0);
        Date entrada = cal.getTime();

        cal.set(Calendar.HOUR_OF_DAY, 17);
        cal.set(Calendar.MINUTE, 0);
        Date salida = cal.getTime();

        marcaciones.add(new Marcacion(empleadoId, entrada, "ENTRADA"));
        marcaciones.add(new Marcacion(empleadoId, salida, "SALIDA"));
        return marcaciones;
    }
}