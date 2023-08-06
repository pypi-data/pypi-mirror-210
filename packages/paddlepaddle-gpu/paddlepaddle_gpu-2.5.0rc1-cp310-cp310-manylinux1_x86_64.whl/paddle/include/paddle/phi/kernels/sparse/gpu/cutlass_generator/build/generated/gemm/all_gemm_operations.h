#pragma once
#ifdef PADDLE_WITH_CUTLASS
#include "paddle/phi/kernels/sparse/gpu/cutlass_generator/common.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_256x128_32x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x256_32x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_256x64_32x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_256x64_32x4_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x256_32x4_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x128_32x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x128_32x4_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x128_32x5_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x64_32x6_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x128_32x6_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x64_32x10_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_256x128_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x256_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_256x64_64x4_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x256_64x4_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x128_64x4_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_256x64_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x256_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x128_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_128x64_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x128_64x3_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_h16816gemm_64x64_64x5_nn_align8.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x256_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x64_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x256_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x5_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x64_16x6_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x128_16x6_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x64_16x10_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x256_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x64_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x256_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x64_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x64_32x5_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x256_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x64_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x256_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x5_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x64_16x6_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x128_16x6_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x64_16x10_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x256_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x64_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x256_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x64_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x64_32x5_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x256_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x64_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x256_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x5_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x64_16x6_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x128_16x6_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x64_16x10_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x256_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_256x64_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x256_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_128x64_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_tf32_64x64_32x5_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x256_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x64_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x256_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x5_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x64_16x6_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x128_16x6_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x64_16x10_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x256_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x64_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x256_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x64_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x64_32x5_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x256_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x64_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x256_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x5_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x64_16x6_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x128_16x6_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x64_16x10_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x256_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x64_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x256_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x64_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x64_32x5_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x256_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x64_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x256_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x5_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x64_16x6_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x128_16x6_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x64_16x10_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x256_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_256x64_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x256_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_128x64_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_tf32_s1688gemm_tf32_64x64_32x5_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x256_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x64_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x256_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x5_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x64_16x6_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x128_16x6_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x64_16x10_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x256_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x64_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x256_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_32x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x64_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x64_32x5_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x256_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x64_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x256_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x5_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x64_16x6_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x128_16x6_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x64_16x10_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x256_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x64_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x256_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_32x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x64_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x64_32x5_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x256_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x64_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x256_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x5_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x64_16x6_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x128_16x6_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x64_16x10_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x256_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_256x64_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x256_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_32x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_128x64_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688tf32gemm_64x64_32x5_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_256x64_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x256_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x64_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x128_16x4_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x64_16x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_256x64_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x256_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x64_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x128_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x64_32x3_nn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_256x64_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x256_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x64_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x128_16x4_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x64_16x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_256x64_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x256_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x64_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x128_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x64_32x3_nt_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_256x64_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x256_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x64_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x128_16x4_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x64_16x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_256x64_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x256_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_128x64_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x128_32x3_tn_align4.h"
#include "/paddle/paddle/phi/kernels/sparse/gpu/cutlass_generator/build/generated/gemm/cutlass_tensorop_s1688gemm_64x64_32x3_tn_align4.h"

namespace phi {
namespace sparse {
static std::vector<fp16_gather_gemm_scatter> fp16_nn_kernels = {
launchKernel<cutlass_tensorop_h16816gemm_256x128_32x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x256_32x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_256x64_32x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_256x64_32x4_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x256_32x4_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x128_32x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x128_32x4_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x128_32x5_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x64_32x6_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x128_32x6_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x64_32x10_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_256x128_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x256_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_256x64_64x4_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x256_64x4_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x128_64x4_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_256x64_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x256_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x128_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_128x64_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x128_64x3_nn_align8<>>,
launchKernel<cutlass_tensorop_h16816gemm_64x64_64x5_nn_align8<>>,
};
static std::vector<fp32_gather_gemm_scatter> fp32_nn_kernels = {
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x256_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x64_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x256_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x5_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x64_16x6_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x128_16x6_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x64_16x10_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x256_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x64_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x256_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x64_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x64_32x5_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x256_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x64_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x256_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x5_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x64_16x6_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x128_16x6_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x64_16x10_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x256_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x64_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x256_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x64_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x64_32x5_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x256_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x64_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x256_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x5_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x64_16x6_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x128_16x6_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x64_16x10_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x256_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x64_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x256_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_32x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x64_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x64_32x5_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_256x64_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x256_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x64_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x128_16x4_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x64_16x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_256x64_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x256_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x64_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x128_32x3_nn_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x64_32x3_nn_align4<>>,
};
static std::vector<fp32_gather_gemm_scatter> fp32_nt_kernels = {
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x256_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x64_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x256_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x5_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x64_16x6_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x128_16x6_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x64_16x10_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x256_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x64_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x256_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x64_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x64_32x5_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x256_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x64_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x256_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x5_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x64_16x6_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x128_16x6_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x64_16x10_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x256_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x64_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x256_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x64_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x64_32x5_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x256_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x64_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x256_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x5_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x64_16x6_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x128_16x6_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x64_16x10_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x256_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x64_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x256_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_32x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x64_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x64_32x5_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_256x64_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x256_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x64_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x128_16x4_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x64_16x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_256x64_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x256_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_128x64_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x128_32x3_nt_align4<>>,
launchKernel<cutlass_tensorop_s1688gemm_64x64_32x3_nt_align4<>>,
};
static std::vector<fp32_gather_gemm_scatter> fp32_tn_kernels = {
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x256_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x64_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x256_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x5_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x64_16x6_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x128_16x6_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x64_16x10_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x256_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_256x64_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x256_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_128x64_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_tf32_64x64_32x5_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x256_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x64_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x256_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x5_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x64_16x6_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x128_16x6_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x64_16x10_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x256_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_256x64_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x256_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_128x64_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_tf32_s1688gemm_tf32_64x64_32x5_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x256_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x64_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x256_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x5_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x64_16x6_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x128_16x6_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x64_16x10_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x256_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_256x64_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x256_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_32x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_128x64_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688tf32gemm_64x64_32x5_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_256x64_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_64x256_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_128x64_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_64x128_16x4_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_64x64_16x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_128x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_256x64_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_64x256_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_128x64_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_64x128_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
launchKernel<cutlass_tensorop_s1688gemm_64x64_32x3_tn_align4<cutlass::gemm::GemmUniversalMode::kGemmSplitKParallel>>,
};

}  // namespace sparse
}  // namespace phi
#endif
