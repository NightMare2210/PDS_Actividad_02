package edu.universidad.asistencia.target;

import edu.universidad.asistencia.domain.RegistroAsistencia;

import java.time.LocalDate;
import java.util.Optional;

/**
 * TARGET: Contrato estable que espera el sistema institucional.
 * Es la interfaz que el cliente conoce y utiliza.
 * Devuelve un Optional vacío si el colaborador no tiene marcaciones en la fecha.
 */
public interface AsistenciaTarget {
    Optional<RegistroAsistencia> obtenerRegistro(String idColaborador, LocalDate fecha);
}
