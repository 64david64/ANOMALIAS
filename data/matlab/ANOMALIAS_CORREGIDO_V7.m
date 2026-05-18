%% =========================================================
%  ANÁLISIS SISMOTECTÓNICO — GRAVEDAD + GNSS
%  Colombia: Cordillera Central y Oriental
%  Entrada: resultado_cruzado.csv
%
%  Versión corregida:
%  - Corrige desalineación de estaciones GNSS después del filtrado.
%  - Distingue entre desplazamiento acumulado [m] y velocidad [mm/año].
%  - Usa duración de la serie temporal para estimar tasa media cuando aplica.
%  - Evita colorbars mezcladas en el mapa integrado.
%  - Calcula gradiente horizontal con conversión aproximada grados -> km.
%  - Cambia el lenguaje de "fallas" a "lineamientos potenciales".
%  - Usa umbrales de gradiente por percentiles para evitar umbrales fijos inconsistentes.
%  - Clasifica la relación espacial gravedad-GNSS por distancia.
%  - Evita asociar puntos gravimétricos lejanos a una estación como evidencia local.
%  - Reincorpora vectores GNSS en los mapas de Bouguer, gradiente e integrado.
%  - Excluye estaciones GNSS con baja solidez temporal/anomalías cinemáticas
%    para el análisis vectorial, sin eliminar sus puntos gravimétricos de la grilla regional.
%  - V5: conserva el tratamiento gravimétrico base de la primera versión:
%    gravity_anomaly se usa como insumo y se calculan anomalía de aire libre
%    y anomalía de Bouguer simple.
%  - V5: mantiene vectores GNSS residuales respecto a la media de la red retenida
%    para una interpretación práctica en marco IGS20/ITRF2020.
%  - V6: prepara salidas oficiales para visor web.
%  - V6: las tablas de análisis solo incluyen estaciones GNSS retenidas; las estaciones
%    excluidas no se mencionan en los archivos oficiales de análisis contextual.
%  - V6: explicita que la relación gravedad-GNSS es contextual por proximidad,
%    no una asociación directa entre puntos gravimétricos y estaciones GNSS.
%  - V6: exporta metadata_variables.json y figuras oficiales para el visor.
%  - V7: deja únicamente las salidas oficiales necesarias para el visor web.
%% =========================================================
clc; clear; close all;

%% ── CONFIGURACIÓN ─────────────────────────────────────────
[nombre_archivo, ruta] = uigetfile('*.csv', 'Selecciona resultado_cruzado.csv');
if isequal(nombre_archivo,0)
    error('No se seleccionó ningún archivo CSV.');
end
ARCHIVO = fullfile(ruta, nombre_archivo);

% Carpeta oficial de salidas para alimentar el visor web.
out_dir = fullfile(fileparts(ARCHIVO), 'salidas_sismotectonicas');
fig_dir = fullfile(out_dir, 'figuras');
if ~exist(out_dir, 'dir'), mkdir(out_dir); end
if ~exist(fig_dir, 'dir'), mkdir(fig_dir); end

% Regenerar salidas limpias en cada ejecución.
old_csv = dir(fullfile(out_dir, '*.csv'));
for ii_obs = 1:numel(old_csv)
    delete(fullfile(out_dir, old_csv(ii_obs).name));
end
old_png = dir(fullfile(fig_dir, '*.png'));
for ii_obs = 1:numel(old_png)
    delete(fullfile(fig_dir, old_png(ii_obs).name));
end
old_json = fullfile(out_dir, 'metadata_variables.json');
if exist(old_json, 'file')
    delete(old_json);
end

DENSIDAD_BOUGUER = 2670;        % kg/m³, densidad cortical estándar usada para placa simple
G_CONST          = 6.674e-11;   % constante gravitacional [m³ kg⁻¹ s⁻²]
GAMMA_FA         = 0.3086;      % gradiente de aire libre [mGal/m]
GAMMA_BOUGUER    = 2*pi*G_CONST*DENSIDAD_BOUGUER*1e5; % corrección Bouguer simple [mGal/m]

% IMPORTANTE SOBRE GRAVEDAD:
% Para mantener consistencia con la primera versión del procesamiento,
% gravity_anomaly se conserva como insumo base y se aplican las correcciones
% simples de aire libre y Bouguer. No se modifica la columna original;
% se crean variables derivadas: anom_FA y anom_Bouguer.
GRAVITY_INPUT_TIPO = 'requiere_correcciones_simples';  % opciones: 'requiere_correcciones_simples' | 'bouguer_corregida'

% Marco de referencia de los datos GNSS.
% IGS20 está alineado con ITRF2020 para efectos prácticos de este proyecto.
MARCO_REFERENCIA_GNSS = 'IGS20 / ITRF2020';

% En un marco global, las velocidades absolutas pueden incluir el movimiento común
% de la red. Para los mapas integrados se recomienda mostrar vectores residuales,
% removiendo la media de las estaciones retenidas. Esto NO reemplaza una solución
% placa-fija rigurosa; es una normalización práctica y pedagógica.
GNSS_VECTOR_MODE = 'residual_media_red';  % opciones: 'residual_media_red' | 'absoluto'

% IMPORTANTE SOBRE GNSS:
% Si gnss_east_m, gnss_north_m y gnss_up_m son desplazamientos acumulados
% de la serie temporal en metros, use 'desplazamiento_acumulado'.
% Si vienen directamente de un archivo MIDAS velocity de NGL, use 'velocidad_midas'.
% En el CSV actual los nombres terminan en _m y existe gnss_n_dias, por eso se
% recomienda trabajar como desplazamiento acumulado y derivar una tasa media.
GNSS_MODO = 'desplazamiento_acumulado';  % opciones: 'desplazamiento_acumulado' | 'velocidad_midas'

% Estaciones excluidas del análisis GNSS vectorial por control de calidad.
% Motivo: series temporales cortas y/o componentes de velocidad/desplazamiento
% poco coherentes para sostener una interpretación sismotectónica robusta.
% IMPORTANTE: sus puntos gravimétricos NO se eliminan de la grilla regional;
% solo se excluyen de mapas/vectorización/resumen GNSS y de asociaciones locales.
EXCLUIR_ESTACIONES_GNSS = ["IGAC", "SGCC", "SOCB"];
MIN_DURACION_GNSS_YR = 2;

% Resolución de la grilla. 0.05° equivale aproximadamente a 5.5 km en latitud.
res = 0.05;

% Umbrales para interpretar la cercanía entre puntos gravimétricos y estaciones GNSS.
% Los puntos NO se eliminan de la grilla regional; estos umbrales solo controlan
% el peso interpretativo cuando se resume gravedad alrededor de una estación.
DIST_LOCAL_KM      = 50;
DIST_CONTEXTUAL_KM = 100;
DIST_REGIONAL_KM   = 150;

% Escala visual de las flechas GNSS en grados. Las flechas quedan normalizadas
% respecto a la mayor velocidad horizontal para que sean legibles en el mapa.
ESCALA_VECTOR_GNSS_DEG = 0.45;

%% ── LEER DATOS ────────────────────────────────────────────
fprintf('Leyendo %s...\n', ARCHIVO);
opts = detectImportOptions(ARCHIVO);
opts.VariableNamesLine = 1;
T = readtable(ARCHIVO, opts);

