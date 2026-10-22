package edu.universidad.asistencia;

import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Sistema institucional: consulta varios dispositivos solo a través del Target,
 * sin saber de qué proveedor es cada uno. Incorporar un proveedor nuevo es
 * agregar otro dispositivo a la lista; esta clase no cambia.
 */
public class SistemaAsistencia implements AsistenciaTarget {

    private final List<AsistenciaTarget> dispositivos;

    public SistemaAsistencia(List<AsistenciaTarget> dispositivos) {
        this.dispositivos = List.copyOf(dispositivos);
    }

    @Override
    public Optional<RegistroAsistencia> obtenerRegistro(String idColaborador, LocalDate fecha) {
        for (AsistenciaTarget dispositivo : dispositivos) {
            Optional<RegistroAsistencia> registro = dispositivo.obtenerRegistro(idColaborador, fecha);
            if (registro.isPresent()) {
                return registro;
            }
        }
        return Optional.empty();
    }
}
