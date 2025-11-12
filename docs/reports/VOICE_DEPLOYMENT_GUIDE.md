# 🎤 Guía de Despliegue: Reconocimiento de Voz

## ✅ Estado Actual

El reconocimiento de voz **YA está implementado** en el frontend y funciona en:

- ✅ Localhost (desarrollo)
- ❌ Producción HTTP (requiere HTTPS)

## 🔒 Requisitos para Producción

### 1. **HTTPS Obligatorio**

El Web Speech API **solo funciona en contextos seguros**:

- ✅ `https://tudominio.com`
- ✅ `http://localhost:*` (desarrollo)
- ❌ `http://tudominio.com` (producción HTTP)

### 2. **Navegadores Compatibles**

- ✅ Chrome/Chromium (mejor soporte)
- ✅ Microsoft Edge
- ✅ Safari (macOS/iOS)
- ❌ Firefox (soporte limitado)

### 3. **Permisos del Navegador**

El usuario debe **autorizar el acceso al micrófono** cuando se le solicite.

---

## 🚀 Pasos para Habilitar en Producción

### **Opción A: Desplegar con HTTPS (Recomendado)**

#### 1. **Obtener un Certificado SSL**

**Opción Gratuita - Let's Encrypt (Recomendado):**

```bash
# En tu servidor (Nginx/Apache)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com
```

**Opción Paga - Certificado Comercial:**

- Comprar en: Namecheap, GoDaddy, Cloudflare, etc.
- Instalar en tu servidor web

#### 2. **Configurar Nginx para HTTPS**

```nginx
server {
    listen 443 ssl http2;
    server_name tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5173;  # Frontend Vite
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tudominio.com;
    return 301 https://$host$request_uri;
}
```

#### 3. **Verificar SSL**

```bash
# Probar que SSL funciona
curl -I https://tudominio.com

# Debería devolver 200 OK
```

---

### **Opción B: Usar Plataformas con HTTPS Automático**

#### **Vercel (Recomendado para Frontend)**

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desde ss_frontend/
cd ss_frontend
vercel

# ✅ Vercel automáticamente proporciona HTTPS
```

#### **Netlify (Alternativa)**

```bash
# Instalar Netlify CLI
npm i -g netlify-cli

# Desde ss_frontend/
cd ss_frontend
netlify deploy --prod

# ✅ Netlify automáticamente proporciona HTTPS
```

#### **Railway/Render/Heroku**

Todas estas plataformas proporcionan HTTPS automático al desplegar.

---

### **Opción C: Túnel HTTPS para Testing (No Producción)**

Para **probar rápidamente** sin configurar SSL:

```bash
# Instalar ngrok (Windows)
choco install ngrok

# O descargar de https://ngrok.com/download

# Desde ss_frontend/ con Vite corriendo
ngrok http 5173

# Te dará una URL HTTPS temporal:
# https://abc123.ngrok.io -> funciona con voz
```

⚠️ **Nota**: Esta opción es solo para testing, no para producción.

---

## 🧪 Verificar que Funciona

### 1. **Abrir en HTTPS**

```
https://tudominio.com/reports
```

### 2. **Hacer Clic en el Botón de Voz**

- Debe solicitar permisos del micrófono
- El botón cambia a rojo "Escuchando..."

### 3. **Hablar Claramente**

```
"Reporte de ventas del año 2025 en Excel"
```

### 4. **Verificar Transcripción**

El prompt debe aparecer en el input automáticamente.

---

## 🐛 Solución de Problemas

### **"Navegador no soporta voz"**

```
❌ Problema: Firefox no soporta Web Speech API
✅ Solución: Usar Chrome, Edge o Safari
```

### **"El reconocimiento de voz requiere HTTPS"**

```
❌ Problema: Accediendo por HTTP en producción
✅ Solución: Configurar SSL o usar plataforma con HTTPS
```

### **"Por favor permite el acceso al micrófono"**

```
❌ Problema: Usuario denegó permisos
✅ Solución: En Chrome -> Configuración -> Privacidad -> Permisos del sitio -> Micrófono
```

### **"No se detectó ningún audio"**

```
❌ Problema: Micrófono no está funcionando
✅ Solución:
   1. Verificar que el micrófono esté conectado
   2. Probar en https://www.onlinemictest.com/
   3. Hablar más fuerte/cerca del micrófono
```

---

## 📱 Soporte Móvil

### **iOS (Safari)**

- ✅ Funciona bien con HTTPS
- ⚠️ Requiere interacción del usuario (no auto-play)

### **Android (Chrome)**

- ✅ Funciona perfectamente con HTTPS
- ⚠️ Necesita permisos del sistema

---

## 🎯 Checklist de Despliegue

- [ ] Frontend desplegado en HTTPS
- [ ] SSL configurado correctamente
- [ ] Navegador compatible (Chrome/Edge/Safari)
- [ ] Permisos de micrófono habilitados
- [ ] Probado en múltiples dispositivos
- [ ] Error handling implementado (✅ ya implementado)
- [ ] UI muestra estado de "Escuchando..." (✅ ya implementado)

---

## 📝 Código Ya Implementado

El código de reconocimiento de voz **ya está completamente implementado** en:

**`ReportPromptInput.tsx`** (líneas 24-113):

```typescript
const handleVoiceInput = () => {
  const SpeechRecognition =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;

  if (!SpeechRecognition) {
    setVoiceError("Tu navegador no soporta reconocimiento de voz...");
    return;
  }

  if (!window.isSecureContext) {
    setVoiceError("El reconocimiento de voz requiere HTTPS o localhost.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "es-ES";
  recognition.start();
  // ... resto del código
};
```

---

## 🎉 Resumen

Para habilitar voz en producción:

1. **Desplegar con HTTPS** (Let's Encrypt, Vercel, Netlify, etc.)
2. **Acceder a la app via `https://`**
3. **Usar Chrome, Edge o Safari**
4. **Permitir acceso al micrófono cuando se solicite**

¡El código ya está listo, solo falta HTTPS! 🚀
