#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>
#include <string.h>


#define US_IN_S 1000000
#define EGM96MAXN 360 // Maximum degree and order for the EGM96 gravity model

uint64_t GetTimeStamp() {
    struct timeval tv;
    gettimeofday(&tv,NULL);
    return tv.tv_sec*(uint64_t)1000000+tv.tv_usec;
}

uint64_t dt;
void tic() {
    dt = GetTimeStamp();
}

void toc() {
    printf("Elapsed time: %.2e\n", (float) ((GetTimeStamp()-dt)) / US_IN_S);
}

// Vector3 type
typedef struct Vector3 {
    double x;
    double y;
    double z;
} Vector3;

double Vector3Norm(Vector3 v) {
    return sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
}

Vector3 Vector3Divide(Vector3 v, double s) {
    return (Vector3) {v.x / s, v.y/s, v.z/s};
}

Vector3 Vector3Hat(Vector3 v) {
    return Vector3Divide(v, Vector3Norm(v));
}

enum BODY {
    EARTH,
    MOON,
    MARS
};

enum MODEL {
    EGM96,
    GRGM360, // https://pds-geosciences.wustl.edu/grail/grail-l-lgrs-5-rdr-v1/grail_1001/shbdr/gggrx_1200a_shb_l180.lbl
    MRO120F // https://pds-geosciences.wustl.edu/mro/mro-m-rss-5-sdp-v1/mrors_1xxx/data/shadr/jgmro_120f_sha.lbl
};

void set_indices(char* model_name, int *model_index, int *body_index) {
    if(strcmp(model_name, "EGM96") == 0) { // if they're the same
        *body_index = EARTH;
        *model_index = EGM96;
    }
    if(strcmp(model_name, "GRGM360") == 0) {
        *body_index = MOON;
        *model_index = GRGM360;
    }
    if(strcmp(model_name, "MRO120F") == 0) {
        *body_index = MARS;
        *model_index = MRO120F;
    }
}


void set_body_params(int body_index, double *mu, double *req) {
    if(body_index == EARTH) {
        *mu = 398600.44;
        *req = 6378.137;
    }
    if(body_index == MOON) {
        *mu = 4902.8001224453001;
        *req = 1738.0;
    }
    if(body_index == MARS) {
        *mu = 42828.3748574;
        *req = 3396.0;
    }
}


void read_cnm_snm(double cnm[EGM96MAXN+2][EGM96MAXN+2], 
                  double snm[EGM96MAXN+2][EGM96MAXN+2],
                  int nmax, int model_index) {
    FILE *f;
    if(model_index == EGM96) {
        f = fopen("./EGM96", "r");
    }
    if(model_index == GRGM360) {
        f = fopen("./GRGM360", "r");
        // Coefficients from: https://pds-geosciences.wustl.edu/grail/grail-l-lgrs-5-rdr-v1/grail_1001/shadr/gggrx_1200a_sha.tab
    }
    if(model_index == MRO120F) {
        f = fopen("./MRO120F", "r");
        // Coefficients from: https://pds-geosciences.wustl.edu/mro/mro-m-rss-5-sdp-v1/mrors_1xxx/data/shadr/jgmro_120f_sha.tab
    }
    int n = -1; 
    int m; 
    double c;
    double s; 
    double temp;
    while(n <= nmax) {
        fscanf(f, "%d ", &n);
        fscanf(f, "%d ", &m);
        fscanf(f, "%lf ", &c);
        fscanf(f, "%lf ", &s);
        fscanf(f, "%lf ", &temp);
        fscanf(f, "%lf ", &temp);
        cnm[n][m] = c;
        snm[n][m] = s;
    }
    cnm[0][0] = 1.0; // Central gravity
    return;
}