% Validar columnas obligatorias
required = {'latitude','longitude','h_over_geoid','gravity_anomaly', ...
            'gnss_site','gnss_latitude_deg','gnss_longitude_deg','gnss_height_m', ...
            'gnss_east_m','gnss_north_m','gnss_up_m', ...
            'gnss_sig_e_m','gnss_sig_n_m','gnss_sig_u_m', ...
            'gnss_n_dias','dist_gnss_km'};
for k = 1:numel(required)
    if ~ismember(required{k}, T.Properties.VariableNames)
        error('Falta la columna obligatoria: %s', required{k});
    end
end

% Extraer columnas principales
lat  = T.latitude;
lon  = T.longitude;
h    = T.h_over_geoid;
ag   = T.gravity_anomaly;   % anomalía/base gravimétrica original del insumo [mGal]

% Estaciones GNSS
est_nombres = string(T.gnss_site);
est_lat     = T.gnss_latitude_deg;
est_lon     = T.gnss_longitude_deg;
est_h       = T.gnss_height_m;
est_e_raw   = T.gnss_east_m;
est_n_raw   = T.gnss_north_m;
est_u_raw   = T.gnss_up_m;
est_sige    = T.gnss_sig_e_m;
est_sign    = T.gnss_sig_n_m;
est_sigu    = T.gnss_sig_u_m;
est_ndias   = T.gnss_n_dias;
dist_km     = T.dist_gnss_km;

%% ── FILTRAR DATOS VÁLIDOS ─────────────────────────────────
% Se filtran todas las variables en conjunto para evitar desalineaciones entre
% nombre de estación, coordenadas, desplazamientos/velocidades y distancias.
mask = isfinite(lat) & isfinite(lon) & isfinite(h) & isfinite(ag) & ...
       isfinite(dist_km) & est_nombres ~= "" & ~ismissing(est_nombres) & ...
       isfinite(est_lat) & isfinite(est_lon) & isfinite(est_h) & ...
       isfinite(est_e_raw) & isfinite(est_n_raw) & isfinite(est_u_raw) & ...
       isfinite(est_sige) & isfinite(est_sign) & isfinite(est_sigu) & ...
       isfinite(est_ndias) & est_ndias > 0;

lat  = lat(mask);
lon  = lon(mask);
h    = h(mask);
ag   = ag(mask);

est_nombres = est_nombres(mask);
est_lat     = est_lat(mask);
est_lon     = est_lon(mask);
est_h       = est_h(mask);
est_e_raw   = est_e_raw(mask);
est_n_raw   = est_n_raw(mask);
est_u_raw   = est_u_raw(mask);
est_sige    = est_sige(mask);
est_sign    = est_sign(mask);
est_sigu    = est_sigu(mask);
est_ndias   = est_ndias(mask);
dist_km     = dist_km(mask);

fprintf('  → %d puntos gravimétricos válidos cargados para grilla regional.\n', numel(lat));
fprintf('  → %d estaciones GNSS únicas en el archivo original.\n', numel(unique(est_nombres)));

% Marcador de estaciones excluidas. Se conserva para exportar el estado de cada
% punto, pero estas estaciones no entran al análisis GNSS vectorial.
estacion_excluida_qc = ismember(est_nombres, EXCLUIR_ESTACIONES_GNSS);
if any(estacion_excluida_qc)
    fprintf('  → %d estaciones GNSS fueron excluidas por control de calidad temporal/cinemático.\n', numel(EXCLUIR_ESTACIONES_GNSS));
    fprintf('  → Sus puntos gravimétricos se conservan para interpolación regional, no para asociación local GNSS.\n');
end

%% ── TRATAMIENTO DE LA ANOMALÍA GRAVIMÉTRICA ──────────────
% La columna gravity_anomaly se conserva como dato base.
% Por defecto se aplican las correcciones simples de aire libre y Bouguer
% para reproducir el tratamiento de la primera versión del código.
if strcmpi(GRAVITY_INPUT_TIPO, 'bouguer_corregida')
    anom_Bouguer = ag;
    anom_FA = NaN(size(ag));
    anom_FA_disponible = false;
    etiqueta_bouguer = 'Anomalía de Bouguer corregida del insumo [mGal]';
    etiqueta_bouguer_corta = 'Anomalía de Bouguer corregida';

    fprintf('  Modo alternativo: gravity_anomaly se interpreta como anomalía ya corregida. No se recalculan correcciones gravimétricas.\n');
    fprintf('  Anomalía corregida: min=%.2f  max=%.2f  media=%.2f mGal\n', ...
        min(anom_Bouguer), max(anom_Bouguer), mean(anom_Bouguer));

elseif strcmpi(GRAVITY_INPUT_TIPO, 'requiere_correcciones_simples')
    % 1. Corrección de aire libre
    corr_FA = GAMMA_FA * h;
    anom_FA = ag + corr_FA;   % anomalía de aire libre simple [mGal]

    % 2. Corrección de placa de Bouguer simple
    corr_BP = GAMMA_BOUGUER * h;  % [mGal]
    anom_Bouguer = anom_FA - corr_BP;
    anom_FA_disponible = true;
    etiqueta_bouguer = 'Anomalía de Bouguer simple [mGal]';
    etiqueta_bouguer_corta = 'Anomalía de Bouguer simple';

    fprintf('  Correcciones simples aplicadas desde gravity_anomaly.\n');
    fprintf('  Anomalía aire libre:       min=%.2f  max=%.2f  media=%.2f mGal\n', ...
        min(anom_FA), max(anom_FA), mean(anom_FA));
    fprintf('  Anomalía Bouguer simple:   min=%.2f  max=%.2f  media=%.2f mGal\n', ...
        min(anom_Bouguer), max(anom_Bouguer), mean(anom_Bouguer));
else
    error('GRAVITY_INPUT_TIPO no válido. Use bouguer_corregida o requiere_correcciones_simples.');
end

%% ── GRILLA INTERPOLADA ────────────────────────────────────
lon_vec = min(lon):res:max(lon);
lat_vec = min(lat):res:max(lat);
[LON_G, LAT_G] = meshgrid(lon_vec, lat_vec);

AG_G  = griddata(lon, lat, ag,           LON_G, LAT_G, 'natural');
if anom_FA_disponible
    FA_G = griddata(lon, lat, anom_FA,   LON_G, LAT_G, 'natural');
else
    FA_G = NaN(size(LON_G));
end
BG_G  = griddata(lon, lat, anom_Bouguer, LON_G, LAT_G, 'natural');
H_G   = griddata(lon, lat, h,            LON_G, LAT_G, 'natural');

%% ── GRADIENTE HORIZONTAL ──────────────────────────────────
% Conversión aproximada de grados a km para Colombia.
% Para una versión más rigurosa, proyectar previamente la grilla a coordenadas métricas.
dy_km = res * 110.57;
dx_km = res * 111.32 * cosd(mean(lat));

[dBdy, dBdx] = gradient(BG_G, dy_km, dx_km); % MATLAB entrega derivada por filas y columnas
GradH = sqrt(dBdx.^2 + dBdy.^2);             % [mGal/km]

GradH_valid = GradH(isfinite(GradH));
if isempty(GradH_valid)
    error('No se pudo calcular el gradiente horizontal: la grilla contiene solo NaN.');
