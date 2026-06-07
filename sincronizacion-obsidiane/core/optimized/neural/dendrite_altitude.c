/* neural/dendrite_altitude.c */
#include "dendrite_altitude.h"
#include <math.h>

void dendrite_altitude_init(dendrite_altitude_t *d) {
    d->u_P = P0_HPA;
    d->u_T = T0_K;
    d->h_dend = 0.0f;
    d->P_reference = P0_HPA;
    d->h_reference = 0.0f;
    d->K_scale = 1.0f;
}

void dendrite_altitude_set_reference(dendrite_altitude_t *d, float P_hPa, float h_known) {
    d->P_reference = P_hPa;
    d->h_reference = h_known;
}

float dendrite_altitude_exact(float P_hPa, float T_celsius) {
    /*
     * Fórmula barométrica exacta:
     * h = (T/L) × [1 - (P/P₀)^α]
     */
    float T_K = T_celsius + 273.15f;
    float P_Pa = P_hPa * 100.0f;
    
    /* Ratio de presión */
    float p_ratio = P_Pa / P0_PA;
    
    /* Término exponencial: p^α = exp(α × ln(p)) */
    float exp_term = expf(ALPHA * logf(p_ratio));
    
    /* Altitud con corrección de temperatura */
    return (T_K / L_LAPSE) * (1.0f - exp_term);
}

float dendrite_altitude_compute(dendrite_altitude_t *d, float P_hPa, float T_celsius) {
    d->u_P = P_hPa;
    d->u_T = T_celsius + 273.15f;
    
    /* Calcular altitud absoluta */
    float h_absolute = dendrite_altitude_exact(P_hPa, T_celsius);
    
    /* Calcular altitud de referencia */
    float h_ref_calc = dendrite_altitude_exact(d->P_reference, T_celsius);
    
    /* Altitud relativa respecto a referencia conocida */
    d->h_dend = d->h_reference + (h_absolute - h_ref_calc);
    d->h_dend *= d->K_scale;
    
    return d->h_dend;
}
