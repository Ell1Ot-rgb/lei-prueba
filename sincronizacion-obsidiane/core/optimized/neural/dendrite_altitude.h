/* neural/dendrite_altitude.h */
#ifndef DENDRITE_ALTITUDE_H
#define DENDRITE_ALTITUDE_H

/* Constantes físicas */
#define T0_K            288.15f         /* Temperatura estándar [K] */
#define L_LAPSE         0.0065f         /* Tasa de lapso [K/m] */
#define P0_PA           101325.0f       /* Presión estándar [Pa] */
#define P0_HPA          1013.25f        /* Presión estándar [hPa] */
#define ALPHA           0.1903f         /* Exponente barométrico */
#define K_ALT           44330.77f       /* T0/L [m] */

typedef struct {
    float u_P;              /* Presión integrada [hPa] */
    float u_T;              /* Temperatura integrada [K] */
    float h_dend;           /* Altitud calculada [m] */
    float P_reference;      /* Presión de referencia local */
    float h_reference;      /* Altitud conocida de referencia */
    float K_scale;          /* Factor de calibración */
} dendrite_altitude_t;

void dendrite_altitude_init(dendrite_altitude_t *d);
void dendrite_altitude_set_reference(dendrite_altitude_t *d, float P_hPa, float h_known);
float dendrite_altitude_compute(dendrite_altitude_t *d, float P_hPa, float T_celsius);
float dendrite_altitude_exact(float P_hPa, float T_celsius);

#endif /* DENDRITE_ALTITUDE_H */
