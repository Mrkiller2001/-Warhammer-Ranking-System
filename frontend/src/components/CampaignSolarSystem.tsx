import React, { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import type { Planet } from '@/types/api'

interface CampaignSolarSystemProps {
  campaignId: number
  planets: Planet[]
  onPlanetClick?: (planet: Planet) => void
}

interface PlanetMesh {
  mesh: THREE.Mesh
  orbit: THREE.Line
  angle: number
  speed: number
  distance: number
  planet: Planet
  label: THREE.Sprite
}

const CampaignSolarSystem: React.FC<CampaignSolarSystemProps> = ({ campaignId, planets, onPlanetClick }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const planetsRef = useRef<PlanetMesh[]>([])
  const animationFrameRef = useRef<number>()
  const [hoveredPlanet, setHoveredPlanet] = useState<Planet | null>(null)

  useEffect(() => {
    if (!containerRef.current || planets.length === 0) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x000510)
    sceneRef.current = scene

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      60,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    )
    camera.position.set(0, 20, 30)
    camera.lookAt(0, 0, 0)
    cameraRef.current = camera

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Add stars
    const starGeometry = new THREE.BufferGeometry()
    const starVertices = []
    for (let i = 0; i < 1000; i++) {
      const x = (Math.random() - 0.5) * 200
      const y = (Math.random() - 0.5) * 200
      const z = (Math.random() - 0.5) * 200
      starVertices.push(x, y, z)
    }
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3))
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.5 })
    const stars = new THREE.Points(starGeometry, starMaterial)
    scene.add(stars)

    // Add sun (central star) representing the campaign system
    const sunGeometry = new THREE.SphereGeometry(2, 32, 32)
    const sunMaterial = new THREE.MeshStandardMaterial({ color: 0xffaa00, emissive: 0xffaa00, emissiveIntensity: 1 })
    const sun = new THREE.Mesh(sunGeometry, sunMaterial)
    scene.add(sun)

    // Add sun glow
    const glowGeometry = new THREE.SphereGeometry(2.5, 32, 32)
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xffaa00,
      transparent: true,
      opacity: 0.3
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    scene.add(glow)

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 2)
    scene.add(ambientLight)

    // Add point light at sun
    const pointLight = new THREE.PointLight(0xffaa00, 2, 100)
    scene.add(pointLight)

    // Create planets for each planet in the campaign
    const planetMeshes: PlanetMesh[] = []

    planets.forEach((planet) => {
      const distance = 8 + (planet.position - 1) * 4
      const size = planet.size
      const color = planet.color

      // Create planet mesh
      const planetGeometry = new THREE.SphereGeometry(Math.min(size, 2), 32, 32)
      const planetMaterial = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.7,
        metalness: 0.3,
        emissive: planet.is_contested ? color : 0x000000,
        emissiveIntensity: planet.is_contested ? 0.3 : 0
      })
      const planetMesh = new THREE.Mesh(planetGeometry, planetMaterial)
      
      // Create orbit path
      const orbitGeometry = new THREE.BufferGeometry()
      const orbitPoints = []
      for (let i = 0; i <= 64; i++) {
        const angle = (i / 64) * Math.PI * 2
        orbitPoints.push(
          Math.cos(angle) * distance,
          0,
          Math.sin(angle) * distance
        )
      }
      orbitGeometry.setAttribute('position', new THREE.Float32BufferAttribute(orbitPoints, 3))
      const orbitMaterial = new THREE.LineBasicMaterial({ color: 0x444444, opacity: 0.3, transparent: true })
      const orbit = new THREE.Line(orbitGeometry, orbitMaterial)
      scene.add(orbit)

      // Create label
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')!
      canvas.width = 512
      canvas.height = 128
      context.fillStyle = '#ffffff'
      context.font = 'Bold 32px Arial'
      context.textAlign = 'center'
      context.fillText(planet.name, 256, 48)
      
      // Add games played indicator if any
      if (planet.games_played > 0) {
        context.fillStyle = planet.is_contested ? '#ff0000' : '#00ff00'
        context.font = '24px Arial'
        context.fillText(`${planet.games_played} battles`, 256, 88)
      }

      const texture = new THREE.CanvasTexture(canvas)
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true })
      const label = new THREE.Sprite(spriteMaterial)
      label.scale.set(8, 2, 1)
      
      scene.add(planetMesh)
      scene.add(label)

      planetMeshes.push({
        mesh: planetMesh,
        orbit,
        angle: (planet.position / planets.length) * Math.PI * 2,
        speed: 0.001 + Math.random() * 0.002,
        distance,
        planet,
        label
      })
    })

    planetsRef.current = planetMeshes

    // Handle mouse interaction
    const raycaster = new THREE.Raycaster()
    const mouse = new THREE.Vector2()

    const onMouseMove = (event: MouseEvent) => {
      if (!containerRef.current) return
      
      const rect = containerRef.current.getBoundingClientRect()
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(mouse, camera)
      const intersects = raycaster.intersectObjects(planetMeshes.map(p => p.mesh))

      if (intersects.length > 0) {
        const planetMesh = planetMeshes.find(p => p.mesh === intersects[0].object)
        if (planetMesh) {
          setHoveredPlanet(planetMesh.planet)
          containerRef.current.style.cursor = 'pointer'
        }
      } else {
        setHoveredPlanet(null)
        containerRef.current.style.cursor = 'default'
      }
    }

    const onClick = (event: MouseEvent) => {
      if (!containerRef.current) return
      
      const rect = containerRef.current.getBoundingClientRect()
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(mouse, camera)
      const intersects = raycaster.intersectObjects(planetMeshes.map(p => p.mesh))

      if (intersects.length > 0) {
        const planetMesh = planetMeshes.find(p => p.mesh === intersects[0].object)
        if (planetMesh && onPlanetClick) {
          onPlanetClick(planetMesh.planet)
        }
      }
    }

    renderer.domElement.addEventListener('mousemove', onMouseMove)
    renderer.domElement.addEventListener('click', onClick)

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate)

      // Rotate sun glow
      glow.rotation.y += 0.001

      // Update planets
      planetMeshes.forEach((planetMesh) => {
        planetMesh.angle += planetMesh.speed
        planetMesh.mesh.position.x = Math.cos(planetMesh.angle) * planetMesh.distance
        planetMesh.mesh.position.z = Math.sin(planetMesh.angle) * planetMesh.distance
        planetMesh.mesh.rotation.y += 0.01

        // Position label above planet
        planetMesh.label.position.copy(planetMesh.mesh.position)
        planetMesh.label.position.y = planetMesh.mesh.position.y + 2
      })

      // Gentle camera rotation
      const time = Date.now() * 0.0001
      camera.position.x = Math.cos(time) * 30
      camera.position.z = Math.sin(time) * 30
      camera.lookAt(0, 0, 0)

      renderer.render(scene, camera)
    }

    animate()

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current) return
      
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      renderer.domElement.removeEventListener('mousemove', onMouseMove)
      renderer.domElement.removeEventListener('click', onClick)
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement)
      }
      
      renderer.dispose()
    }
  }, [planets, onPlanetClick])

  return (
    <div style={{ position: 'relative' }}>
      <div 
        ref={containerRef} 
        style={{ 
          width: '100%', 
          height: '600px',
          borderRadius: '8px',
          overflow: 'hidden'
        }} 
      />
      {hoveredPlanet && (
        <div
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            color: 'white',
            padding: '16px',
            borderRadius: '8px',
            maxWidth: '350px',
            pointerEvents: 'none',
            border: hoveredPlanet.is_contested ? '2px solid #ff0000' : '1px solid #333'
          }}
        >
          <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', color: hoveredPlanet.color }}>
            {hoveredPlanet.name}
          </h3>
          <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '8px' }}>
            {hoveredPlanet.planet_type.toUpperCase()} WORLD
          </div>
          <p style={{ margin: '0 0 8px 0', fontSize: '13px' }}>
            {hoveredPlanet.description}
          </p>
          <div style={{ fontSize: '12px', opacity: 0.8, borderTop: '1px solid #444', paddingTop: '8px' }}>
            <div><strong>Strategic Value:</strong> {hoveredPlanet.strategic_value}</div>
            <div><strong>Battles Fought:</strong> {hoveredPlanet.games_played}</div>
            {hoveredPlanet.current_controller && (
              <div><strong>Controlled By:</strong> {hoveredPlanet.current_controller}</div>
            )}
            {hoveredPlanet.is_contested && (
              <div style={{ color: '#ff4444', fontWeight: 'bold', marginTop: '4px' }}>
                ⚔️ CONTESTED
              </div>
            )}
          </div>
        </div>
      )}
      <div
        style={{
          position: 'absolute',
          bottom: '10px',
          left: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '8px 12px',
          borderRadius: '8px',
          fontSize: '12px'
        }}
      >
        <strong>{planets.length}</strong> Planet{planets.length !== 1 ? 's' : ''} in System
      </div>
    </div>
  )
}

export default CampaignSolarSystem