end

% Umbrales relativos. Evitan clasificar con límites fijos que pueden no existir en el rango real.
thr_grad_probable = prctile(GradH_valid, 75);
thr_grad_definido = prctile(GradH_valid, 90);
thr_grad_alto     = prctile(GradH_valid, 95);

% Gradiente interpolado sobre cada punto gravimétrico. Se usa solo para
% resúmenes por estación dentro de radios controlados de distancia.
GradH_puntos = interp2(lon_vec, lat_vec, GradH, lon, lat, 'linear', NaN);

%% ── ESTACIONES GNSS ÚNICAS Y TASAS ────────────────────────
% Se separa el universo gravimétrico del universo GNSS.
% - lat/lon/h/ag/anom_Bouguer alimentan la grilla regional completa.
% - las estaciones excluidas NO se dibujan como vectores ni entran en resúmenes GNSS.
mask_gnss_usada = ~ismember(est_nombres, EXCLUIR_ESTACIONES_GNSS);

if ~any(mask_gnss_usada)
    error('Todas las estaciones GNSS quedaron excluidas. Revise EXCLUIR_ESTACIONES_GNSS.');
end

est_nombres_gnss = est_nombres(mask_gnss_usada);
est_lat_gnss     = est_lat(mask_gnss_usada);
est_lon_gnss     = est_lon(mask_gnss_usada);
est_h_gnss       = est_h(mask_gnss_usada);
est_e_raw_gnss   = est_e_raw(mask_gnss_usada);
est_n_raw_gnss   = est_n_raw(mask_gnss_usada);
est_u_raw_gnss   = est_u_raw(mask_gnss_usada);
est_sige_gnss    = est_sige(mask_gnss_usada);
est_sign_gnss    = est_sign(mask_gnss_usada);
est_sigu_gnss    = est_sigu(mask_gnss_usada);
est_ndias_gnss   = est_ndias(mask_gnss_usada);
dist_km_gnss     = dist_km(mask_gnss_usada);
anom_Bouguer_gnss = anom_Bouguer(mask_gnss_usada);
GradH_puntos_gnss = GradH_puntos(mask_gnss_usada);

fprintf('  → %d estaciones GNSS usadas después del control de calidad: %d excluidas, %d retenidas.\n', ...
    numel(unique(est_nombres)), numel(unique(est_nombres)) - numel(unique(est_nombres_gnss)), numel(unique(est_nombres_gnss)));

% Se agrupa por estación para no depender del primer registro de la tabla.
[G, est_cat] = findgroups(categorical(est_nombres_gnss));
GNSS.nombre = cellstr(est_cat);
n_est = numel(GNSS.nombre);

GNSS.lat      = splitapply(@mean, est_lat_gnss, G);
GNSS.lon      = splitapply(@mean, est_lon_gnss, G);
GNSS.h        = splitapply(@mean, est_h_gnss, G);
GNSS.e_raw    = splitapply(@mean, est_e_raw_gnss, G);
GNSS.n_raw    = splitapply(@mean, est_n_raw_gnss, G);
GNSS.u_raw    = splitapply(@mean, est_u_raw_gnss, G);
GNSS.sige_raw = splitapply(@mean, est_sige_gnss, G);
GNSS.sign_raw = splitapply(@mean, est_sign_gnss, G);
GNSS.sigu_raw = splitapply(@mean, est_sigu_gnss, G);
GNSS.n_dias   = splitapply(@mean, est_ndias_gnss, G);
GNSS.duracion_yr = GNSS.n_dias / 365.25;

% Estadísticos de distancia entre puntos gravimétricos y estación asociada,
% calculados solo para estaciones GNSS retenidas.
GNSS.dist_min_km = splitapply(@min, dist_km_gnss, G);
GNSS.dist_med_km = splitapply(@median, dist_km_gnss, G);
GNSS.dist_max_km = splitapply(@max, dist_km_gnss, G);
GNSS.n_puntos    = splitapply(@numel, dist_km_gnss, G);

GNSS.n_local       = splitapply(@(d) sum(d <= DIST_LOCAL_KM), dist_km_gnss, G);
GNSS.n_contextual  = splitapply(@(d) sum(d > DIST_LOCAL_KM & d <= DIST_CONTEXTUAL_KM), dist_km_gnss, G);
GNSS.n_regional    = splitapply(@(d) sum(d > DIST_CONTEXTUAL_KM & d <= DIST_REGIONAL_KM), dist_km_gnss, G);
GNSS.n_no_local    = splitapply(@(d) sum(d > DIST_REGIONAL_KM), dist_km_gnss, G);
GNSS.n_hasta_100km = splitapply(@(d) sum(d <= DIST_CONTEXTUAL_KM), dist_km_gnss, G);
GNSS.n_hasta_150km = splitapply(@(d) sum(d <= DIST_REGIONAL_KM), dist_km_gnss, G);
GNSS.pct_100km     = 100 * GNSS.n_hasta_100km ./ GNSS.n_puntos;
GNSS.pct_150km     = 100 * GNSS.n_hasta_150km ./ GNSS.n_puntos;

% Resumen gravimétrico alrededor de cada estación usando SOLO puntos <=100 km.
% Las estaciones excluidas no entran a este resumen.
GNSS.bouguer_med_100km = splitapply(@(b,d) median_radius(b,d,DIST_CONTEXTUAL_KM), anom_Bouguer_gnss, dist_km_gnss, G);
GNSS.bouguer_mean_100km = splitapply(@(b,d) mean_radius(b,d,DIST_CONTEXTUAL_KM), anom_Bouguer_gnss, dist_km_gnss, G);
GNSS.grad_med_100km = splitapply(@(g,d) median_radius(g,d,DIST_CONTEXTUAL_KM), GradH_puntos_gnss, dist_km_gnss, G);
GNSS.grad_max_100km = splitapply(@(g,d) max_radius(g,d,DIST_CONTEXTUAL_KM), GradH_puntos_gnss, dist_km_gnss, G);

GNSS.clase_espacial = strings(n_est,1);
for i = 1:n_est
    if GNSS.pct_100km(i) >= 70 && GNSS.dist_med_km(i) <= DIST_CONTEXTUAL_KM && GNSS.n_no_local(i) == 0
        GNSS.clase_espacial(i) = "contexto_local_robusto";
    elseif GNSS.pct_100km(i) >= 50 && GNSS.pct_150km(i) >= 85
        GNSS.clase_espacial(i) = "contexto_regional_aceptable";
    elseif GNSS.pct_150km(i) >= 70
        GNSS.clase_espacial(i) = "contexto_regional_con_cautela";
    else
        GNSS.clase_espacial(i) = "no_recomendado_para_asociacion_local";
    end
end

if strcmpi(GNSS_MODO, 'desplazamiento_acumulado')
    % Interpreta gnss_*_m como desplazamiento acumulado en metros durante la serie.
    GNSS.dispE_mm = GNSS.e_raw * 1000;
    GNSS.dispN_mm = GNSS.n_raw * 1000;
    GNSS.dispU_mm = GNSS.u_raw * 1000;

    GNSS.vE_mmyr = GNSS.dispE_mm ./ GNSS.duracion_yr;
    GNSS.vN_mmyr = GNSS.dispN_mm ./ GNSS.duracion_yr;
    GNSS.vU_mmyr = GNSS.dispU_mm ./ GNSS.duracion_yr;

    GNSS.sigE_mmyr = (GNSS.sige_raw * 1000) ./ GNSS.duracion_yr;
    GNSS.sigN_mmyr = (GNSS.sign_raw * 1000) ./ GNSS.duracion_yr;
    GNSS.sigU_mmyr = (GNSS.sigu_raw * 1000) ./ GNSS.duracion_yr;

    etiqueta_gnss = 'Velocidad media estimada desde desplazamiento acumulado [mm/año]';
