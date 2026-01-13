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

const CampaignSolarSystem: React.FC<CampaignSolarSystemProps> = ({ planets, onPlanetClick }) => {
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
    scene.background = new THREE.Color(0x000000)
    sceneRef.current = scene
    
    // Add deep space background gradient
    const vertexShader = `
      varying vec3 vWorldPosition;
      void main() {
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `
    
    const fragmentShader = `
      varying vec3 vWorldPosition;
      void main() {
        vec3 color1 = vec3(0.0, 0.02, 0.1);  // Deep blue
        vec3 color2 = vec3(0.05, 0.0, 0.15); // Purple
        vec3 color3 = vec3(0.0, 0.0, 0.02);  // Almost black
        
        float h = normalize(vWorldPosition).y;
        vec3 color = mix(color3, mix(color1, color2, h * 0.5 + 0.5), smoothstep(-1.0, 1.0, h));
        gl_FragColor = vec4(color, 1.0);
      }
    `
    
    const skyGeo = new THREE.SphereGeometry(500, 32, 32)
    const skyMat = new THREE.ShaderMaterial({
      vertexShader: vertexShader,
      fragmentShader: fragmentShader,
      side: THREE.BackSide
    })
    const sky = new THREE.Mesh(skyGeo, skyMat)
    scene.add(sky)

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
    const renderer = new THREE.WebGLRenderer({ 
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.2
    containerRef.current.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Create realistic starfield with texture and colors
    const createStarTexture = () => {
      const canvas = document.createElement('canvas')
      canvas.width = 32
      canvas.height = 32
      const ctx = canvas.getContext('2d')!
      
      const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16)
      gradient.addColorStop(0, 'rgba(255,255,255,1)')
      gradient.addColorStop(0.2, 'rgba(255,255,255,0.8)')
      gradient.addColorStop(0.4, 'rgba(255,255,255,0.4)')
      gradient.addColorStop(1, 'rgba(255,255,255,0)')
      
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, 32, 32)
      
      return new THREE.CanvasTexture(canvas)
    }
    
    const starTexture = createStarTexture()
    
    // Add multiple layers of stars with varying sizes and distances
    const createStarField = (count: number, size: number, minRadius: number, maxRadius: number, colors: boolean = true) => {
      const starGeometry = new THREE.BufferGeometry()
      const starVertices = []
      const starColors = []
      const starSizes = []
      
      for (let i = 0; i < count; i++) {
        const radius = minRadius + Math.random() * (maxRadius - minRadius)
        const theta = Math.random() * Math.PI * 2
        const phi = Math.acos(2 * Math.random() - 1)
        
        const x = radius * Math.sin(phi) * Math.cos(theta)
        const y = radius * Math.sin(phi) * Math.sin(theta)
        const z = radius * Math.cos(phi)
        
        starVertices.push(x, y, z)
        
        // More realistic star colors
        const color = new THREE.Color()
        if (colors) {
          const rand = Math.random()
          if (rand < 0.6) {
            // White/blue stars (most common)
            color.setHSL(0.6, 0.15, 0.85 + Math.random() * 0.15)
          } else if (rand < 0.85) {
            // Yellow/white stars
            color.setHSL(0.15, 0.3, 0.9 + Math.random() * 0.1)
          } else {
            // Red/orange stars
            color.setHSL(0.05, 0.8, 0.7 + Math.random() * 0.2)
          }
        } else {
          color.setRGB(1, 1, 1)
        }
        starColors.push(color.r, color.g, color.b)
        
        // Vary star sizes
        starSizes.push(size * (0.5 + Math.random() * 1.5))
      }
      
      starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3))
      starGeometry.setAttribute('color', new THREE.Float32BufferAttribute(starColors, 3))
      starGeometry.setAttribute('size', new THREE.Float32BufferAttribute(starSizes, 1))
      
      const starMaterial = new THREE.PointsMaterial({
        size: size,
        map: starTexture,
        vertexColors: true,
        transparent: true,
        alphaTest: 0.5,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true
      })
      
      return new THREE.Points(starGeometry, starMaterial)
    }
    
    // Create multiple star layers for depth
    const distantStars = createStarField(2000, 0.2, 80, 120, true)
    scene.add(distantStars)
    
    const midStars = createStarField(1200, 0.35, 50, 80, true)
    scene.add(midStars)
    
    const closeStars = createStarField(600, 0.5, 30, 50, true)
    scene.add(closeStars)
    
    // Add subtle distant galaxies/nebula glow (very faint)
    const createDistantNebula = () => {
      const nebulaGeometry = new THREE.BufferGeometry()
      const nebulaVertices = []
      const nebulaColors = []
      
      for (let i = 0; i < 50; i++) {
        const radius = 90 + Math.random() * 30
        const theta = Math.random() * Math.PI * 2
        const phi = Math.acos(2 * Math.random() - 1)
        
        const x = radius * Math.sin(phi) * Math.cos(theta)
        const y = radius * Math.sin(phi) * Math.sin(theta)
        const z = radius * Math.cos(phi)
        
        nebulaVertices.push(x, y, z)
        
        // Very subtle purple/blue tint
        const color = new THREE.Color()
        color.setHSL(0.65 + Math.random() * 0.1, 0.3, 0.15)
        nebulaColors.push(color.r, color.g, color.b)
      }
      
      nebulaGeometry.setAttribute('position', new THREE.Float32BufferAttribute(nebulaVertices, 3))
      nebulaGeometry.setAttribute('color', new THREE.Float32BufferAttribute(nebulaColors, 3))
      
      const nebulaMaterial = new THREE.PointsMaterial({
        size: 3,
        vertexColors: true,
        transparent: true,
        opacity: 0.05,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      })
      
      return new THREE.Points(nebulaGeometry, nebulaMaterial)
    }
    
    const nebula = createDistantNebula()
    scene.add(nebula)
    
    // Add space dust/gas particles
    const dustGeometry = new THREE.BufferGeometry()
    const dustVertices = []
    const dustColors = []
    for (let i = 0; i < 800; i++) {
      const radius = 35 + Math.random() * 25
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      
      const x = radius * Math.sin(phi) * Math.cos(theta)
      const y = radius * Math.sin(phi) * Math.sin(theta)
      const z = radius * Math.cos(phi)
      
      dustVertices.push(x, y, z)
      
      const brightness = 0.3 + Math.random() * 0.3
      dustColors.push(brightness, brightness * 0.9, brightness * 0.95)
    }
    dustGeometry.setAttribute('position', new THREE.Float32BufferAttribute(dustVertices, 3))
    dustGeometry.setAttribute('color', new THREE.Float32BufferAttribute(dustColors, 3))
    const dustMaterial = new THREE.PointsMaterial({
      size: 0.15,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.NormalBlending
    })
    const dust = new THREE.Points(dustGeometry, dustMaterial)
    scene.add(dust)

    // Add sun (central star) with IcosahedronGeometry for smoother look
    const sunGeometry = new THREE.IcosahedronGeometry(2, 16)
    const sunMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xffff99, 
      emissive: 0xffff99, 
      emissiveIntensity: 2.0,
      roughness: 1.0,
      metalness: 0.0
    })
    const sun = new THREE.Mesh(sunGeometry, sunMaterial)
    scene.add(sun)
    
    // Add fresnel-based glow layers for realistic sun atmosphere
    const createSunGlow = (scale: number, color1: string, color2: string) => {
      const uniforms = {
        color1: { value: new THREE.Color(color1) },
        color2: { value: new THREE.Color(color2) },
        fresnelBias: { value: 0.2 },
        fresnelScale: { value: 1.5 },
        fresnelPower: { value: 4.0 },
      }
      
      const vertexShader = `
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
      `
      
      const fragmentShader = `
        uniform vec3 color1;
        uniform vec3 color2;
        varying float vReflectionFactor;
        
        void main() {
          float f = clamp(vReflectionFactor, 0.0, 1.0);
          gl_FragColor = vec4(mix(color2, color1, vec3(f)), f);
        }
      `
      
      const material = new THREE.ShaderMaterial({
        uniforms,
        vertexShader,
        fragmentShader,
        transparent: true,
        blending: THREE.AdditiveBlending,
      })
      
      const geometry = new THREE.IcosahedronGeometry(2, 16)
      const mesh = new THREE.Mesh(geometry, material)
      mesh.scale.setScalar(scale)
      return mesh
    }
    
    const glow1 = createSunGlow(1.15, '#ffff99', '#000000')
    scene.add(glow1)
    
    // Removed glow2 for performance

    // Add sun corona effect
    const coronaGeometry = new THREE.IcosahedronGeometry(2.8, 16)
    const coronaMaterial = new THREE.ShaderMaterial({
      uniforms: {
        c: { value: 0.2 },
        p: { value: 4.0 },
      },
      vertexShader: `
        varying vec3 vNormal;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float c;
        uniform float p;
        varying vec3 vNormal;
        void main() {
          float intensity = pow(c - dot(vNormal, vec3(0.0, 0.0, 1.0)), p);
          gl_FragColor = vec4(1.0, 0.6, 0.0, 1.0) * intensity;
        }
      `,
      side: THREE.BackSide,
      blending: THREE.AdditiveBlending,
      transparent: true,
    })
    const corona = new THREE.Mesh(coronaGeometry, coronaMaterial)
    scene.add(corona)

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 1.5)
    scene.add(ambientLight)

    // Add point light at sun
    const pointLight = new THREE.PointLight(0xffaa00, 3, 150)
    pointLight.castShadow = true
    scene.add(pointLight)
    
    // Add rim light for better planet definition
    const rimLight = new THREE.DirectionalLight(0x6699ff, 0.5)
    rimLight.position.set(-10, 5, -10)
    scene.add(rimLight)

    // Helper function to generate procedural planet texture
    const generatePlanetTexture = (planet: Planet) => {
      const canvas = document.createElement('canvas')
      canvas.width = 1024
      canvas.height = 512
      const ctx = canvas.getContext('2d')!
      
      const planetTypeLower = planet.planet_type.toLowerCase()
      
      // Improved Perlin-like noise function with multiple octaves
      const noise = (x: number, y: number, scale: number) => {
        return Math.sin(x * scale) * Math.cos(y * scale) * 0.5 + 0.5
      }
      
      // Multi-octave noise for better detail
      const fbm = (x: number, y: number, octaves: number = 4) => {
        let value = 0
        let amplitude = 0.5
        let frequency = 1
        for (let i = 0; i < octaves; i++) {
          value += noise(x * frequency, y * frequency, 3.14159) * amplitude
          frequency *= 2.1
          amplitude *= 0.5
        }
        return value
      }
      
      // Create base terrain
      for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
          const nx = x / canvas.width
          const ny = y / canvas.height
          
          let r, g, b
          const baseColor = parseInt(planet.color.slice(1), 16)
          const baseR = (baseColor >> 16) & 255
          const baseG = (baseColor >> 8) & 255
          const baseB = baseColor & 255
          
          // Generate terrain based on planet type with improved noise
          const elevation = fbm(nx * 4, ny * 4, 5)
          const detail = fbm(nx * 20, ny * 20, 3) * 0.3
          
          if (planetTypeLower.includes('ocean') || planetTypeLower.includes('water')) {
            // Ocean world with islands
            if (elevation > 0.55) {
              // Land masses
              const landColor = elevation * 0.3 + detail
              r = Math.min(255, baseR * (0.6 + landColor))
              g = Math.min(255, baseG * (0.8 + landColor))
              b = Math.min(255, baseB * (0.5 + landColor))
            } else if (elevation > 0.5) {
              // Shallow water / beaches
              r = baseR * 0.7
              g = baseG * 0.8
              b = baseB * 1.1
            } else {
              // Deep ocean with depth variation
              const depth = (0.5 - elevation) * 2
              r = baseR * (0.2 + depth * 0.1)
              g = baseG * (0.3 + depth * 0.2)
              b = baseB * (1.0 + depth * 0.3)
            }
          } else if (planetTypeLower.includes('desert') || planetTypeLower.includes('arid')) {
            // Desert with dunes and variation
            const dune = fbm(nx * 15, ny * 15, 4) * 0.4
            r = Math.min(255, baseR * (0.7 + dune))
            g = Math.min(255, baseG * (0.6 + dune))
            b = Math.min(255, baseB * (0.4 + dune * 0.5))
          } else if (planetTypeLower.includes('ice') || planetTypeLower.includes('frozen')) {
            // Ice caps with cracks and variation
            const crack = fbm(nx * 25, ny * 25, 4) * 0.3
            const ice = elevation * 0.2
            r = Math.min(255, baseR * (1.0 + ice - crack))
            g = Math.min(255, baseG * (1.0 + ice - crack * 0.8))
            b = Math.min(255, baseB * (1.1 + ice - crack * 0.5))
          } else if (planetTypeLower.includes('volcanic') || planetTypeLower.includes('lava')) {
            // Volcanic with lava flows
            if (elevation > 0.65) {
              // Lava
              const heat = (elevation - 0.65) * 3
              r = 255
              g = Math.min(255, 60 + heat * 150)
              b = Math.max(0, heat * 50)
            } else {
              // Dark rock
              const rock = detail * 0.3
              r = Math.min(255, baseR * (0.15 + rock))
              g = Math.min(255, baseG * (0.1 + rock))
              b = Math.min(255, baseB * (0.1 + rock))
            }
          } else if (planetTypeLower.includes('forge') || planetTypeLower.includes('industrial')) {
            // Industrial/forge world with structures
            const structure = fbm(nx * 30, ny * 30, 3)
            if (structure > 0.6) {
              // Metallic structures
              r = Math.min(255, baseR * 0.8)
              g = Math.min(255, baseG * 0.8)
              b = Math.min(255, baseB * 0.8)
            } else {
              // Polluted ground
              r = Math.min(255, baseR * (0.3 + elevation * 0.3))
              g = Math.min(255, baseG * (0.25 + elevation * 0.2))
              b = Math.min(255, baseB * (0.2 + elevation * 0.15))
            }
          } else {
            // Earth-like with continents and oceans
            if (elevation > 0.52) {
              // Land with varied terrain
              const terrain = detail * 0.5
              const heightVariation = (elevation - 0.52) * 2
              r = Math.min(255, baseR * (0.5 + terrain + heightVariation * 0.3))
              g = Math.min(255, baseG * (0.7 + terrain + heightVariation * 0.4))
              b = Math.min(255, baseB * (0.3 + terrain * 0.5))
            } else if (elevation > 0.48) {
              // Coastal areas
              r = baseR * 0.6
              g = baseG * 0.7
              b = baseB * 0.8
            } else {
              // Water with depth
              const depth = (0.48 - elevation) * 3
              r = Math.min(255, baseR * (0.1 + depth * 0.1))
              g = Math.min(255, baseG * (0.3 + depth * 0.2))
              b = Math.min(255, baseB * (0.8 + depth * 0.3))
            }
          }
          
          ctx.fillStyle = `rgb(${r},${g},${b})`
          ctx.fillRect(x, y, 1, 1)
        }
      }
      
      return new THREE.CanvasTexture(canvas)
    }

    // Helper function to generate cloud texture
    const generateCloudTexture = () => {
      const canvas = document.createElement('canvas')
      canvas.width = 1024
      canvas.height = 512
      const ctx = canvas.getContext('2d')!
      
      const noise = (x: number, y: number, scale: number) => {
        return Math.sin(x * scale) * Math.cos(y * scale) * 0.5 + 0.5
      }
      
      // Multi-octave noise for realistic clouds
      const fbm = (x: number, y: number, octaves: number = 4) => {
        let value = 0
        let amplitude = 0.5
        let frequency = 1
        for (let i = 0; i < octaves; i++) {
          value += noise(x * frequency, y * frequency, 3.14159) * amplitude
          frequency *= 2.1
          amplitude *= 0.5
        }
        return value
      }
      
      for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
          const nx = x / canvas.width
          const ny = y / canvas.height
          
          const cloud = fbm(nx * 6, ny * 6, 5)
          const detail = fbm(nx * 15, ny * 15, 3) * 0.3
          const alpha = cloud > 0.45 ? (cloud - 0.45) * 1.8 + detail : 0
          
          ctx.fillStyle = `rgba(255, 255, 255, ${Math.min(1, alpha * 0.7)})`
          ctx.fillRect(x, y, 1, 1)
        }
      }
      
      return new THREE.CanvasTexture(canvas)
    }

    // Create planets for each planet in the campaign
    const planetMeshes: PlanetMesh[] = []

    planets.forEach((planet) => {
      const distance = 8 + (planet.position - 1) * 4
      const size = Math.min(planet.size, 2)
      const color = planet.color

      // Create planet mesh with IcosahedronGeometry for smoother appearance
      const planetGeometry = new THREE.IcosahedronGeometry(size, 20)
      
      // Create varied materials based on planet type
      let shininess = 5
      let specular = 0x333333
      let bumpScale = 0.02
      
      if (planet.planet_type.toLowerCase().includes('ice') || planet.planet_type.toLowerCase().includes('frozen')) {
        shininess = 50
        specular = 0xcccccc
        bumpScale = 0.01
      } else if (planet.planet_type.toLowerCase().includes('desert') || planet.planet_type.toLowerCase().includes('arid')) {
        shininess = 3
        specular = 0x111111
        bumpScale = 0.03
      } else if (planet.planet_type.toLowerCase().includes('ocean') || planet.planet_type.toLowerCase().includes('water')) {
        shininess = 60
        specular = 0xffffff
        bumpScale = 0.005
      } else if (planet.planet_type.toLowerCase().includes('forge') || planet.planet_type.toLowerCase().includes('industrial')) {
        shininess = 30
        specular = 0x999999
        bumpScale = 0.015
      } else if (planet.planet_type.toLowerCase().includes('volcanic') || planet.planet_type.toLowerCase().includes('lava')) {
        shininess = 15
        specular = 0xff4400
        bumpScale = 0.04
      }
      
      // Generate procedural surface texture
      const planetTexture = generatePlanetTexture(planet)
      planetTexture.anisotropy = renderer.capabilities.getMaxAnisotropy()
      
      const planetMaterial = new THREE.MeshPhongMaterial({
        map: planetTexture,
        shininess: shininess,
        specular: specular,
        bumpMap: planetTexture,
        bumpScale: bumpScale,
        emissive: planet.is_contested ? color : 0x000000,
        emissiveIntensity: planet.is_contested ? 0.4 : 0.05,
      })
      
      const planetMesh = new THREE.Mesh(planetGeometry, planetMaterial)
      
      // Add weather systems (clouds) for habitable planets
      const planetTypeLower = planet.planet_type.toLowerCase()
      if (!planetTypeLower.includes('death') && 
          !planetTypeLower.includes('dead') &&
          !planetTypeLower.includes('volcanic') &&
          !planetTypeLower.includes('gas')) {
        
        const cloudTexture = generateCloudTexture()
        cloudTexture.wrapS = THREE.RepeatWrapping
        cloudTexture.wrapT = THREE.RepeatWrapping
        
        const cloudGeometry = new THREE.SphereGeometry(size * 1.01, 32, 32)
        const cloudMaterial = new THREE.MeshStandardMaterial({
          map: cloudTexture,
          transparent: true,
          opacity: 0.8,
          depthWrite: false,
        })
        const cloudMesh = new THREE.Mesh(cloudGeometry, cloudMaterial)
        planetMesh.add(cloudMesh)
        
        // Store cloud mesh for animation
        ;(planetMesh as any).cloudLayer = cloudMesh
      }
      
      // Add bump/displacement effect simulation using multiple layers
      const detailGeometry = new THREE.SphereGeometry(size * 1.002, 32, 32)
      const detailMaterial = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.8,
        metalness: 0.2,
        transparent: true,
        opacity: 0.3,
      })
      const detailMesh = new THREE.Mesh(detailGeometry, detailMaterial)
      planetMesh.add(detailMesh)
      
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

      // Add atmospheric glow using fresnel effect
      const glowGeometry = new THREE.IcosahedronGeometry(size, 16)
      const glowMaterial = new THREE.ShaderMaterial({
        uniforms: {
          color1: { value: new THREE.Color(color) },
          color2: { value: new THREE.Color(0x000000) },
          fresnelBias: { value: 0.1 },
          fresnelScale: { value: 2.0 },
          fresnelPower: { value: 3.0 },
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
      const planetGlow = new THREE.Mesh(glowGeometry, glowMaterial)
      planetGlow.scale.setScalar(1.1)
      planetMesh.add(planetGlow)

      // Add rings for gas giants or special planets
      if (planet.planet_type.toLowerCase().includes('gas') || 
          planet.planet_type.toLowerCase().includes('ring') ||
          Math.random() > 0.7) {
        const ringGeometry = new THREE.RingGeometry(size * 1.3, size * 1.8, 64)
        const ringMaterial = new THREE.MeshBasicMaterial({
          color: color,
          transparent: true,
          opacity: 0.4,
          side: THREE.DoubleSide,
        })
        const ring = new THREE.Mesh(ringGeometry, ringMaterial)
        ring.rotation.x = Math.PI / 2 + (Math.random() - 0.5) * 0.3
        planetMesh.add(ring)
      }

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

      // Rotate sun glow layers at different speeds
      glow1.rotation.y += 0.002
      corona.rotation.y += 0.0015
      sun.rotation.y += 0.001

      // Subtle star twinkle effect
      const time = Date.now() * 0.001
      if (distantStars.material instanceof THREE.PointsMaterial) {
        distantStars.material.opacity = 0.7 + Math.sin(time * 0.5) * 0.1
      }
      if (midStars.material instanceof THREE.PointsMaterial) {
        midStars.material.opacity = 0.8 + Math.sin(time * 0.7) * 0.1
      }
      if (closeStars.material instanceof THREE.PointsMaterial) {
        closeStars.material.opacity = 0.9 + Math.sin(time) * 0.1
      }
      
      // Slowly rotate nebula
      nebula.rotation.y += 0.00005
      nebula.rotation.x += 0.00003
      
      // Drift space dust
      dust.rotation.y -= 0.0001
      dust.rotation.x += 0.00005

      // Update planets
      planetMeshes.forEach((planetMesh) => {
        planetMesh.angle += planetMesh.speed
        planetMesh.mesh.position.x = Math.cos(planetMesh.angle) * planetMesh.distance
        planetMesh.mesh.position.z = Math.sin(planetMesh.angle) * planetMesh.distance
        planetMesh.mesh.rotation.y += 0.008
        
        // Rotate cloud layer independently (weather systems moving)
        if ((planetMesh.mesh as any).cloudLayer) {
          (planetMesh.mesh as any).cloudLayer.rotation.y += 0.012
        }
        
        // Rotate detail layer at different speed
        if (planetMesh.mesh.children.length > 0) {
          planetMesh.mesh.children.forEach((child, index) => {
            if (child instanceof THREE.Mesh && child !== (planetMesh.mesh as any).cloudLayer) {
              child.rotation.y -= 0.005 * (index + 1)
            }
          })
        }

        // Position label above planet
        planetMesh.label.position.copy(planetMesh.mesh.position)
        planetMesh.label.position.y = planetMesh.mesh.position.y + 2.5
      })

      // Gentle camera rotation
      const cameraTime = Date.now() * 0.00008
      camera.position.x = Math.cos(cameraTime) * 32
      camera.position.z = Math.sin(cameraTime) * 32
      camera.position.y = 20 + Math.sin(cameraTime * 0.5) * 3
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
