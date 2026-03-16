# FMweb-K-Quantum

Plataforma unificada para simulaciones cuánticas, machine learning y gestión de trabajos utilizando Qiskit y Cirq.

## Requisitos Previos

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) y npm
- [Docker](https://www.docker.com/) (si se requieren los servicios dockerizados)

## Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd Scandia05-ML-FMweb-K-Quantum
```

---

## Configuración e Instalación del Backend (Python)

El backend en base a Flask maneja la integración con APIs y los procesos de Qiskit y Cirq.

1. **Navegar al directorio del Backend:**
   ```bash
   cd Backend
   ```

2. **Crear un entorno virtual (recomendado):**
   ```bash
   python -m venv .venv
   ```

3. **Activar el entorno virtual:**
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source .venv/bin/activate
     ```

4. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar las variables de entorno:**
   - Copiar el archivo de ejemplo `.env.example` a `.env`:
     ```bash
     cp .env.example .env
     ```
   - Editar el archivo `.env` para agregar las credenciales necesarias (como `IBM_QUANTUM_TOKEN`, `GEMINI_API_KEY`, etc.).

6. **Ejecutar el servidor del Backend:**
   ```bash
   python main.py
   ```
   > El backend estará corriendo por defecto en `http://localhost:5000` (o el puerto configurado).

---

## Configuración e Instalación del Frontend (React + Vite)

El frontend está construido usando React y Vite.

1. **Abrir una nueva terminal** (manteniendo el backend corriendo).

2. **Navegar al directorio del Frontend:**
   ```bash
   cd Frontend
   ```

3. **Instalar las dependencias de Node:**
   ```bash
   npm install
   ```

4. **Iniciar el servidor de desarrollo:**
   ```bash
   npm run dev
   ```
   > El frontend de desarrollo se abrirá típicamente en `http://localhost:5173`. Visita esa URL en tu navegador para ver la aplicación.