elseif strcmpi(GNSS_MODO, 'velocidad_midas')
    % Interpreta gnss_*_m como velocidad MIDAS en m/año.
    GNSS.vE_mmyr = GNSS.e_raw * 1000;
    GNSS.vN_mmyr = GNSS.n_raw * 1000;
    GNSS.vU_mmyr = GNSS.u_raw * 1000;

    GNSS.sigE_mmyr = GNSS.sige_raw * 1000;
    GNSS.sigN_mmyr = GNSS.sign_raw * 1000;
    GNSS.sigU_mmyr = GNSS.sigu_raw * 1000;

    GNSS.dispE_mm = NaN(size(GNSS.vE_mmyr));
    GNSS.dispN_mm = NaN(size(GNSS.vN_mmyr));
    GNSS.dispU_mm = NaN(size(GNSS.vU_mmyr));

    etiqueta_gnss = 'Velocidad GNSS tipo MIDAS [mm/año]';
else
    error('GNSS_MODO no válido. Use desplazamiento_acumulado o velocidad_midas.');
end

GNSS.vH_mmyr = sqrt(GNSS.vE_mmyr.^2 + GNSS.vN_mmyr.^2);
GNSS.azimuth_deg = mod(atan2d(GNSS.vE_mmyr, GNSS.vN_mmyr), 360); % 0=N, 90=E
GNSS.sigH_mmyr = sqrt(GNSS.sigE_mmyr.^2 + GNSS.sigN_mmyr.^2);
GNSS.snrH = GNSS.vH_mmyr ./ GNSS.sigH_mmyr;
GNSS.snrH(~isfinite(GNSS.snrH)) = NaN;

% Residuales simples respecto a la media de la red retenida.
% Útiles para visualizar deformación diferencial sin que domine el movimiento común
% del marco global IGS20/ITRF2020.
media_vE = mean(GNSS.vE_mmyr(isfinite(GNSS.vE_mmyr)));
media_vN = mean(GNSS.vN_mmyr(isfinite(GNSS.vN_mmyr)));
media_vU = mean(GNSS.vU_mmyr(isfinite(GNSS.vU_mmyr)));
GNSS.vE_res_mmyr = GNSS.vE_mmyr - media_vE;
GNSS.vN_res_mmyr = GNSS.vN_mmyr - media_vN;
GNSS.vU_res_mmyr = GNSS.vU_mmyr - media_vU;
GNSS.vH_res_mmyr = sqrt(GNSS.vE_res_mmyr.^2 + GNSS.vN_res_mmyr.^2);
GNSS.azimuth_res_deg = mod(atan2d(GNSS.vE_res_mmyr, GNSS.vN_res_mmyr), 360);

if strcmpi(GNSS_VECTOR_MODE, 'residual_media_red')
    GNSS.vE_plot_mmyr = GNSS.vE_res_mmyr;
    GNSS.vN_plot_mmyr = GNSS.vN_res_mmyr;
    GNSS.vU_plot_mmyr = GNSS.vU_res_mmyr;
    GNSS.vH_plot_mmyr = GNSS.vH_res_mmyr;
    etiqueta_vector_gnss = 'Vectores GNSS residuales: media de la red retenida removida';
elseif strcmpi(GNSS_VECTOR_MODE, 'absoluto')
    GNSS.vE_plot_mmyr = GNSS.vE_mmyr;
    GNSS.vN_plot_mmyr = GNSS.vN_mmyr;
    GNSS.vU_plot_mmyr = GNSS.vU_mmyr;
    GNSS.vH_plot_mmyr = GNSS.vH_mmyr;
    etiqueta_vector_gnss = 'Vectores GNSS absolutos en marco de referencia de origen';
else
    error('GNSS_VECTOR_MODE no válido. Use residual_media_red o absoluto.');
end

% Componentes normalizadas para dibujar flechas GNSS visibles en mapas 2D.
mag_max = max(GNSS.vH_plot_mmyr(isfinite(GNSS.vH_plot_mmyr)));
if isempty(mag_max) || mag_max <= 0 || ~isfinite(mag_max)
    mag_max = 1;
end
GNSS.vecE_plot = (GNSS.vE_plot_mmyr ./ mag_max) * ESCALA_VECTOR_GNSS_DEG;
GNSS.vecN_plot = (GNSS.vN_plot_mmyr ./ mag_max) * ESCALA_VECTOR_GNSS_DEG;

% Control de calidad básico
idx_corta = GNSS.duracion_yr < MIN_DURACION_GNSS_YR;
idx_alta  = GNSS.vH_mmyr > 150 | abs(GNSS.vU_mmyr) > 150;
if any(idx_corta)
    fprintf('\nADVERTENCIA GNSS: estaciones retenidas con duración menor al mínimo definido: %s\n', ...
        strjoin(GNSS.nombre(idx_corta), ', '));
end
if any(idx_alta)
    fprintf('ADVERTENCIA GNSS: velocidades altas detectadas. Revisar unidades o duración en: %s\n', ...
        strjoin(GNSS.nombre(idx_alta), ', '));
end
if max(GNSS.dist_max_km) > DIST_REGIONAL_KM
    idx_espacial = GNSS.n_no_local > 0;
    fprintf('ADVERTENCIA ESPACIAL: hay puntos gravimétricos a más de %.0f km de su estación GNSS asociada.\n', DIST_REGIONAL_KM);
    fprintf('  → No se eliminan de la grilla regional, pero NO deben usarse como evidencia local por estación.\n');
    fprintf('  → Estaciones con puntos >%.0f km: %s\n', DIST_REGIONAL_KM, strjoin(GNSS.nombre(idx_espacial), ', '));
end

%% =========================================================
%  FIGURA 1 — ANOMALÍA DE AIRE LIBRE + VECTORES GNSS
%% =========================================================
figure('Name','Anomalía Aire Libre','Position',[50 50 900 700]);
if anom_FA_disponible
    data_fig1 = anom_FA;
    etiqueta_fig1 = 'Anomalía aire libre [mGal]';
    titulo_fig1 = 'Anomalía de Aire Libre + Vectores GNSS horizontales';
else
    data_fig1 = anom_Bouguer;
    etiqueta_fig1 = etiqueta_bouguer;
    titulo_fig1 = 'Anomalía gravimétrica corregida del insumo + Vectores GNSS horizontales';
end
scatter(lon, lat, 8, data_fig1, 'filled');
colormap(gca, redblue(256));
cb = colorbar; cb.Label.String = etiqueta_fig1;
cb.Label.FontSize = 11;
caxis([pct(data_fig1,2) pct(data_fig1,98)]);
hold on;

