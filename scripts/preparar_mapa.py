"""Límites de los 26 ámbitos (24 departamentos, Callao, Lima Metropolitana y
Lima Provincias) a partir de los límites provinciales del INEI.

Fuente: INEI (2007), Límite Provincial, publicado en el Geoservidor del MINAM y
GEOIDEP; convertido a GeoJSON en https://github.com/juaneladio/peru-geojson
(licencia MPL-2.0).

Uso:
    python scripts/preparar_mapa.py
"""

import urllib.request

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient

from procesar import DEPARTAMENTOS, ORIGINALES, RAIZ

URL = "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_provincial_simple.geojson"
ORIGEN = ORIGINALES / "limites" / "peru_provincial_simple.geojson"
DESTINO = RAIZ / "web" / "data" / "ambitos.geojson"

def horario(geom):
    """D3 espera el anillo exterior en sentido horario (al revés que RFC 7946)."""
    if isinstance(geom, Polygon):
        return orient(geom, sign=-1.0)
    return MultiPolygon([orient(g, sign=-1.0) for g in geom.geoms])


if __name__ == "__main__":
    ORIGEN.parent.mkdir(parents=True, exist_ok=True)
    if not ORIGEN.exists():
        urllib.request.urlretrieve(URL, ORIGEN)
    g = gpd.read_file(ORIGEN)
    g["codigo"] = g.FIRST_IDPR.str[:2].astype(int)
    g.loc[g.FIRST_IDPR == "1501", "codigo"] = 26
    a = g.dissolve(by="codigo").reset_index()[["codigo", "geometry"]]
    a["ambito"] = a.codigo.map(DEPARTAMENTOS)
    assert a.ambito.notna().all() and len(a) == 26
    a["geometry"] = a.geometry.simplify(0.01, preserve_topology=True).map(horario)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    a.to_file(DESTINO, driver="GeoJSON")
    print(a[["codigo", "ambito"]].to_string(index=False), f"\n{DESTINO.stat().st_size / 1e3:.0f} KB")
