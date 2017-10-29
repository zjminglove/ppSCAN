#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <ctime>

#include <immintrin.h>  //AVX
#include <omp.h> //OpenMP

#include <iostream>
#include <vector>
#include <fstream>
#include <set>
#include <atomic> //CAS

#include"graph.h"
#include"unionfind.h"

#define PARA 16

inline void core_detection(Graph *g);

inline bool hub_check_uf(Graph *g, UnionFind *uf, int a);

#ifdef NAIVE
inline int compute_cn(Graph *g, int edge_idx);
#endif

static int NUMT;

using namespace std;