% Vectores GNSS normalizados solo para visualización cartográfica
plot_gnss_vectors(GNSS, 'k', 2.0, 0.6);
for i = 1:n_est
    text(GNSS.lon(i)+0.03, GNSS.lat(i)+0.03, GNSS.nombre{i}, ...
         'FontSize', 8, 'FontWeight','bold', 'Color','k');
end

xlabel('Longitud [°]', 'FontSize', 12);
ylabel('Latitud [°]', 'FontSize', 12);
title({titulo_fig1, ...
       etiqueta_vector_gnss}, ...
       'FontSize',13,'FontWeight','bold');
axis tight; grid on; box on;
safe_export_fig(gcf, fig_dir, '01_anomalia_aire_libre_vectores_gnss.png');

%% =========================================================
%  FIGURA 2 — ANOMALÍA DE BOUGUER
%% =========================================================
figure('Name','Anomalía de Bouguer','Position',[100 50 900 700]);
contourf(LON_G, LAT_G, BG_G, 30, 'LineColor','none');
colormap(gca, redblue(256));
cb = colorbar; cb.Label.String = etiqueta_bouguer;
cb.Label.FontSize = 11;
caxis([pct(BG_G,2) pct(BG_G,98)]);
hold on;

% Contornos de alto gradiente como lineamientos potenciales
contour(LON_G, LAT_G, GradH, [thr_grad_definido thr_grad_alto], ...
        'k--', 'LineWidth', 1.1);

scatter(GNSS.lon, GNSS.lat, 80, 'w', 'filled', ...
        'MarkerEdgeColor','k', 'LineWidth',1.5);
plot_gnss_vectors(GNSS, 'k', 2.0, 0.6);
for i = 1:n_est
    text(GNSS.lon(i)+0.05, GNSS.lat(i)+0.05, GNSS.nombre{i}, ...
         'FontSize', 8, 'FontWeight','bold', 'Color','w', ...
         'BackgroundColor',[0 0 0]);
end

xlabel('Longitud [°]', 'FontSize', 12);
ylabel('Latitud [°]', 'FontSize', 12);
title({[etiqueta_bouguer_corta ' — contraste gravimétrico regional'], ...
       'Líneas punteadas = zonas de alto gradiente; interpretación como lineamientos potenciales'}, ...
      'FontSize', 13, 'FontWeight', 'bold');
grid on; box on;
set(gca, 'FontSize', 10);
safe_export_fig(gcf, fig_dir, '02_anomalia_bouguer_lineamientos_gnss.png');

%% =========================================================
%  FIGURA 3 — GRADIENTE HORIZONTAL
%% =========================================================
figure('Name','Gradiente Horizontal','Position',[150 50 900 700]);
imagesc(lon_vec, lat_vec, GradH);
set(gca, 'YDir', 'normal');
colormap(gca, hot(256));
cb = colorbar; cb.Label.String = 'Gradiente horizontal de Bouguer [mGal/km]';
cb.Label.FontSize = 11;
caxis([0 pct(GradH,95)]);
hold on;

contour(LON_G, LAT_G, GradH, [thr_grad_probable thr_grad_definido thr_grad_alto], ...
        'c-', 'LineWidth', 1.2);

scatter(GNSS.lon, GNSS.lat, 80, 'w', 'filled', ...
        'MarkerEdgeColor','k', 'LineWidth', 1.5);
plot_gnss_vectors(GNSS, [1 0.9 0], 2.1, 0.7);
for i = 1:n_est
    text(GNSS.lon(i)+0.05, GNSS.lat(i)+0.05, GNSS.nombre{i}, ...
         'FontSize', 8, 'FontWeight','bold', 'Color','w', ...
         'BackgroundColor',[0 0 0]);
end

xlabel('Longitud [°]', 'FontSize', 12);
ylabel('Latitud [°]', 'FontSize', 12);
title({'Gradiente horizontal de anomalía de Bouguer', ...
       'Máximos relativos = posibles bordes de bloques corticales / lineamientos gravimétricos'}, ...
      'FontSize', 13, 'FontWeight', 'bold');
grid on; box on;
set(gca, 'FontSize', 10);
safe_export_fig(gcf, fig_dir, '03_gradiente_horizontal_bouguer_gnss.png');

%% =========================================================
%  FIGURA 4 — PERFILES W-E
%% =========================================================
lat_perfiles = [6.2, 5.0, 4.6, 3.5];  % Medellín, Manizales, Bogotá, Neiva
colores_p = {'b','r','g','m'};
nombres_p = {'~6.2° (Medellín)', '~5.0° (Manizales)', ...
             '~4.6° (Bogotá)',    '~3.5° (Neiva)'};

figure('Name','Perfiles W-E','Position',[200 50 1100 800]);

subplot(2,1,1); hold on;
title(['Perfiles W-E — ' etiqueta_bouguer_corta], 'FontSize', 12, 'FontWeight','bold');
for k = 1:length(lat_perfiles)
    [~, iy] = min(abs(lat_vec - lat_perfiles(k)));
    plot(lon_vec, BG_G(iy, :), colores_p{k}, 'LineWidth', 2);
end
legend(nombres_p, 'Location','best', 'FontSize', 9);
xlabel('Longitud [°]', 'FontSize', 11);
ylabel(etiqueta_bouguer, 'FontSize', 11);
grid on; box on;

subplot(2,1,2); hold on;
title('Perfiles W-E — Topografía', 'FontSize', 12, 'FontWeight','bold');
for k = 1:length(lat_perfiles)
    [~, iy] = min(abs(lat_vec - lat_perfiles(k)));
    plot(lon_vec, H_G(iy, :), colores_p{k}, 'LineWidth', 2);
end
legend(nombres_p, 'Location','best', 'FontSize', 9);
xlabel('Longitud [°]', 'FontSize', 11);
ylabel('Altura sobre geoide [m]', 'FontSize', 11);
grid on; box on;
safe_export_fig(gcf, fig_dir, '04_perfiles_we_bouguer_topografia.png');

%% =========================================================
%  FIGURA 5 — GNSS: VELOCIDADES POR ESTACIÓN
%% =========================================================
figure('Name','GNSS por Estación','Position',[250 50 1200 760]);

subplot(2,3,1);
bar(categorical(GNSS.nombre), GNSS.vE_mmyr, 'FaceColor', [0.2 0.5 0.8]);
title('Este absoluto [mm/año]', 'FontSize', 11, 'FontWeight','bold');
ylabel('[mm/año]'); grid on; box on; yline(0,'k-'); xtickangle(45);

subplot(2,3,2);
bar(categorical(GNSS.nombre), GNSS.vN_mmyr, 'FaceColor', [0.2 0.7 0.4]);
title('Norte absoluto [mm/año]', 'FontSize', 11, 'FontWeight','bold');
ylabel('[mm/año]'); grid on; box on; yline(0,'k-'); xtickangle(45);

subplot(2,3,3);
bar(categorical(GNSS.nombre), GNSS.vU_mmyr, 'FaceColor', [0.8 0.4 0.2]);
title('Up absoluto [mm/año]', 'FontSize', 11, 'FontWeight','bold');
ylabel('[mm/año]'); grid on; box on; yline(0,'k-'); xtickangle(45);

subplot(2,3,4);
bar(categorical(GNSS.nombre), GNSS.vE_res_mmyr, 'FaceColor', [0.2 0.5 0.8]);
title('Este residual [mm/año]', 'FontSize', 11, 'FontWeight','bold');
ylabel('[mm/año]'); grid on; box on; yline(0,'k-'); xtickangle(45);

