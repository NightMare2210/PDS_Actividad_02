package edu.universidad.asistencia.domain;

import java.time.LocalDate;
import java.time.LocalTime;

/**
 * DTO normalizado que devuelve el contrato (Target).
 * Una hora nula significa que no existe la marcación correspondiente.
 */
public class RegistroAsistencia {
    private final String idColaborador;
    private final LocalDate fecha;
    private final LocalTime horaIngreso;
    private final LocalTime horaSalida;

    public RegistroAsistencia(String idColaborador, LocalDate fecha, LocalTime horaIngreso, LocalTime horaSalida) {
        this.idColaborador = idColaborador;
        this.fecha = fecha;
        this.horaIngreso = horaIngreso;
        this.horaSalida = horaSalida;
    }

    public String getIdColaborador() { return idColaborador; }
    public LocalDate getFecha() { return fecha; }
    public LocalTime getHoraIngreso() { return horaIngreso; }
    public LocalTime getHoraSalida() { return horaSalida; }

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
