/* neural/dendrite_power.c */
#include "dendrite_power.h"
#include <math.h>

void dendrite_power_init(dendrite_power_t *d) {
    d->u_V = 0.0f;
    d->u_I = 0.0f;
    d->P_dend = 0.0f;
    d->w_V = 1.0f;
    d->w_I = 1.0f;
    d->K_scale = 1.25f;  /* Compensación por saturación de tanh */
}

float dendrite_power_compute(dendrite_power_t *d, float V_bus, float I_load) {
    /*
     * Implementación de P = V × I mediante multiplicación neuronal
     * P_dend = K × σ(V/V_max) × σ(I/I_max) × P_scale
     */
    
    /* Paso 1: Normalizar entradas */
    d->u_V = d->w_V * (V_bus / V_MAX_V);
    d->u_I = d->w_I * (I_load / I_MAX_A);
    
    /* Paso 2: Aplicar no-linealidad (multiplicación NMDA-like) */
    float sigma_V = tanhf(d->u_V);
    float sigma_I = tanhf(d->u_I);
    
    /* Paso 3: Multiplicar y escalar */
    float P_normalized = sigma_V * sigma_I;
    
    /* Paso 4: Convertir a Watts con factor de calibración */
    d->P_dend = d->K_scale * P_normalized * P_SCALE_W;
    
    /* Verificación: comparar con cálculo directo para calibración */
    float P_exact = V_bus * I_load;
    float error = fabsf(d->P_dend - P_exact);
    
    /* Auto-calibración del factor K si error es grande */
    if (error > 0.1f * P_exact && P_exact > 1.0f) {
        /* Ajustar K_scale lentamente */
        float K_needed = P_exact / (P_normalized * P_SCALE_W + 1e-6f);
        d->K_scale = 0.99f * d->K_scale + 0.01f * K_needed;
    }
    
    return d->P_dend;
}
