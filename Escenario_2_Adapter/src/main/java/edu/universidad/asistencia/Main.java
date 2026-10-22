package edu.universidad.asistencia;

import edu.universidad.asistencia.adapter.AdaptadorAsistencia;
import edu.universidad.asistencia.dispositivo.DispositivoProveedorActual;
import edu.universidad.asistencia.adaptee.BibliotecaBiometrica;
import edu.universidad.asistencia.domain.RegistroAsistencia;
import edu.universidad.asistencia.target.AsistenciaTarget;
import edu.universidad.asistencia.ui.ConsolaUI;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Scanner;

/**
 * Punto de entrada. Ensambla el patrón Adapter:
 *   Cliente -> Target <- Adapter -> Adaptee
 * y un dispositivo del proveedor anterior que implementa el Target directamente.
 */
public class Main {
    public static void main(String[] args) {
        // Proveedor anterior: ya cumple el contrato
        DispositivoProveedorActual proveedorActual = new DispositivoProveedorActual();
        proveedorActual.registrar(new RegistroAsistencia("200", LocalDate.of(2024, 1, 15),
                LocalTime.of(7, 45), LocalTime.of(16, 30)));

        // Adaptee (biblioteca del fabricante, no modificable) envuelto por el Adapter
        AsistenciaTarget nuevoProveedor = new AdaptadorAsistencia(new BibliotecaBiometrica());

        // Cliente: usa solo la interfaz Target
        AsistenciaTarget servicio = new SistemaAsistencia(List.of(proveedorActual, nuevoProveedor));
        new ConsolaUI(servicio, new Scanner(System.in), System.out).iniciar();
    }
}