subplot(2,3,5);
bar(categorical(GNSS.nombre), GNSS.vN_res_mmyr, 'FaceColor', [0.2 0.7 0.4]);
title('Norte residual [mm/año]', 'FontSize', 11, 'FontWeight','bold');
ylabel('[mm/año]'); grid on; box on; yline(0,'k-'); xtickangle(45);

subplot(2,3,6);
bar(categorical(GNSS.nombre), GNSS.vU_res_mmyr, 'FaceColor', [0.8 0.4 0.2]);
title('Up residual [mm/año]', 'FontSize', 11, 'FontWeight','bold');
ylabel('[mm/año]'); grid on; box on; yline(0,'k-'); xtickangle(45);

sgtitle({sprintf('Velocidades GNSS por estación retenida QC — n=%d | Marco: %s', n_est, MARCO_REFERENCIA_GNSS), ...
         etiqueta_gnss, ...
         'Fila superior: tasa absoluta | Fila inferior: residual respecto a la media de la red retenida'}, ...
        'FontSize', 13, 'FontWeight','bold');
safe_export_fig(gcf, fig_dir, '05_velocidades_gnss_estaciones_retenidas.png');

%% =========================================================
%  FIGURA 6 — MAPA INTEGRADO SISMOTECTÓNICO
%% =========================================================
figure('Name','Mapa Sismotectónico','Position',[50 50 1050 800]);

% Fondo: gradiente horizontal. La barra de color corresponde SOLO al gradiente.
imagesc(lon_vec, lat_vec, GradH);
set(gca, 'YDir','normal');
colormap(gca, gray(256));
caxis([0 pct(GradH,90)]);
cb = colorbar('eastoutside');
cb.Label.String = 'Gradiente horizontal de Bouguer [mGal/km]';
cb.Label.FontSize = 11;
hold on;

% Contornos de Bouguer
contour(LON_G, LAT_G, BG_G, 15, 'LineWidth', 0.8, 'LineColor',[0.2 0.4 0.8]);

% Lineamientos potenciales por alto gradiente relativo
contour(LON_G, LAT_G, GradH, [thr_grad_definido thr_grad_alto], ...
        'r-', 'LineWidth', 1.6);

% Vectores GNSS horizontales normalizados
plot_gnss_vectors(GNSS, [1 0.9 0], 2.6, 0.8);

% Marcadores de estaciones con color fijo para no mezclar colorbar de GNSS y gradiente
scatter(GNSS.lon, GNSS.lat, 120, 'w', 'filled', ...
        'MarkerEdgeColor','k', 'LineWidth',2);

for i = 1:n_est
    etiqueta = sprintf('%s\nHres=%.1f | Ures=%.1f', GNSS.nombre{i}, GNSS.vH_plot_mmyr(i), GNSS.vU_plot_mmyr(i));
    text(GNSS.lon(i)+0.06, GNSS.lat(i)+0.06, etiqueta, ...
         'FontSize', 8, 'FontWeight','bold', 'Color','w', ...
         'BackgroundColor',[0 0 0]);
end

xlabel('Longitud [°]', 'FontSize', 12);
ylabel('Latitud [°]', 'FontSize', 12);
title({'MAPA INTEGRADO SISMOTECTÓNICO', ...
       ['Fondo: gradiente gravimétrico | Azul: Bouguer | Rojo: lineamientos potenciales | ' etiqueta_vector_gnss]}, ...
      'FontSize', 12, 'FontWeight','bold');
grid on; box on;
set(gca,'FontSize',10, 'Layer','top');
safe_export_fig(gcf, fig_dir, '06_mapa_integrado_sismotectonico.png');

%% =========================================================
%  FIGURA 7 — CORRELACIÓN BOUGUER vs ALTURA
%% =========================================================
figure('Name','Relación Bouguer-Topografía','Position',[300 100 750 520]);
scatter(h, anom_Bouguer, 8, lon, 'filled', 'MarkerFaceAlpha', 0.5);
colormap(gca, jet(256));
cb = colorbar; cb.Label.String = 'Longitud [°]';
hold on;

valid_corr = isfinite(h) & isfinite(anom_Bouguer);
p = polyfit(h(valid_corr), anom_Bouguer(valid_corr), 1);
h_fit = linspace(min(h(valid_corr)), max(h(valid_corr)), 200);
y_fit = polyval(p, h_fit);
plot(h_fit, y_fit, 'r-', 'LineWidth', 2.5);

y_obs = anom_Bouguer(valid_corr);
y_hat = polyval(p, h(valid_corr));
R2 = 1 - sum((y_obs - y_hat).^2) / sum((y_obs - mean(y_obs)).^2);

xlabel('Altura sobre geoide [m]', 'FontSize', 12);
ylabel(etiqueta_bouguer, 'FontSize', 12);
title({['Relación entre ' etiqueta_bouguer_corta ' y topografía'], ...
       sprintf('Pendiente = %.4f mGal/m | R² = %.3f', p(1), R2)}, ...
      'FontSize', 12, 'FontWeight','bold');
legend('Datos', sprintf('Regresión: %.4f·h + %.2f', p(1), p(2)), ...
       'Location','best', 'FontSize',10);
grid on; box on;
safe_export_fig(gcf, fig_dir, '07_correlacion_bouguer_topografia.png');

%% =========================================================
%  EXPORTAR SALIDAS OFICIALES PARA EL VISOR WEB
%% =========================================================

% Tabla oficial de análisis contextual por estación.
% Solo incluye estaciones GNSS retenidas tras QC.
% La relación con gravedad se reporta como contexto por proximidad,
% no como asociación directa punto-estación.
GNSS_tabla = table(GNSS.nombre(:), GNSS.lat(:), GNSS.lon(:), GNSS.h(:), ...
                   repmat(string(MARCO_REFERENCIA_GNSS), n_est, 1), repmat(string(GNSS_VECTOR_MODE), n_est, 1), ...
                   repmat("contextual_por_proximidad_no_asociacion_directa", n_est, 1), ...
                   repmat(DIST_CONTEXTUAL_KM, n_est, 1), ...
                   GNSS.duracion_yr(:), GNSS.n_puntos(:), ...
                   GNSS.dist_min_km(:), GNSS.dist_med_km(:), GNSS.dist_max_km(:), ...
                   GNSS.n_local(:), GNSS.n_contextual(:), GNSS.n_regional(:), GNSS.n_no_local(:), ...
                   GNSS.pct_100km(:), GNSS.pct_150km(:), GNSS.clase_espacial(:), ...
                   GNSS.bouguer_med_100km(:), GNSS.bouguer_mean_100km(:), ...
                   GNSS.grad_med_100km(:), GNSS.grad_max_100km(:), ...
                   GNSS.vE_mmyr(:), GNSS.vN_mmyr(:), GNSS.vU_mmyr(:), ...
                   GNSS.vH_mmyr(:), GNSS.azimuth_deg(:), ...
                   GNSS.vE_res_mmyr(:), GNSS.vN_res_mmyr(:), GNSS.vU_res_mmyr(:), ...
                   GNSS.vH_res_mmyr(:), GNSS.azimuth_res_deg(:), ...
                   GNSS.sigE_mmyr(:), GNSS.sigN_mmyr(:), GNSS.sigU_mmyr(:), GNSS.sigH_mmyr(:), GNSS.snrH(:), ...
                   'VariableNames', {'estacion','lat','lon','altura_m','marco_referencia','modo_vector_mapa', ...
                                     'tipo_relacion_gravedad_gnss','radio_resumen_contextual_km', ...
                                     'duracion_yr','n_puntos_grav', ...
                                     'dist_min_km','dist_med_km','dist_max_km', ...
                                     'n_0_50km','n_50_100km','n_100_150km','n_mayor_150km', ...
                                     'pct_hasta_100km','pct_hasta_150km','clase_contexto_espacial', ...
                                     'bouguer_mediana_100km_mgal','bouguer_media_100km_mgal', ...
                                     'gradiente_mediana_100km_mgal_km','gradiente_max_100km_mgal_km', ...
                                     'vel_e_abs_mm_yr','vel_n_abs_mm_yr','vel_u_abs_mm_yr', ...
                                     'vel_horizontal_abs_mm_yr','azimut_abs_grados', ...
                                     'vel_e_res_mm_yr','vel_n_res_mm_yr','vel_u_res_mm_yr', ...
                                     'vel_horizontal_res_mm_yr','azimut_res_grados', ...
                                     'sig_e_mm_yr','sig_n_mm_yr','sig_u_mm_yr','sig_h_mm_yr','snr_horizontal'});
