package edu.universidad.asistencia.target;

import edu.universidad.asistencia.domain.RegistroAsistencia;

import java.util.Date;

/**
 * TARGET: Contrato estable que espera el sistema institucional.
 * Es la interfaz que el cliente conoce y utiliza.
 */
public interface AsistenciaTarget {
    RegistroAsistencia obtenerRegistro(String idColaborador, Date fecha);
}