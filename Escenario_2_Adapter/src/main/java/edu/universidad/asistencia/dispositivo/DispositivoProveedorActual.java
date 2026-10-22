package edu.universidad.asistencia.dispositivo;

import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Dispositivo del proveedor anterior: ya trabaja con el contrato institucional,
 * por lo que implementa el Target directamente y no necesita adaptador.
 */
public class DispositivoProveedorActual implements AsistenciaTarget {

    private final Map<String, RegistroAsistencia> registros = new HashMap<>();

    public void registrar(RegistroAsistencia registro) {
        registros.put(clave(registro.getIdColaborador(), registro.getFecha()), registro);
    }

    @Override
    public Optional<RegistroAsistencia> obtenerRegistro(String idColaborador, LocalDate fecha) {
        return Optional.ofNullable(registros.get(clave(idColaborador, fecha)));
    }

    private static String clave(String id, LocalDate fecha) {
        return id + "|" + fecha;
    }
}
