/* neural/dendrite_ohm.c */
#include "dendrite_ohm.h"
#include <math.h>

static float synaptic_kernel(float t, float tau) {
    if (t < 0) return 0.0f;
    float t_norm = t / tau;
    return t_norm * expf(-t_norm) / tau;
}

void dendrite_ohm_init(dendrite_ohm_t *d) {
    for (int i = 0; i < KERNEL_SAMPLES; i++) d->spike_times[i] = -1000.0f;
    d->spike_idx = 0;
    d->spike_count = 0;
    d->u_V = 0.0f;
    d->I_dend = 0.0f;
    d->w_V = 1.0f;
}

void dendrite_ohm_add_spike(dendrite_ohm_t *d, float t_spike) {
    d->spike_times[d->spike_idx] = t_spike;
    d->spike_idx = (d->spike_idx + 1) % KERNEL_SAMPLES;
    if (d->spike_count < KERNEL_SAMPLES) d->spike_count++;
}

float dendrite_ohm_compute(dendrite_ohm_t *d, float t_now) {
    /* Paso 1: Integrar spikes */
    d->u_V = 0.0f;
    float tau = TAU_SYN_MS / 1000.0f;
    
    for (int i = 0; i < d->spike_count; i++) {
        float dt = t_now - d->spike_times[i];
        if (dt >= 0 && dt < 10 * tau) {
            d->u_V += d->w_V * synaptic_kernel(dt, tau);
        }
    }
    
    /* Paso 2: Ley de Ohm con saturación */
    /* I_linear = u_V * LSB / R */
    float I_linear = d->u_V * (LSB_SHUNT_UV * 1e-6f) / R_SHUNT_OHM;
    d->I_dend = I_MAX_A * tanhf(I_linear / I_MAX_A);
    
    return d->I_dend;
}
