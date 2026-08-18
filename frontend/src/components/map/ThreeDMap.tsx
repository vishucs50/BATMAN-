import { useRef, useMemo, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Line, Sphere, Box, useGLTF } from '@react-three/drei';
import * as THREE from 'three';

// Preload the model
useGLTF.preload('/assets/brahmos.glb');

// ─── Global right-shift ───────────────────────
const OX = 9; // scene offset X — shift far right away from hero text

// ─────────────────────────────────────────────
// TERRAIN
// ─────────────────────────────────────────────
const Terrain = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const wireRef = useRef<THREE.Mesh>(null);

  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(40, 40, 100, 100);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z =
        Math.sin(x * 0.4) * Math.cos(y * 0.4) * 2.0 +
        Math.sin(x * 0.9 + y * 0.6) * 1.2 +
        Math.cos(x * 0.2 - y * 0.5) * 1.8 +
        Math.sin(x * 1.5 + 0.3) * Math.cos(y * 1.5) * 0.5;
      pos.setZ(i, z);
    }
    geo.computeVertexNormals();
    return geo;
  }, []);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (meshRef.current) meshRef.current.rotation.z = t * 0.025;
    if (wireRef.current) wireRef.current.rotation.z = t * 0.025;
  });

  return (
    <group rotation={[-Math.PI / 2.1, 0, 0]} position={[OX, -3, -2]}>
      <mesh ref={meshRef} geometry={geometry}>
        <meshStandardMaterial color="#040410" roughness={1} metalness={0} />
      </mesh>
      <mesh ref={wireRef} geometry={geometry}>
        <meshBasicMaterial color="#3D3DFF" wireframe transparent opacity={0.22} />
      </mesh>
      <gridHelper args={[40, 40, '#0000AD', '#08085E']} rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0.05]} />
    </group>
  );
};

// ─────────────────────────────────────────────
// COORDINATE GRID LABELS
// ─────────────────────────────────────────────
const CoordinateGrid = () => {
  const labels = useMemo(() => {
    const out: { x: number; z: number; label: string }[] = [];
    for (let i = -2; i <= 2; i++) {
      for (let j = -2; j <= 2; j++) {
        out.push({
          x: i * 3.5 + OX,
          z: j * 3.5,
          label: `${(28.6 + i * 0.15).toFixed(2)}°N ${(77.2 + j * 0.15).toFixed(2)}°E`,
        });
      }
    }
    return out;
  }, []);

  return (
    <>
      {labels.map((l, i) => (
        <Html key={i} position={[l.x, 0.1, l.z]} center>
          <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: '8px', color: 'rgba(0,0,238,0.32)', pointerEvents: 'none', whiteSpace: 'nowrap' }}>
            {l.label}
          </div>
        </Html>
      ))}
    </>
  );
};

// ─────────────────────────────────────────────
// THREAT PULSE — single expanding ring
// ─────────────────────────────────────────────
const ThreatPulse = ({ position, color }: { position: [number, number, number]; color: string }) => {
  const ringRef = useRef<THREE.Mesh>(null);
  const phase = useMemo(() => Math.random() * Math.PI * 2, []);

  useFrame(({ clock }) => {
    if (!ringRef.current) return;
    const t = ((clock.elapsedTime * 0.9 + phase) % 2.5) / 2.5;
    ringRef.current.scale.setScalar(0.4 + t * 5);
    (ringRef.current.material as THREE.MeshBasicMaterial).opacity = (1 - t) * 0.55;
  });

  const [px, py, pz] = position;
  return (
    <group position={[px + OX, py, pz]}>
      <mesh ref={ringRef} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.38, 0.52, 48]} />
        <meshBasicMaterial color={color} transparent opacity={0.55} side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.3, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
      <Sphere args={[0.13, 16, 16]}>
        <meshBasicMaterial color={color} />
      </Sphere>
    </group>
  );
};

// ─────────────────────────────────────────────
// RADAR SCAN LINE
// ─────────────────────────────────────────────
const ScanLine = () => {
  const ref = useRef<THREE.Group>(null);
  useFrame(({ clock }) => {
    if (ref.current) ref.current.rotation.y = clock.elapsedTime * 0.6;
  });
  return (
    <group ref={ref} position={[OX, 0.15, 0]}>
      <Line points={[[0, 0, 0], [12, 0, 0]]} color="#0000EE" lineWidth={1.5} transparent opacity={0.22} />
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[12, 32, 0, Math.PI / 6]} />
        <meshBasicMaterial color="#0000EE" transparent opacity={0.04} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
};

