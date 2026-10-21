package edu.universidad.asistencia.domain;

import java.util.Date;

/**
 * DTO normalizado que devuelve el contrato (Target).
 */
public class RegistroAsistencia {
    private final String idColaborador;
    private final Date fecha;
    private final Date horaIngreso;
    private final Date horaSalida;

    public RegistroAsistencia(String idColaborador, Date fecha, Date horaIngreso, Date horaSalida) {
        this.idColaborador = idColaborador;
        this.fecha = fecha;
        this.horaIngreso = horaIngreso;
        this.horaSalida = horaSalida;
    }

    public String getIdColaborador() { return idColaborador; }
    public Date getFecha() { return fecha; }
    public Date getHoraIngreso() { return horaIngreso; }
    public Date getHoraSalida() { return horaSalida; }

    @Override
    public String toString() {
        return "RegistroAsistencia{" +
                "id='" + idColaborador + '\'' +
                ", fecha=" + fecha +
                ", ingreso=" + horaIngreso +
                ", salida=" + horaSalida +
                '}';
    }
}