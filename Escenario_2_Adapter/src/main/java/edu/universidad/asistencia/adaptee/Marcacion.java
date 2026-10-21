package edu.universidad.asistencia.adaptee;


import java.util.Date;

/**
 * Estructura propia del fabricante (no modificable).
 */
public class Marcacion {
    private final long empleadoId;
    private final Date timestamp;
    private final String tipo; // "ENTRADA" o "SALIDA"

    public Marcacion(long empleadoId, Date timestamp, String tipo) {
        this.empleadoId = empleadoId;
        this.timestamp = timestamp;
        this.tipo = tipo;
    }

    public long getEmpleadoId() { return empleadoId; }
    public Date getTimestamp() { return timestamp; }
    public String getTipo() { return tipo; }
}