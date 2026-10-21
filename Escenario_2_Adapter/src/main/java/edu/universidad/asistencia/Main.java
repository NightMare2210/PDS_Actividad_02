package edu.universidad.asistencia;

import edu.universidad.asistencia.adapter.AdaptadorAsistencia;
import edu.universidad.asistencia.adaptee.BibliotecaBiometrica;
import edu.universidad.asistencia.target.AsistenciaTarget;
import edu.universidad.asistencia.ui.ConsolaUI;

import java.util.Scanner;

/**
 * Punto de entrada. Ensambla el patrón Adapter:
 *   Cliente -> Target <- Adapter -> Adaptee
 */
public class Main {
    public static void main(String[] args) {
        // Adaptee (biblioteca del fabricante, no modificable)
        BibliotecaBiometrica biblioteca = new BibliotecaBiometrica();

        // Adapter: expone la interfaz Target sobre el Adaptee
        AsistenciaTarget servicio = new AdaptadorAsistencia(biblioteca);

        // Cliente: usa solo la interfaz Target
        ConsolaUI ui = new ConsolaUI(servicio, new Scanner(System.in), System.out);
        ui.iniciar();
    }
}