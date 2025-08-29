# 🏆 Agregar Badges de Certificaciones - CV Martín Iribarne

## 📋 Información sobre Badges de Certificaciones

Basándome en tu solicitud de incluir las fotos de certificaciones vigentes con enlaces a Credly y LinkedIn, aquí tienes la información para agregar los badges:

## 🎯 **Certificaciones Vigentes con Enlaces**

### 1. **CEH (Certified Ethical Hacker)**
```html
<div class="cert-badge-container">
    <img src="https://images.credly.com/size/340x340/images/ec81134d-e80b-4eb5-ae07-0eb8e1a60fcd/ec-council-ceh-v12.png" alt="CEH Badge" class="cert-badge-img">
    <a href="[TU_ENLACE_CREDLY_CEH]">Ver en Credly</a>
    <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/">Ver en LinkedIn</a>
</div>
```

### 2. **CCNA (Cisco Certified Network Associate)**
```html
<div class="cert-badge-container">
    <img src="https://images.credly.com/size/340x340/images/683783d8-eaac-4c37-a14d-11bd8a6e9555/ccna_600.png" alt="CCNA Badge" class="cert-badge-img">
    <a href="[TU_ENLACE_CREDLY_CCNA]">Ver en Credly</a>
    <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/">Ver en LinkedIn</a>
</div>
```

### 3. **Azure AZ-900 Fundamentals**
```html
<div class="cert-badge-container">
    <img src="https://images.credly.com/size/340x340/images/be8fcaeb-c769-4858-b567-ffaaa73ce8cf/image.png" alt="Azure AZ-900 Badge" class="cert-badge-img">
    <a href="[TU_ENLACE_CREDLY_AZURE]">Ver en Credly</a>
    <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/">Ver en LinkedIn</a>
</div>
```

### 4. **AWS Cloud Practitioner**
```html
<div class="cert-badge-container">
    <img src="https://images.credly.com/size/340x340/images/00634f82-b07f-4bbd-a6bb-53de397fc3a6/image.png" alt="AWS Cloud Practitioner Badge" class="cert-badge-img">
    <a href="[TU_ENLACE_CREDLY_AWS]">Ver en Credly</a>
    <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/">Ver en LinkedIn</a>
</div>
```

### 5. **ISA/IEC 62443 Industrial Cybersecurity**
```html
<div class="cert-badge-container">
    <img src="https://images.credly.com/size/340x340/images/f8c5b2b7-7e62-46a0-b906-8dc59ef68418/ISA_62443_Digital_Badge.png" alt="ISA 62443 Badge" class="cert-badge-img">
    <a href="[TU_ENLACE_CREDLY_ISA]">Ver en Credly</a>
    <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/">Ver en LinkedIn</a>
</div>
```

## 🎨 **CSS para los Badges**

```css
.cert-badge-container {
    display: inline-block;
    margin: 10px;
    text-align: center;
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.cert-badge-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.cert-badge-img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    margin-bottom: 10px;
    border: 3px solid #667eea;
}

.cert-links {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.cert-links a {
    color: #0366d6;
    text-decoration: none;
    font-size: 0.8em;
    padding: 5px 10px;
    border: 1px solid #0366d6;
    border-radius: 15px;
    transition: all 0.3s ease;
}

.cert-links a:hover {
    background: #0366d6;
    color: white;
}

.certifications-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 30px 0;
}
```

## 📝 **Sección Actualizada para el CV HTML**

```html
<!-- CERTIFICATIONS WITH BADGES -->
<div class="section">
    <h2 class="section-title"><span class="emoji">🏆</span>CERTIFICACIONES PROFESIONALES</h2>
    
    <div class="certifications-grid">
        <div class="cert-badge-container">
            <img src="https://images.credly.com/size/340x340/images/ec81134d-e80b-4eb5-ae07-0eb8e1a60fcd/ec-council-ceh-v12.png" alt="CEH Badge" class="cert-badge-img">
            <h4>CEH - Certified Ethical Hacker</h4>
            <div class="cert-links">
                <a href="[TU_ENLACE_CREDLY_CEH]" target="_blank">🏅 Ver en Credly</a>
                <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/" target="_blank">💼 Ver en LinkedIn</a>
            </div>
        </div>

        <div class="cert-badge-container">
            <img src="https://images.credly.com/size/340x340/images/683783d8-eaac-4c37-a14d-11bd8a6e9555/ccna_600.png" alt="CCNA Badge" class="cert-badge-img">
            <h4>CCNA - Cisco Network Associate</h4>
            <div class="cert-links">
                <a href="[TU_ENLACE_CREDLY_CCNA]" target="_blank">🏅 Ver en Credly</a>
                <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/" target="_blank">💼 Ver en LinkedIn</a>
            </div>
        </div>

        <div class="cert-badge-container">
            <img src="https://images.credly.com/size/340x340/images/be8fcaeb-c769-4858-b567-ffaaa73ce8cf/image.png" alt="Azure Badge" class="cert-badge-img">
            <h4>Azure AZ-900 Fundamentals</h4>
            <div class="cert-links">
                <a href="[TU_ENLACE_CREDLY_AZURE]" target="_blank">🏅 Ver en Credly</a>
                <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/" target="_blank">💼 Ver en LinkedIn</a>
            </div>
        </div>

        <div class="cert-badge-container">
            <img src="https://images.credly.com/size/340x340/images/00634f82-b07f-4bbd-a6bb-53de397fc3a6/image.png" alt="AWS Badge" class="cert-badge-img">
            <h4>AWS Cloud Practitioner</h4>
            <div class="cert-links">
                <a href="[TU_ENLACE_CREDLY_AWS]" target="_blank">🏅 Ver en Credly</a>
                <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/" target="_blank">💼 Ver en LinkedIn</a>
            </div>
        </div>

        <div class="cert-badge-container">
            <img src="https://images.credly.com/size/340x340/images/f8c5b2b7-7e62-46a0-b906-8dc59ef68418/ISA_62443_Digital_Badge.png" alt="ISA Badge" class="cert-badge-img">
            <h4>ISA/IEC 62443 Industrial Security</h4>
            <div class="cert-links">
                <a href="[TU_ENLACE_CREDLY_ISA]" target="_blank">🏅 Ver en Credly</a>
                <a href="https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/" target="_blank">💼 Ver en LinkedIn</a>
            </div>
        </div>
    </div>
</div>
```

## 📋 **Información Necesaria de Tu Parte**

Para completar la implementación, necesito que me proporciones:

1. **Enlaces de Credly específicos** para cada certificación:
   - CEH Credly URL
   - CCNA Credly URL  
   - Azure AZ-900 Credly URL
   - AWS Cloud Practitioner Credly URL
   - ISA/IEC 62443 Credly URL

2. **Confirmación del LinkedIn correcto**: ✅ Ya actualizado a `https://www.linkedin.com/in/mart%C3%ADn-iribarne-swtf/`

## 🚀 **Próximos Pasos**

1. **Proporciona los enlaces de Credly**
2. **Implementaré los badges en el CV HTML**
3. **Actualizaré el CV Markdown también**
4. **Verificaré que todos los enlaces funcionen**

Con los badges de certificaciones, tu CV tendrá un aspecto mucho más profesional y verificable, mostrando visualmente tus credenciales técnicas.