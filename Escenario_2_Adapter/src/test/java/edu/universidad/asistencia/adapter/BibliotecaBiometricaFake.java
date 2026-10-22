package edu.universidad.asistencia.adapter;

import edu.universidad.asistencia.adaptee.BibliotecaBiometrica;
import edu.universidad.asistencia.adaptee.Marcacion;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * Test double (Fake) para aislar el adaptador del hardware real.
 * Se apoya en herencia porque la clase original no es final.
 */
public class BibliotecaBiometricaFake extends BibliotecaBiometrica {

    private List<Marcacion> respuesta = new ArrayList<>();
    private long lastEmpleadoId;
    private Date lastDesde;
    private Date lastHasta;
    private int llamadas = 0;

    public void configurarRespuesta(List<Marcacion> marcaciones) {
        this.respuesta = marcaciones;
    }

    @Override
    public List<Marcacion> getMarcaciones(long empleadoId, Date desde, Date hasta) {
        this.llamadas++;
        this.lastEmpleadoId = empleadoId;
        this.lastDesde = desde;
        this.lastHasta = hasta;
        return respuesta;
    }

    public long getLastEmpleadoId() { return lastEmpleadoId; }
    public Date getLastDesde() { return lastDesde; }
    public Date getLastHasta() { return lastHasta; }
    public int getLlamadas() { return llamadas; }
}
