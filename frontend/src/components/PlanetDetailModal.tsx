import React, { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { campaignsApi } from '@/api/client'
import type { Planet } from '@/types/api'
import * as THREE from 'three'

interface PlanetDetailModalProps {
  planet: Planet
  onClose: () => void
}

const PlanetDetailModal: React.FC<PlanetDetailModalProps> = ({ planet, onClose }) => {
  const { data: games, isLoading } = useQuery({
    queryKey: ['planetGames', planet.id],
    queryFn: async () => (await campaignsApi.getPlanetGames(planet.id)).data,
  })
  
  const planetCanvasRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!planetCanvasRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000)
    camera.position.z = 4.5

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(200, 200)
    renderer.setPixelRatio(window.devicePixelRatio)
    planetCanvasRef.current.appendChild(renderer.domElement)

    // Determine material properties based on planet type
    let shininess = 10
    let specular = 0x444444
    let emissiveIntensity = planet.is_contested ? 0.4 : 0.05
    
    const planetTypeLower = planet.planet_type.toLowerCase()
    
    if (planetTypeLower.includes('ice') || planetTypeLower.includes('frozen')) {
      shininess = 50
      specular = 0x999999
    } else if (planetTypeLower.includes('desert') || planetTypeLower.includes('arid')) {
      shininess = 3
      specular = 0x222222
    } else if (planetTypeLower.includes('ocean') || planetTypeLower.includes('water')) {
      shininess = 60
      specular = 0xbbbbbb
    } else if (planetTypeLower.includes('forge') || planetTypeLower.includes('industrial')) {
      shininess = 25
      specular = 0x888888
      emissiveIntensity = 0.2
    } else if (planetTypeLower.includes('volcanic') || planetTypeLower.includes('lava')) {
      shininess = 15
      specular = 0xff4400
      emissiveIntensity = 0.3
    } else if (planetTypeLower.includes('death') || planetTypeLower.includes('barren')) {
      shininess = 2
      specular = 0x111111
    }
    
    // Helper function to generate procedural planet texture
    const generatePlanetTexture = () => {
      const canvas = document.createElement('canvas')
      canvas.width = 2048
      canvas.height = 1024
      const ctx = canvas.getContext('2d')!
      
      // Advanced noise function with multiple octaves
      const noise = (x: number, y: number, scale: number, octaves: number = 1) => {
        let value = 0
        let amplitude = 1
        let frequency = scale
        
        for (let i = 0; i < octaves; i++) {
          value += Math.sin(x * frequency) * Math.cos(y * frequency) * amplitude
          amplitude *= 0.5
          frequency *= 2
        }
        
        return value * 0.5 + 0.5
      }
      
      // Create detailed terrain
      for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
          const nx = x / canvas.width
          const ny = y / canvas.height
          
          let r, g, b
          const baseColor = parseInt(planet.color.slice(1), 16)
          const baseR = (baseColor >> 16) & 255
          const baseG = (baseColor >> 8) & 255
          const baseB = baseColor & 255
          
          // Multi-octave terrain generation
          const elevation = noise(nx * 6, ny * 6, 5, 4)
          const detail = noise(nx * 30, ny * 30, 15, 2)
          const microDetail = noise(nx * 60, ny * 60, 25, 1)
          
          if (planetTypeLower.includes('ocean') || planetTypeLower.includes('water')) {
            if (elevation > 0.58) {
              r = baseR * (0.6 + detail * 0.3)
              g = baseG * (0.8 + detail * 0.2)
              b = baseB * (0.5 + detail * 0.2)
            } else if (elevation > 0.52) {
              r = baseR * 0.5
              g = baseG * 0.7
              b = baseB * 1.1
            } else {
              r = baseR * (0.2 + microDetail * 0.1)
              g = baseG * (0.3 + microDetail * 0.1)
              b = baseB * (1.0 + microDetail * 0.2)
            }
          } else if (planetTypeLower.includes('desert') || planetTypeLower.includes('arid')) {
            const dune = noise(nx * 25, ny * 25, 18, 3) * 0.4
            const rocky = microDetail > 0.7 ? 0.3 : 0
            r = baseR * (0.7 + dune + rocky)
            g = baseG * (0.6 + dune * 0.8 + rocky * 0.5)
            b = baseB * (0.4 + dune * 0.5 + rocky * 0.3)
          } else if (planetTypeLower.includes('ice') || planetTypeLower.includes('frozen')) {
            const crack = noise(nx * 40, ny * 40, 30, 2) > 0.7 ? 0.4 : 0
            const glacier = noise(nx * 15, ny * 15, 10, 3) * 0.2
            r = Math.min(255, baseR * (1.0 - crack + glacier))
            g = Math.min(255, baseG * (1.05 - crack + glacier))
            b = Math.min(255, baseB * (1.15 - crack * 0.5 + glacier))
          } else if (planetTypeLower.includes('volcanic') || planetTypeLower.includes('lava')) {
            const hotspot = elevation > 0.72 || (elevation > 0.5 && detail > 0.7)
            if (hotspot) {
              r = 255
              g = Math.min(255, 80 + elevation * 150)
              b = Math.max(0, elevation * 50)
            } else {
              r = baseR * (0.15 + microDetail * 0.15)
              g = baseG * (0.15 + microDetail * 0.10)
              b = baseB * (0.15 + microDetail * 0.10)
            }
          } else if (planetTypeLower.includes('hive') || planetTypeLower.includes('forge') || planetTypeLower.includes('industrial')) {
            const city = noise(nx * 35, ny * 35, 20, 2) > 0.6 ? 0.5 : 0
            r = baseR * (0.4 + city)
            g = baseG * (0.4 + city * 0.7)
            b = baseB * (0.3 + city * 0.5)
          } else if (planetTypeLower.includes('death') || planetTypeLower.includes('dead')) {
            const crater = noise(nx * 50, ny * 50, 35, 2) > 0.8 ? 0.5 : 0
            r = baseR * (0.5 - crater)
            g = baseG * (0.5 - crater)
            b = baseB * (0.5 - crater)
          } else {
            // Earth-like with detailed continents
            if (elevation > 0.55) {
              const latitude = Math.abs(ny - 0.5) * 2
              if (elevation > 0.75) {
                r = baseR * (0.5 + detail * 0.3)
                g = baseG * (0.5 + detail * 0.3)
                b = baseB * (0.5 + detail * 0.3)
              } else if (latitude > 0.7) {
                r = baseR * (0.8 + microDetail * 0.2)
                g = baseG * (0.9 + microDetail * 0.1)
                b = baseB * (1.0 + microDetail * 0.1)
              } else if (latitude < 0.3 && elevation < 0.65) {
                r = baseR * (0.3 + detail * 0.2)
                g = baseG * (0.7 + detail * 0.2)
                b = baseB * (0.3 + detail * 0.1)
              } else {
                r = baseR * (0.5 + detail * 0.3)
                g = baseG * (0.7 + detail * 0.2)
                b = baseB * (0.4 + detail * 0.2)
              }
            } else {
              r = baseR * (0.15 + microDetail * 0.05)
              g = baseG * (0.3 + microDetail * 0.1)
              b = baseB * (0.8 + microDetail * 0.15)
            }
          }
          
          ctx.fillStyle = `rgb(${Math.min(255, Math.max(0, r))},${Math.min(255, Math.max(0, g))},${Math.min(255, Math.max(0, b))})`
          ctx.fillRect(x, y, 1, 1)
        }
      }
      
      const texture = new THREE.CanvasTexture(canvas)
      texture.wrapS = THREE.RepeatWrapping
      texture.wrapT = THREE.RepeatWrapping
      return texture
    }
    
    // Generate cloud texture
    const generateCloudTexture = () => {
      const canvas = document.createElement('canvas')
      canvas.width = 2048
      canvas.height = 1024
      const ctx = canvas.getContext('2d')!
      
      const noise = (x: number, y: number, scale: number, octaves: number = 1) => {
        let value = 0
        let amplitude = 1
        let frequency = scale
        
        for (let i = 0; i < octaves; i++) {
          value += Math.sin(x * frequency) * Math.cos(y * frequency) * amplitude
          amplitude *= 0.5
          frequency *= 2
        }
        
        return value * 0.5 + 0.5
      }
      
      for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
          const nx = x / canvas.width
          const ny = y / canvas.height
          
          const largeSystems = noise(nx * 4, ny * 4, 3, 3)
          const mediumClouds = noise(nx * 12, ny * 12, 8, 2)
          const smallClouds = noise(nx * 30, ny * 30, 20, 1)
          
          const cloud = largeSystems * 0.5 + mediumClouds * 0.3 + smallClouds * 0.2
          const alpha = cloud > 0.45 ? (cloud - 0.45) * 1.8 : 0
          
          ctx.fillStyle = `rgba(255, 255, 255, ${Math.min(1, alpha * 0.85)})`
          ctx.fillRect(x, y, 1, 1)
        }
      }
      
      const texture = new THREE.CanvasTexture(canvas)
      texture.wrapS = THREE.RepeatWrapping
      texture.wrapT = THREE.RepeatWrapping
      return texture
    }

    // Create main planet with procedural texture using IcosahedronGeometry
    const geometry = new THREE.IcosahedronGeometry(planet.size * 0.5, 12)
    const planetTexture = generatePlanetTexture()
    const material = new THREE.MeshPhongMaterial({
      map: planetTexture,
      shininess: shininess,
      specular: specular,
      emissive: planet.is_contested ? planet.color : planet.color,
      emissiveIntensity: emissiveIntensity,
    })
    const planetMesh = new THREE.Mesh(geometry, material)
    scene.add(planetMesh)
    
    // Add surface detail layer
    const detailGeometry = new THREE.IcosahedronGeometry(planet.size * 0.502, 8)
    const detailMaterial = new THREE.MeshPhongMaterial({
      color: planet.color,
      shininess: shininess * 0.7,
      specular: specular,
      transparent: true,
      opacity: 0.4,
    })
    const detailMesh = new THREE.Mesh(detailGeometry, detailMaterial)
    scene.add(detailMesh)

    // Add atmospheric glow using fresnel effect
    const glowGeometry = new THREE.IcosahedronGeometry(planet.size * 0.58, 12)
    const glowMaterial = new THREE.ShaderMaterial({
      uniforms: {
        color1: { value: new THREE.Color(planet.color) },
        color2: { value: new THREE.Color(0x000000) },
        fresnelBias: { value: 0.2 },
        fresnelScale: { value: 1.5 },
        fresnelPower: { value: 4.0 },
      },
      vertexShader: `
        uniform float fresnelBias;
        uniform float fresnelScale;
        uniform float fresnelPower;
        varying float vReflectionFactor;
        
        void main() {
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          vec4 worldPosition = modelMatrix * vec4(position, 1.0);
          vec3 worldNormal = normalize(mat3(modelMatrix[0].xyz, modelMatrix[1].xyz, modelMatrix[2].xyz) * normal);
          vec3 I = worldPosition.xyz - cameraPosition;
          vReflectionFactor = fresnelBias + fresnelScale * pow(1.0 + dot(normalize(I), worldNormal), fresnelPower);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform vec3 color1;
        uniform vec3 color2;
        varying float vReflectionFactor;
        
        void main() {
          float f = clamp(vReflectionFactor, 0.0, 1.0);
          gl_FragColor = vec4(mix(color2, color1, vec3(f)), f);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    scene.add(glow)
    
    // Add outer glow halo
    const haloGeometry = new THREE.IcosahedronGeometry(planet.size * 0.65, 8)
    const haloMaterial = new THREE.MeshBasicMaterial({
      color: planet.color,
      transparent: true,
      opacity: 0.15,
      side: THREE.BackSide
    })
    const halo = new THREE.Mesh(haloGeometry, haloMaterial)
    scene.add(halo)

    // Add rings for certain planet types
    if (planetTypeLower.includes('gas') || planetTypeLower.includes('ring') || 
        planetTypeLower.includes('hive') || Math.random() > 0.6) {
      const ringGeometry = new THREE.RingGeometry(planet.size * 0.65, planet.size * 0.95, 128)
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: planet.color,
        transparent: true,
        opacity: 0.5,
        side: THREE.DoubleSide,
      })
      const ring = new THREE.Mesh(ringGeometry, ringMaterial)
      ring.rotation.x = Math.PI / 2.2
      scene.add(ring)
    }
    
    // Add cloud layer for habitable planets
    let cloudMesh: THREE.Mesh | null = null
    if (planetTypeLower.includes('agri') || planetTypeLower.includes('habitable') || 
        planetTypeLower.includes('paradise') || planetTypeLower.includes('civilised') ||
        (!planetTypeLower.includes('death') && !planetTypeLower.includes('volcanic') && !planetTypeLower.includes('desert'))) {
      const cloudGeometry = new THREE.SphereGeometry(planet.size * 0.515, 64, 64)
      const cloudTexture = generateCloudTexture()
      const cloudMaterial = new THREE.MeshStandardMaterial({
        map: cloudTexture,
        transparent: true,
        opacity: 0.7,
        depthWrite: false,
      })
      cloudMesh = new THREE.Mesh(cloudGeometry, cloudMaterial)
      scene.add(cloudMesh)
    }

    // Enhanced lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
    scene.add(ambientLight)
    
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.2)
    keyLight.position.set(5, 3, 5)
    scene.add(keyLight)
    
    const fillLight = new THREE.DirectionalLight(0x6699ff, 0.4)
    fillLight.position.set(-5, 0, -3)
    scene.add(fillLight)
    
    const rimLight = new THREE.PointLight(planet.color, 0.8, 10)
    rimLight.position.set(0, 0, -4)
    scene.add(rimLight)

    // Animation
    let animationId: number
    const animate = () => {
      animationId = requestAnimationFrame(animate)
      
      // Rotate planet
      planetMesh.rotation.y += 0.003
      
      // Rotate detail layer at different speed
      detailMesh.rotation.y -= 0.002
      
      // Rotate cloud layer independently (weather systems)
      if (cloudMesh) {
        cloudMesh.rotation.y += 0.005
      }
      
      // Pulse glow for contested planets
      if (planet.is_contested) {
        const time = Date.now() * 0.001
        glow.scale.setScalar(1 + Math.sin(time * 2) * 0.05)
        halo.scale.setScalar(1 + Math.sin(time * 2) * 0.08)
      }
      
      // Rotate atmospheric effects
      glow.rotation.y -= 0.001
      halo.rotation.y += 0.0015
      
      renderer.render(scene, camera)
    }
    animate()

    // Cleanup
    return () => {
      cancelAnimationFrame(animationId)
      if (planetCanvasRef.current) {
        planetCanvasRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
      geometry.dispose()
      material.dispose()
      glowGeometry.dispose()
      glowMaterial.dispose()
    }
  }, [planet])

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#1a1a2e',
          borderRadius: '12px',
          maxWidth: '800px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          padding: '0',
          border: planet.is_contested ? '3px solid #ff4444' : `2px solid ${planet.color}`,
          boxShadow: `0 10px 40px ${planet.color}44`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            background: `linear-gradient(135deg, ${planet.color}22 0%, ${planet.color}44 100%)`,
            padding: '24px',
            borderBottom: `2px solid ${planet.color}`,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '20px' }}>
            {/* 3D Planet Preview */}
            <div
              ref={planetCanvasRef}
              style={{
                width: '200px',
                height: '200px',
                borderRadius: '50%',
                overflow: 'hidden',
                border: `2px solid ${planet.color}`,
                boxShadow: `0 0 20px ${planet.color}66`,
                flexShrink: 0
              }}
            />
            
            <div style={{ flex: 1 }}>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '28px', color: planet.color }}>
                {planet.name}
              </h2>
              <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '12px' }}>
                {planet.planet_type.toUpperCase()} WORLD - Position {planet.position}
              </div>
              <p style={{ margin: '0', fontSize: '15px', lineHeight: '1.6' }}>
                {planet.description}
              </p>
            </div>
            
            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontSize: '24px',
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                flexShrink: 0
              }}
            >
              ×
            </button>
          </div>

          {/* Planet Stats */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '12px',
              marginTop: '20px',
            }}
          >
            <div
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                padding: '12px',
                borderRadius: '8px',
              }}
            >
              <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '4px' }}>
                Strategic Value
              </div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                {planet.strategic_value}
              </div>
            </div>
            <div
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                padding: '12px',
                borderRadius: '8px',
              }}
            >
              <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '4px' }}>
                Battles Fought
              </div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                {planet.games_played}
              </div>
            </div>
            {planet.current_controller && (
              <div
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.3)',
                  padding: '12px',
                  borderRadius: '8px',
                }}
              >
                <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '4px' }}>
                  Controller
                </div>
                <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                  {planet.current_controller}
                </div>
              </div>
            )}
            {planet.is_contested && (
              <div
                style={{
                  backgroundColor: 'rgba(255, 68, 68, 0.2)',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #ff4444',
                }}
              >
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#ff4444' }}>
                  ⚔️ CONTESTED
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Battle History */}
        <div style={{ padding: '24px' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>Battle History</h3>

          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px', opacity: 0.7 }}>
              Loading battles...
            </div>
          ) : !games || games.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px',
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '8px',
                opacity: 0.7,
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>🌌</div>
              <div>No battles have been fought on this world... yet.</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {games.map((game) => (
                <div
                  key={game.id}
                  style={{
                    backgroundColor: 'rgba(0, 0, 0, 0.3)',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'start',
                      marginBottom: '12px',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '12px', opacity: 0.6, marginBottom: '4px' }}>
                        {new Date(game.played_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </div>
                      <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '8px' }}>
                        {game.mission_type.toUpperCase()} MISSION
                      </div>
                    </div>
                    <div
                      style={{
                        backgroundColor: game.winner_id === game.attacker_id
                          ? 'rgba(76, 175, 80, 0.2)'
                          : 'rgba(244, 67, 54, 0.2)',
                        color: game.winner_id === game.attacker_id ? '#4caf50' : '#f44336',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        border: `1px solid ${
                          game.winner_id === game.attacker_id ? '#4caf50' : '#f44336'
                        }`,
                      }}
                    >
                      {game.winner_name ? `${game.winner_name} Victorious` : 'Draw'}
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px' }}>
                    {/* Attacker */}
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: '12px',
                          opacity: 0.6,
                          marginBottom: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        <span>⚔️</span>
                        <span>ATTACKER</span>
                      </div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>
                        {game.attacker_name}
                      </div>
                      <div style={{ fontSize: '14px', opacity: 0.8 }}>
                        Score: {game.attacker_score} | RP: +{game.attacker_req}
                      </div>
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        fontSize: '20px',
                        opacity: 0.5,
                      }}
                    >
                      VS
                    </div>

                    {/* Defender */}
                    <div style={{ flex: 1, textAlign: 'right' }}>
                      <div
                        style={{
                          fontSize: '12px',
                          opacity: 0.6,
                          marginBottom: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-end',
                          gap: '4px',
                        }}
                      >
                        <span>DEFENDER</span>
                        <span>🛡️</span>
                      </div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>
                        {game.defender_name}
                      </div>
                      <div style={{ fontSize: '14px', opacity: 0.8 }}>
                        Score: {game.defender_score} | RP: +{game.defender_req}
                      </div>
                    </div>
                  </div>

                  {game.notes && (
                    <div
                      style={{
                        marginTop: '12px',
                        padding: '12px',
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontStyle: 'italic',
                        opacity: 0.8,
                        borderLeft: '3px solid rgba(255, 255, 255, 0.2)',
                      }}
                    >
                      {game.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PlanetDetailModal