writetable(GNSS_tabla, fullfile(out_dir, 'gnss_resumen_estaciones.csv'));

% Exportar puntos gravimétricos usados para el análisis contextual gravedad-GNSS.
% Esta tabla solo incluye puntos asociados a estaciones retenidas QC. Los puntos de
% estaciones excluidas NO aparecen aquí para evitar que entren en tablas de análisis.
% Todos los puntos, incluidos los de zonas excluidas del análisis GNSS, sí quedan
% incorporados en la grilla regional exportada más abajo.
clase_distancia_punto = strings(numel(dist_km),1);
clase_distancia_punto(dist_km <= DIST_LOCAL_KM) = "local_0_50km";
clase_distancia_punto(dist_km > DIST_LOCAL_KM & dist_km <= DIST_CONTEXTUAL_KM) = "contextual_50_100km";
clase_distancia_punto(dist_km > DIST_CONTEXTUAL_KM & dist_km <= DIST_REGIONAL_KM) = "regional_100_150km";
clase_distancia_punto(dist_km > DIST_REGIONAL_KM) = "no_local_mayor_150km";

idx_puntos_contextuales = ~estacion_excluida_qc(:);
tipo_relacion_punto = repmat("contextual_por_proximidad_no_asociacion_directa", sum(idx_puntos_contextuales), 1);

PuntosDist_tabla = table(lon(idx_puntos_contextuales), lat(idx_puntos_contextuales), ...
                         est_nombres(idx_puntos_contextuales), tipo_relacion_punto, ...
                         dist_km(idx_puntos_contextuales), clase_distancia_punto(idx_puntos_contextuales), ...
                         ag(idx_puntos_contextuales), anom_FA(idx_puntos_contextuales), ...
                         anom_Bouguer(idx_puntos_contextuales), GradH_puntos(idx_puntos_contextuales), ...
                         true(sum(idx_puntos_contextuales),1), ...
                         dist_km(idx_puntos_contextuales) <= DIST_CONTEXTUAL_KM, ...
                         dist_km(idx_puntos_contextuales) <= DIST_REGIONAL_KM, ...
                         'VariableNames', {'lon','lat','estacion_gnss_retenida','tipo_relacion_gravedad_gnss','dist_gnss_km','clase_distancia', ...
                                           'gravity_anomaly_base_mgal','aire_libre_mgal','bouguer_mgal','gradiente_mgal_km', ...
                                           'usar_grilla_regional','usar_resumen_contextual_100km','usar_contexto_regional_150km'});
writetable(PuntosDist_tabla, fullfile(out_dir, 'puntos_gravimetricos_clasificados.csv'));

% Exportar grilla mínima para web: lon, lat, anomalía base, aire libre, Bouguer, topografía y gradiente
Grid_tabla = table(LON_G(:), LAT_G(:), AG_G(:), FA_G(:), BG_G(:), H_G(:), GradH(:), ...
                   'VariableNames', {'lon','lat','gravity_anomaly_base_mgal','aire_libre_mgal','bouguer_mgal','altura_m','gradiente_mgal_km'});
Grid_tabla = Grid_tabla(isfinite(Grid_tabla.bouguer_mgal) & isfinite(Grid_tabla.gradiente_mgal_km), :);
writetable(Grid_tabla, fullfile(out_dir, 'grilla_bouguer_gradiente.csv'));

% Metadata oficial para que el visor pueda describir capas, unidades y cautelas.
metadata = struct();
metadata.proyecto = "SismoTectoLab";
metadata.version_codigo = "V7";
metadata.fecha_generacion = string(datetime('now','Format','yyyy-MM-dd HH:mm:ss'));
metadata.marco_referencia_gnss = string(MARCO_REFERENCIA_GNSS);
metadata.modo_gnss = string(GNSS_MODO);
metadata.modo_vector_mapa = string(GNSS_VECTOR_MODE);
metadata.tipo_tratamiento_gravedad = string(GRAVITY_INPUT_TIPO);
metadata.relacion_gravedad_gnss = "contextual_por_proximidad_no_asociacion_directa";
metadata.nota_relacion_gravedad_gnss = "Las estaciones GNSS y los puntos gravimetricos se comparan por proximidad espacial. No se interpreta que un punto gravimetrico pertenezca directamente a una estacion GNSS.";
metadata.n_estaciones_gnss_retenidas = n_est;
metadata.estaciones_gnss_retenidas = string(GNSS.nombre(:));
metadata.n_estaciones_gnss_excluidas_qc = numel(EXCLUIR_ESTACIONES_GNSS);
metadata.nota_estaciones_excluidas = "Las estaciones excluidas por QC temporal/cinematico no se exportan en tablas oficiales de analisis contextual. Sus puntos gravimetricos se conservan en la grilla regional.";
metadata.umbrales_distancia_km = struct('local', DIST_LOCAL_KM, 'contextual', DIST_CONTEXTUAL_KM, 'regional', DIST_REGIONAL_KM);
metadata.umbrales_gradiente_mgal_km = struct('p75_probable', thr_grad_probable, 'p90_definido', thr_grad_definido, 'p95_alto', thr_grad_alto);
metadata.archivos_oficiales = ["grilla_bouguer_gradiente.csv", "gnss_resumen_estaciones.csv", "puntos_gravimetricos_clasificados.csv", "metadata_variables.json", "figuras/"];
metadata.variables = struct();
metadata.variables.gravity_anomaly_base_mgal = struct('nombre', "Anomalia gravimetrica base", 'unidad', "mGal", 'descripcion', "Dato gravimetrico original del insumo, conservado sin modificacion.");
metadata.variables.aire_libre_mgal = struct('nombre', "Anomalia de aire libre simple", 'unidad', "mGal", 'descripcion', "Variable derivada a partir del dato base y la correccion de aire libre por altura.");
metadata.variables.bouguer_mgal = struct('nombre', "Anomalia de Bouguer simple", 'unidad', "mGal", 'descripcion', "Variable derivada despues de aplicar correccion de aire libre y placa de Bouguer simple.");
metadata.variables.gradiente_mgal_km = struct('nombre', "Gradiente horizontal de Bouguer", 'unidad', "mGal/km", 'descripcion', "Gradiente calculado sobre la grilla interpolada de Bouguer usando conversion aproximada de grados a kilometros.");
metadata.variables.vel_horizontal_res_mm_yr = struct('nombre', "Velocidad horizontal residual GNSS", 'unidad', "mm/año", 'descripcion', "Magnitud horizontal despues de remover la media de la red GNSS retenida. Util para visualizacion diferencial en IGS20/ITRF2020.");

