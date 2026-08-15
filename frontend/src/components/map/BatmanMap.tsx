import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'

interface MapProps {
  style?: 'dark' | 'satellite'
  center?: [number, number]  // [lon, lat]
  zoom?: number
  onMapReady?: (map: maplibregl.Map) => void
}

/**
 * BatmanMap — Primary GIS component using MapLibre GL.
 * Uses a free dark tile style. Production: swap with GeoServer WMS.
 */
export default function BatmanMap({
  style = 'dark',
  center = [76.9, 34.2],   // Default: Kargil sector, J&K
  zoom = 10,
  onMapReady,
}: MapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)

  const tileStyle = style === 'dark'
    ? 'https://tiles.openfreemap.org/styles/liberty'   // free OSM dark style
    : 'https://tiles.openfreemap.org/styles/positron'

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: tileStyle,
      center,
      zoom,
      attributionControl: false,
      pitchWithRotate: true,
    })

    // Navigation controls
    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right')
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 120 }), 'bottom-left')

    map.on('load', () => {
      mapRef.current = map

      // ── DEMO: AOR boundary polygon ─────────────────────────
      map.addSource('aor', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [[
              [76.7, 34.0], [77.1, 34.0], [77.1, 34.4],
              [76.7, 34.4], [76.7, 34.0]
            ]],
          },
          properties: { name: 'AOR — KARGIL SECTOR' },
        },
      })
      map.addLayer({
        id: 'aor-fill',
        type: 'fill',
        source: 'aor',
        paint: {
          'fill-color': 'rgba(245, 158, 11, 0.05)',
          'fill-outline-color': 'rgba(245, 158, 11, 0.6)',
        },
      })
      map.addLayer({
        id: 'aor-border',
        type: 'line',
        source: 'aor',
        paint: {
          'line-color': 'rgba(245, 158, 11, 0.8)',
          'line-width': 2,
          'line-dasharray': [4, 2],
        },
      })

      // ── DEMO: Friendly unit positions ──────────────────────
      map.addSource('units', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [
            { type: 'Feature', geometry: { type: 'Point', coordinates: [76.85, 34.15] }, properties: { id: 'ALPHA', name: 'ALPHA Coy', status: 'GREEN', type: 'Infantry' } },
            { type: 'Feature', geometry: { type: 'Point', coordinates: [76.95, 34.25] }, properties: { id: 'BRAVO', name: 'BRAVO Coy', status: 'AMBER', type: 'Infantry' } },
            { type: 'Feature', geometry: { type: 'Point', coordinates: [77.05, 34.10] }, properties: { id: 'QRT-1', name: 'QRT NORTH', status: 'GREEN', type: 'QRT' } },
          ],
        },
      })
      map.addLayer({
        id: 'units-circle',
        type: 'circle',
        source: 'units',
        paint: {
          'circle-radius': 10,
          'circle-color': [
            'match', ['get', 'status'],
            'GREEN', '#22c55e',
            'AMBER', '#f59e0b',
            'RED',   '#ef4444',
            '#6b7280'
          ],
          'circle-opacity': 0.9,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#0a0c0f',
        },
      })

      // ── DEMO: Threat heatmap zone ──────────────────────────
      map.addSource('threat-zone', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [77.0, 34.35] },
          properties: { probability: 0.83, type: 'INFILTRATION' },
        },
      })
      map.addLayer({
        id: 'threat-zone-halo',
        type: 'circle',
        source: 'threat-zone',
        paint: {
          'circle-radius': 40,
          'circle-color': 'rgba(239, 68, 68, 0.12)',
          'circle-stroke-color': 'rgba(239, 68, 68, 0.5)',
          'circle-stroke-width': 1.5,
        },
      })

      // Popup on unit click
      map.on('click', 'units-circle', (e) => {
        const props = e.features?.[0]?.properties
        if (!props) return
        new maplibregl.Popup({ closeButton: false, maxWidth: '200px' })
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="font-family:Inter,sans-serif;font-size:12px;color:#e8eaf0;background:#1a2130;padding:8px;border-radius:4px">
              <strong>${props.name}</strong><br/>
              Status: <span style="color:${props.status==='GREEN'?'#22c55e':props.status==='AMBER'?'#f59e0b':'#ef4444'}">${props.status}</span><br/>
              Type: ${props.type}
            </div>
          `)
          .addTo(map)
      })
      map.on('mouseenter', 'units-circle', () => { map.getCanvas().style.cursor = 'pointer' })
      map.on('mouseleave', 'units-circle', () => { map.getCanvas().style.cursor = '' })

      onMapReady?.(map)
    })

    return () => { map.remove(); mapRef.current = null }
  }, [])

  return (
    <div
      ref={containerRef}
      className="map-container"
      id="batman-main-map"
      style={{ width: '100%', height: '100%' }}
    />
  )
}