// ─────────────────────────────────────────────
// IMPACT EXPLOSION at target
// ─────────────────────────────────────────────
const ImpactExplosion = ({ position, visible }: { position: THREE.Vector3; visible: boolean }) => {
  const ring1 = useRef<THREE.Mesh>(null);
  const ring2 = useRef<THREE.Mesh>(null);
  const core = useRef<THREE.Mesh>(null);
  const startedAt = useRef(0);
  const wasVisible = useRef(false);

  useFrame(({ clock }) => {
    if (!visible) { wasVisible.current = false; return; }
    if (!wasVisible.current) { startedAt.current = clock.elapsedTime; wasVisible.current = true; }
    const t = Math.min((clock.elapsedTime - startedAt.current) / 1.2, 1);

    if (ring1.current) {
      ring1.current.scale.setScalar(0.2 + t * 6);
      (ring1.current.material as THREE.MeshBasicMaterial).opacity = (1 - t) * 0.7;
    }
    if (ring2.current) {
      const t2 = Math.min(t * 1.4, 1);
      ring2.current.scale.setScalar(0.1 + t2 * 4);
      (ring2.current.material as THREE.MeshBasicMaterial).opacity = (1 - t2) * 0.5;
    }
    if (core.current) {
      core.current.scale.setScalar(1 + t * 2);
      (core.current.material as THREE.MeshBasicMaterial).opacity = (1 - t) * 0.9;
    }
  });

  return (
    <group position={position} visible={visible}>
      <mesh ref={ring1} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.4, 0.6, 48]} />
        <meshBasicMaterial color="#FF4136" transparent opacity={0} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={ring2} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.3, 0.5, 48]} />
        <meshBasicMaterial color="#F59E0B" transparent opacity={0} side={THREE.DoubleSide} />
      </mesh>
      <Sphere ref={core} args={[0.25, 16, 16]}>
        <meshBasicMaterial color="#ffffff" transparent opacity={0} />
      </Sphere>
    </group>
  );
};

// ─────────────────────────────────────────────
// BRAHMOS MISSILE — loads GLB, flies arc, hits target, repeats
// ─────────────────────────────────────────────
const LAUNCH = new THREE.Vector3(-3 + OX, 0.5, 3);    // friendly unit position
const TARGET = new THREE.Vector3(6 + OX, 0.5, -5);    // threat position

const CYCLE_DURATION = 8; // seconds per full launch→impact cycle