Vector3 pinesnorm(Vector3 rf, double cnm[EGM96MAXN+2][EGM96MAXN+2],
               double snm[EGM96MAXN+2][EGM96MAXN+2], int nmax, double mu, double req) {
    // Based on pinesnorm() from: https://core.ac.uk/download/pdf/76424485.pdf
    double rmag = Vector3Norm(rf);
    Vector3 stu = Vector3Hat(rf);
    double anm[nmax+3][nmax+3];
    anm[0][0] = sqrt(2.0);
    for(int m = 0; m <= nmax+2; m++) {
        if(m != 0) { // DIAGONAL RECURSION
            anm[m][m] = sqrt(1.0+1.0/(2.0*m))*anm[m-1][m-1];
        }
        if(m != nmax+2) { // FIRST OFF-DIAGONAL RECURSION 
            anm[m+1][m] = sqrt(2*m+3)*stu.z*anm[m][m];
        }
        if(m < nmax+1) {
            for(int n = m+2; n <= nmax+2; n++) {
                double alpha_num = (2*n+1)*(2*n-1);
                double alpha_den = (n-m)*(n+m);
                double alpha = sqrt(alpha_num/alpha_den);
                double beta_num = (2*n+1)*(n-m-1)*(n+m-1);
                double beta_den = (2*n-3)*(n+m)*(n-m);
                double beta = sqrt(beta_num/beta_den);
                anm[n][m] = alpha*stu.z*anm[n-1][m] - beta*anm[n-2][m];
            }
        }
    }
    for(int n = 0; n <= nmax+2; n++) {
        anm[n][0] *= sqrt(0.50);
    }
    double rm[nmax+2];
    double im[nmax+2];
    rm[0] = 0.00; rm[1] = 1.00; 
    im[0] = 0.00; im[1] = 0.00; 
    for(int m = 2; m < nmax+2; m++) {
        rm[m] = stu.x*rm[m-1] - stu.y*im[m-1]; 
        im[m] = stu.x*im[m-1] + stu.y*rm[m-1];
    }
    double rho  = mu/(req*rmag);
    double rhop = req/rmag;
    double g1 = 0.00; double g2 = 0.00; double g3 = 0.00; double g4 = 0.00;
    for (int n = 0; n <= nmax; n++) {
        double g1t = 0.0; double g2t = 0.0; double g3t = 0.0; double g4t = 0.0;
        double sm = 0.5;
        for(int m = 0; m <= n; m++) {
            if(n == m) anm[n][m+1] = 0.0;
            double dnm = cnm[n][m]*rm[m+1] + snm[n][m]*im[m+1];
            double enm = cnm[n][m]*rm[m] + snm[n][m]*im[m];
            double fnm = snm[n][m]*rm[m] - cnm[n][m]*im[m];
            double alpha  = sqrt(sm*(n-m)*(n+m+1));
            g1t += anm[n][m]*m*enm;
            g2t += anm[n][m]*m*fnm;
            g3t += alpha*anm[n][m+1]*dnm;
            g4t += ((n+m+1)*anm[n][m]+alpha*stu.z*anm[n][m+1])*dnm;
            if(m == 0) sm = 1.0;
        }
        rho *= rhop;
        g1 += rho*g1t; g2 += rho*g2t; g3 += rho*g3t; g4 += rho*g4t;
    }
    return (Vector3) {g1-g4*stu.x, g2-g4*stu.y, g3-g4*stu.z};
}

double* egm96_gravity(double x[], double y[], double z[], int num_pts, int nmax, char* model_name) {
    double cnm[EGM96MAXN+2][EGM96MAXN+2];
    double snm[EGM96MAXN+2][EGM96MAXN+2];
    double req;
    double mu;
    int model_index;
    int body_index;
    set_indices(model_name, &model_index, &body_index);
    set_body_params(body_index, &mu, &req);
    read_cnm_snm(cnm, snm, nmax, model_index);

    double* res = (double*) malloc(3 * num_pts * sizeof(double));
    for(int i = 0; i < num_pts; i++) {
        Vector3 rf = (Vector3){x[i], y[i], z[i]};
        Vector3 gf = pinesnorm(rf, cnm, snm, nmax, mu, req);
        res[3*i + 0] = gf.x;
        res[3*i + 1] = gf.y;
        res[3*i + 2] = gf.z;
    }
    return res;
}