try
    metadata_txt = jsonencode(metadata, 'PrettyPrint', true);
catch
    metadata_txt = jsonencode(metadata);
end
fid = fopen(fullfile(out_dir, 'metadata_variables.json'), 'w');
if fid == -1
    warning('No se pudo crear metadata_variables.json');
else
    fprintf(fid, '%s', metadata_txt);
    fclose(fid);
end

%% =========================================================
%  RESUMEN EN CONSOLA
%% =========================================================
fprintf('\n========================================\n');
fprintf('  RESUMEN SISMOTECTÓNICO CORREGIDO\n');
fprintf('========================================\n');
fprintf('Zona: Lat [%.2f, %.2f]  Lon [%.2f, %.2f]\n', min(lat),max(lat),min(lon),max(lon));
fprintf('Estaciones GNSS excluidas del análisis vectorial por QC: %d (no se exportan en tablas oficiales de análisis).\n', numel(EXCLUIR_ESTACIONES_GNSS));
fprintf('\n%s:\n', etiqueta_bouguer_corta);
fprintf('  Min: %.2f mGal  Max: %.2f mGal  Media: %.2f mGal\n', ...
    min(anom_Bouguer),max(anom_Bouguer),mean(anom_Bouguer));
fprintf('  Tratamiento gravedad: %s | gravity_anomaly se conserva como base y las anomalías derivadas se calculan aparte.\n', GRAVITY_INPUT_TIPO);
fprintf('\nGradiente horizontal:\n');
fprintf('  Max: %.2f mGal/km\n', max(GradH_valid));
fprintf('  Umbrales relativos: P75=%.2f | P90=%.2f | P95=%.2f mGal/km\n', ...
    thr_grad_probable, thr_grad_definido, thr_grad_alto);

fprintf('\nGNSS — %s | Marco: %s | Modo vector mapa: %s:\n', etiqueta_gnss, MARCO_REFERENCIA_GNSS, GNSS_VECTOR_MODE);
for i = 1:n_est
    flag = '';
    if GNSS.duracion_yr(i) < MIN_DURACION_GNSS_YR, flag = '  [serie corta]'; end
    fprintf('  %s: Abs H=%8.2f | Res H=%8.2f | Res U=%8.2f mm/año | %.2f años%s\n', ...
        GNSS.nombre{i}, GNSS.vH_mmyr(i), GNSS.vH_res_mmyr(i), GNSS.vU_res_mmyr(i), ...
        GNSS.duracion_yr(i), flag);
end

fprintf('  Nota QC: las estaciones excluidas por control temporal/cinemático no se listan en tablas oficiales de análisis contextual.\n');

fprintf('\nRelación espacial gravedad-GNSS solo para estaciones retenidas:\n');
for i = 1:n_est
    fprintf('  %s: med=%.1f km | max=%.1f km | <=100km=%.1f%% | <=150km=%.1f%% | %s\n', ...
        GNSS.nombre{i}, GNSS.dist_med_km(i), GNSS.dist_max_km(i), ...
        GNSS.pct_100km(i), GNSS.pct_150km(i), char(GNSS.clase_espacial(i)));
end
fprintf('  Nota: los puntos >%.0f km se conservan para grilla regional, pero no para interpretación local por estación.\n', DIST_REGIONAL_KM);

fprintf('\nRelación Bouguer-topografía:\n');
fprintf('  Pendiente: %.4f mGal/m | R² = %.3f\n', p(1), R2);
if p(1) > 0
    fprintf('  → Relación positiva: interpretar con cautela; puede reflejar tendencia regional o dependencia residual con la topografía.\n');
elseif p(1) < 0
    fprintf('  → Relación negativa: compatible con compensación regional o contraste isostático.\n');
else
    fprintf('  → Relación casi nula entre Bouguer y altura en esta muestra.\n');
end
fprintf('\nArchivos oficiales exportados en: %s\n', out_dir);
fprintf('  - grilla_bouguer_gradiente.csv\n');
fprintf('  - gnss_resumen_estaciones.csv\n');
fprintf('  - puntos_gravimetricos_clasificados.csv\n');
fprintf('  - metadata_variables.json\n');
fprintf('  - figuras/*.png\n');
fprintf('========================================\n');

%% =========================================================
%  FUNCIONES AUXILIARES
%% =========================================================
function safe_export_fig(fig_handle, fig_dir, file_name)
    % Exporta una figura en PNG para el visor sin detener el script si falla.
    if ~exist(fig_dir, 'dir'), mkdir(fig_dir); end
    out_file = fullfile(fig_dir, file_name);
    try
        exportgraphics(fig_handle, out_file, 'Resolution', 180);
    catch
        try
            saveas(fig_handle, out_file);
        catch ME
            warning('No se pudo exportar la figura %s: %s', file_name, ME.message);
        end
    end
end

function plot_gnss_vectors(GNSS, colorSpec, lineWidth, headSize)
    % Dibuja vectores GNSS horizontales normalizados para visualización.
    % La magnitud real usada para el mapa está en GNSS.vH_plot_mmyr; estas flechas solo representan dirección
    % y magnitud relativa para no saturar el mapa.
    for ii = 1:numel(GNSS.lon)
        quiver(GNSS.lon(ii), GNSS.lat(ii), GNSS.vecE_plot(ii), GNSS.vecN_plot(ii), ...
               0, 'Color', colorSpec, 'LineWidth', lineWidth, 'MaxHeadSize', headSize);
    end
end

function m = median_radius(x, d, maxdist)
    idx = d <= maxdist & isfinite(x);
    if any(idx)
        m = median(x(idx));
    else
        m = NaN;
    end
end

function m = mean_radius(x, d, maxdist)
    idx = d <= maxdist & isfinite(x);
    if any(idx)
        m = mean(x(idx));
    else
        m = NaN;
    end
end

function m = max_radius(x, d, maxdist)
    idx = d <= maxdist & isfinite(x);
    if any(idx)
        m = max(x(idx));
    else
        m = NaN;
    end
end


function c = redblue(n)
    % Colormap divergente rojo-blanco-azul.
    if nargin < 1, n = 64; end
    x = linspace(0,1,n)';
    r = min(2-2*x, 1); r(x<0.5) = 1;
    g = 1 - abs(2*x-1);
    b = min(2*x, 1); b(x>0.5) = 1;
    c = [r g b];
end

function y = pct(x, p)
    % Percentil robusto ignorando NaN/Inf.
    xv = x(isfinite(x));
    if isempty(xv)
        y = NaN;
    else
        y = prctile(xv, p);
    end
end
