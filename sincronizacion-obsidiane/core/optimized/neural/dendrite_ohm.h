/* neural/dendrite_ohm.h */
#ifndef DENDRITE_OHM_H
#define DENDRITE_OHM_H

#include <stdint.h>

/* Constantes físicas del INA219 */
#define R_SHUNT_OHM         0.1f
#define LSB_SHUNT_UV        78.125f
#define I_MAX_A             3.2f
#define K_OHM               1280.0f     /* R_shunt / LSB_shunt */

/* Parámetros del kernel sináptico */
#define TAU_SYN_MS          10.0f       /* Constante de tiempo */
#define KERNEL_SAMPLES      100         /* Muestras del kernel */

typedef struct {
    float spike_times[KERNEL_SAMPLES];
    int spike_idx;
    int spike_count;
    float u_V;      /* Voltaje integrado */
    float I_dend;   /* Salida */
    float w_V;      /* Peso sináptico */
} dendrite_ohm_t;

void dendrite_ohm_init(dendrite_ohm_t *d);
void dendrite_ohm_add_spike(dendrite_ohm_t *d, float t_spike);
float dendrite_ohm_compute(dendrite_ohm_t *d, float t_now);

#endif /* DENDRITE_OHM_H */