const BrahmosMissile = () => {
  const { scene } = useGLTF('/assets/brahmos.glb');
  const missileRef = useRef<THREE.Group>(null);
  const trailRef = useRef<{ pts: [number, number, number][] }>({ pts: [] });
  const [trailPts, setTrailPts] = useState<[number, number, number][]>([]);
  const [showImpact, setShowImpact] = useState(false);
  const impactPos = useMemo(() => TARGET.clone(), []);

  // Clone scene so material overrides don't conflict
  const model = useMemo(() => {
    const cloned = scene.clone(true);
    cloned.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const m = child as THREE.Mesh;
        // Tint the model with a slight metallic look
        if (Array.isArray(m.material)) {
          m.material = m.material.map((mat) => {
            const n = (mat as THREE.MeshStandardMaterial).clone();
            n.emissive = new THREE.Color('#3D3DFF');
            n.emissiveIntensity = 0.25;
            return n;
          });
        } else {
          const n = (m.material as THREE.MeshStandardMaterial).clone();
          n.emissive = new THREE.Color('#3D3DFF');
          n.emissiveIntensity = 0.25;
          m.material = n;
        }
      }
    });
    return cloned;
  }, [scene]);

  // Fit model size — scale to ~1.8 units long for visibility
  const modelScale = useMemo(() => {
    const box = new THREE.Box3().setFromObject(model);
    const size = new THREE.Vector3();
    box.getSize(size);
    const maxDim = Math.max(size.x, size.y, size.z);
    return 1.8 / maxDim;
  }, [model]);

  // Bezier arc
  const mid = useMemo(() => {
    const m = LAUNCH.clone().lerp(TARGET, 0.5);
    m.y += LAUNCH.distanceTo(TARGET) * 0.75;
    return m;
  }, []);

  const curve = useMemo(() => new THREE.QuadraticBezierCurve3(LAUNCH, mid, TARGET), [mid]);
  const arcPoints = useMemo(
    () => curve.getPoints(60).map((p) => [p.x, p.y, p.z] as [number, number, number]),
    [curve]
  );

  useFrame(({ clock }) => {
    if (!missileRef.current) return;

    const raw = clock.elapsedTime % CYCLE_DURATION;
    // First 0.5s = launch delay; next 5s = flight; 0.5s impact flash; rest = reset
    const FLIGHT = 5;
    const DELAY = 0.5;

    if (raw < DELAY) {
      // Sitting at launch pad
      missileRef.current.visible = false;
      setShowImpact(false);
      trailRef.current.pts = [];
      setTrailPts([]);
      return;
    }

    const flightT = (raw - DELAY) / FLIGHT;

    if (flightT >= 1) {
      // Impact phase
      missileRef.current.visible = false;
      if (!showImpact) setShowImpact(true);
      return;
    }

    setShowImpact(false);
    missileRef.current.visible = true;

    const pt = curve.getPoint(flightT);
    missileRef.current.position.copy(pt);

    // Orient: missile's local +Z toward travel direction
    const tangent = curve.getTangent(flightT).normalize();
    const up = new THREE.Vector3(0, 1, 0);
    const quat = new THREE.Quaternion().setFromUnitVectors(up, tangent);
    missileRef.current.setRotationFromQuaternion(quat);

    // Live trail — keep last 20 points
    const newPts = [...trailRef.current.pts, [pt.x, pt.y, pt.z] as [number, number, number]];
    if (newPts.length > 35) newPts.shift();
    trailRef.current.pts = newPts;
    setTrailPts([...newPts]);
  });

  return (
    <>
      {/* Faint full arc path */}
      <Line points={arcPoints} color="#3D3DFF" lineWidth={1} transparent opacity={0.08} />

      {/* Launch pad marker */}
      <group position={LAUNCH}>
        <Sphere args={[0.18, 16, 16]}>
          <meshBasicMaterial color="#3D3DFF" />
        </Sphere>
        <Html position={[0.7, 0.7, 0]} center>
          <div style={{ background: 'rgba(17,17,22,0.93)', border: '1px solid rgba(61,61,255,0.55)', padding: '5px 9px', fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: '#fff', whiteSpace: 'nowrap', pointerEvents: 'none', boxShadow: '0 0 12px rgba(61,61,255,0.3)' }}>
            <div style={{ color: '#3D3DFF', fontWeight: 700 }}>BRAHMOS LAUNCHER</div>
            <div style={{ color: '#53AC85' }}>UNIT-07 · READY</div>
          </div>
        </Html>
      </group>

      {/* Target marker */}
      <group position={TARGET}>
        <Sphere args={[0.14, 16, 16]}>
          <meshBasicMaterial color="#FF4136" />
        </Sphere>
        <Html position={[0.6, 0.6, 0]} center>
          <div style={{ background: 'rgba(17,17,22,0.93)', border: '1px solid rgba(255,65,54,0.5)', padding: '5px 9px', fontFamily: 'IBM Plex Mono, monospace', fontSize: '10px', color: '#fff', whiteSpace: 'nowrap', pointerEvents: 'none' }}>
            <div style={{ color: '#FF4136', fontWeight: 700 }}>TARGET-ALPHA</div>
            <div style={{ color: '#9E9E9E' }}>PROB: 0.84</div>
          </div>
        </Html>
      </group>

      {/* Live exhaust trail */}
      {trailPts.length > 1 && (
        <Line points={trailPts} color="#ffffff" lineWidth={2.5} transparent opacity={0.5} />
      )}
      {trailPts.length > 4 && (
        <Line points={trailPts.slice(-12)} color="#F59E0B" lineWidth={1.5} transparent opacity={0.3} />
      )}

      {/* BrahMos GLB model */}
      <group ref={missileRef} scale={modelScale} visible={false}>
        <primitive object={model} />
      </group>

      {/* Impact explosion */}
      <ImpactExplosion position={impactPos} visible={showImpact} />
    </>
  );
};

// ─────────────────────────────────────────────
// UNIT MARKERS (HQ + Unit-12 remain)
// ─────────────────────────────────────────────
const labelBase: React.CSSProperties = {
  background: 'rgba(17,17,22,0.93)',
  padding: '5px 9px',
  fontFamily: 'IBM Plex Mono, monospace',
  fontSize: '10px',
  color: '#fff',
  whiteSpace: 'nowrap',
  pointerEvents: 'none',
};

