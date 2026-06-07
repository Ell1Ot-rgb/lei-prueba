/* neural/dendrite_power.h */
#ifndef DENDRITE_POWER_H
#define DENDRITE_POWER_H

#include "dendrite_ohm.h"

/* Constantes */
#define P_SCALE_W           102.4f      /* V_max × I_max */
#define V_MAX_V             32.0f
#define I_MAX_A             3.2f

/* Estado de la dendrita de potencia */
typedef struct {
    /* Señales integradas */
    float u_V;              /* Voltaje normalizado */
    float u_I;              /* Corriente normalizada */
    
    /* Salida */
    float P_dend;           /* Potencia en Watts */
    
    /* Pesos (para calibración) */
    float w_V;
    float w_I;
    float K_scale;          /* Factor de escala de calibración */
} dendrite_power_t;

/* Funciones */
void dendrite_power_init(dendrite_power_t *d);
float dendrite_power_compute(dendrite_power_t *d, float V_bus, float I_load);

#endif /* DENDRITE_POWER_H */