const UnitMarkers = () => {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 1400);
    return () => clearInterval(id);
  }, []);
  const readiness = useMemo(() => Math.floor(88 + Math.random() * 7), [tick]);

  return (
    <group>
      {/* HQ */}
      <group position={[0 + OX, 0.3, -1]}>
        <Box args={[0.35, 0.35, 0.35]}>
          <meshBasicMaterial color="#F59E0B" />
        </Box>
        <Html position={[0, 0.8, 0]} center>
          <div style={{ ...labelBase, border: '1px solid rgba(245,158,11,0.5)', boxShadow: '0 0 10px rgba(245,158,11,0.2)' }}>
            <div style={{ color: '#F59E0B', fontWeight: 700 }}>HQ-ALPHA</div>
            <div style={{ color: '#9E9E9E' }}>COA-02 ACTIVE</div>
          </div>
        </Html>
      </group>

      {/* UNIT-12 */}
      <group position={[3 + OX, 0.5, 3]}>
        <Sphere args={[0.16, 16, 16]}>
          <meshBasicMaterial color="#22C55E" />
        </Sphere>
        <Html position={[0.6, 0.6, 0]} center>
          <div style={{ ...labelBase, border: '1px solid rgba(34,197,94,0.5)' }}>
            <div style={{ color: '#22C55E', fontWeight: 700 }}>UNIT-12</div>
            <div style={{ color: '#9E9E9E' }}>READINESS: {readiness}%</div>
          </div>
        </Html>
      </group>

      {/* COA route lines */}
      <Line points={[[3 + OX, 0.5, 3], [1.5 + OX, 1.0, 1], [0 + OX, 0.5, -1]]}
        color="#22C55E" lineWidth={1.5} dashed dashSize={0.2} gapSize={0.15} />
      <Line points={[[-3 + OX, 0.5, 2.5], [-1 + OX, 1.2, 0.5], [0 + OX, 0.5, -1]]}
        color="#F59E0B" lineWidth={2} dashed dashSize={0.25} gapSize={0.12} />

      <group position={[-1.5 + OX, 2.2, 0.5]}>
        <Html center>
          <div style={{ ...labelBase, border: '1px solid rgba(245,158,11,0.4)' }}>
            <div style={{ color: '#F59E0B' }}>COA-02</div>
            <div style={{ color: '#22C55E' }}>SUCCESS: 87%</div>
          </div>
        </Html>
      </group>
    </group>
  );
};

// ─────────────────────────────────────────────
// SCENE
// ─────────────────────────────────────────────
const Scene = () => {
  const threats = useMemo<{ pos: [number, number, number]; color: string }[]>(() => [
    { pos: [6, 0.5, -5], color: '#FF4136' },
    { pos: [7, 0.5, 3], color: '#FF4136' },
    { pos: [-6, 0.5, -4], color: '#F59E0B' },
  ], []);

  return (
    <>
      <color attach="background" args={['#050507']} />
      <fog attach="fog" args={['#050507', 14, 34]} />

      <ambientLight intensity={0.6} />
      <pointLight position={[OX, 14, 0]} intensity={1.2} color="#3D3DFF" />
      <pointLight position={[6 + OX, 8, 0]} intensity={0.8} color="#FF4136" />
      <pointLight position={[OX, 8, 6]} intensity={0.5} color="#F59E0B" />
      <pointLight position={[OX, 6, -6]} intensity={0.4} color="#ffffff" />

      <Suspense fallback={null}>
        <Terrain />
        <CoordinateGrid />
        <ScanLine />
        <UnitMarkers />

        {threats.map((t, i) => (
          <ThreatPulse key={i} position={t.pos} color={t.color} />
        ))}

        <BrahmosMissile />
      </Suspense>

      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.3}
        maxPolarAngle={Math.PI / 2.2}
        minPolarAngle={Math.PI / 3.8}
        target={[OX + 2, 0, -1]}
      />
    </>
  );
};

// ─────────────────────────────────────────────
// EXPORT
// ─────────────────────────────────────────────
export const ThreeDMap = () => (
  <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
    <Canvas camera={{ position: [OX + 2, 7, 10], fov: 55 }} style={{ width: '100%', height: '100%' }} gl={{ antialias: true, alpha: false }}>
      <Scene />
    </Canvas>
  </div>
);
